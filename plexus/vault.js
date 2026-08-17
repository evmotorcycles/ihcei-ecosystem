/* vault.js -- on-device vault. KERNEL: no interface, no network, ever.
 * ===========================================================================
 * WHY THE PASSWORD IS NOT THE KEY
 * The obvious design derives an AES key from the master password with PBKDF2
 * and encrypts everything under it. It has two faults, and the second one is
 * the answer to "what if they forget it":
 *
 *   1. changing the password means re-encrypting every record;
 *   2. there is exactly ONE way in, so forgetting it destroys the data.
 *
 * So the data is encrypted under a random Data Encryption Key (DEK) that no
 * human ever sees, and the DEK is WRAPPED separately under each way in. A
 * password change rewraps 32 bytes. A forgotten password costs nothing if
 * another wrapping exists.
 *
 * RECOVERY, STATED PLAINLY
 * At setup the vault mints a recovery code with 128 bits of entropy and wraps
 * the same DEK under it. That code is shown ONCE and never stored -- only the
 * wrapping is. Lose the password, the code opens it. Lose both, the data is
 * gone, permanently, and nobody can help: there is no third wrapping, no
 * escrow, and no vendor key. That is not a gap in the design, it is the
 * design. A vault someone else can open when you forget is a vault they can
 * open when you have not forgotten.
 *
 * THE VAULT MEASURES ITS OWN BLAST RADIUS
 * The wrappings form a graph -- the secrets are sources, the DEK is the
 * conclusion -- so the same FATHOM arithmetic that asks "is there another way
 * in" to a claim asks it of the keys. Measured, not guessed -- I wrote 0.500
 * here first and the suite corrected me:
 *
 *     one way in    deepest dependence 1.000   rests on one thread
 *     two ways in   deepest dependence 0.250   does not
 *
 * 0.250 rather than 0.500 because contracting both secrets into one ground
 * puts two unit conductances in parallel: R falls from 2 to 1.5, so support
 * rises from 0.5 to 0.667 and 1 - 0.5/0.667 = 0.25. That is not a security
 * score somebody invented; it is the measurement this project already trusts,
 * pointed at itself.
 *
 * WHAT THIS DOES NOT DEFEND AGAINST
 * A compromised device. If malware reads the page's memory while the vault is
 * unlocked, it has the DEK. Encryption at rest protects a stolen phone, a
 * shared computer, and a backup -- not a machine already owned by someone else.
 */
(function (root) {
  "use strict";

  var C = (root.crypto && root.crypto.subtle) ? root.crypto : null;
  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  /* OWASP's floor for PBKDF2-HMAC-SHA256. Deliberately slow: it is the only
     thing standing between a stolen blob and an offline guessing run. */
  var ITERATIONS = 600000;
  var DEK_BITS = 256, SALT_BYTES = 16, IV_BYTES = 12, RECOVERY_BITS = 128;

  /* Crockford base32: no I, L, O or U, so a handwritten code cannot be
     misread as a different valid code. */
  var ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";

  function bytes(n) { return C.getRandomValues(new Uint8Array(n)); }

  function b64(u8) {
    var s = "", i;
    for (i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i]);
    return root.btoa ? root.btoa(s) : Buffer.from(u8).toString("base64");
  }
  function unb64(str) {
    var s = root.atob ? root.atob(str) : Buffer.from(str, "base64").toString("binary");
    var u8 = new Uint8Array(s.length), i;
    for (i = 0; i < s.length; i++) u8[i] = s.charCodeAt(i);
    return u8;
  }

  function recoveryCode() {
    var raw = bytes(RECOVERY_BITS / 8), out = "", i;
    for (i = 0; i < raw.length; i++) out += ALPHABET[raw[i] & 31] + ALPHABET[raw[i] >> 3 & 31];
    return out.match(/.{1,5}/g).join("-");
  }
  function normalise(code) {
    return String(code || "").toUpperCase().replace(/[^0-9A-Z]/g, "")
      .replace(/I/g, "1").replace(/L/g, "1").replace(/O/g, "0");
  }

  function kek(secret, salt) {
    return C.subtle.importKey("raw", new TextEncoder().encode(secret),
                              "PBKDF2", false, ["deriveKey"])
      .then(function (base) {
        return C.subtle.deriveKey(
          { name: "PBKDF2", salt: salt, iterations: ITERATIONS, hash: "SHA-256" },
          base, { name: "AES-GCM", length: 256 }, false, ["wrapKey", "unwrapKey"]);
      });
  }

  function wrap(dek, secret) {
    var salt = bytes(SALT_BYTES), iv = bytes(IV_BYTES);
    return kek(secret, salt).then(function (k) {
      return C.subtle.wrapKey("raw", dek, k, { name: "AES-GCM", iv: iv });
    }).then(function (buf) {
      return { salt: b64(salt), iv: b64(iv), blob: b64(new Uint8Array(buf)) };
    });
  }

  function unwrap(w, secret) {
    return kek(secret, unb64(w.salt)).then(function (k) {
      return C.subtle.unwrapKey("raw", unb64(w.blob), k,
        { name: "AES-GCM", iv: unb64(w.iv) },
        { name: "AES-GCM", length: DEK_BITS }, true, ["encrypt", "decrypt"]);
    });
  }

  /* create: one DEK, wrapped once per way in. The code is RETURNED, never
     stored -- if it were stored, it would not be a second way in, it would be
     a copy of the first. */
  function create(password) {
    var code = recoveryCode();
    return C.subtle.generateKey({ name: "AES-GCM", length: DEK_BITS }, true,
                                ["encrypt", "decrypt"])
      .then(function (dek) {
        return Promise.all([wrap(dek, password), wrap(dek, normalise(code))])
          .then(function (ws) {
            return { vault: { v: 1, iterations: ITERATIONS,
                              wraps: { password: ws[0], recovery: ws[1] },
                              records: {} },
                     recoveryCode: code };
          });
      });
  }

  function open(vault, secret) {
    var tries = [["password", vault.wraps.password],
                 ["recovery", vault.wraps.recovery]];
    var norm = normalise(secret);
    function next(i) {
      if (i >= tries.length) return Promise.reject(new Error("that does not open it"));
      var name = tries[i][0], w = tries[i][1];
      if (!w) return next(i + 1);
      /* the recovery wrap is keyed on the normalised code, the password on the
         literal string -- try each against its own form */
      return unwrap(w, name === "recovery" ? norm : secret)
        .then(function (dek) { return { dek: dek, usedWay: name }; },
              function () { return next(i + 1); });
    }
    return next(0);
  }

  function put(vault, dek, name, value) {
    var iv = bytes(IV_BYTES);
    return C.subtle.encrypt({ name: "AES-GCM", iv: iv }, dek,
                            new TextEncoder().encode(JSON.stringify(value)))
      .then(function (buf) {
        vault.records[name] = { iv: b64(iv), blob: b64(new Uint8Array(buf)) };
        return vault;
      });
  }

  function get(vault, dek, name) {
    var rec = vault.records[name];
    if (!rec) return Promise.resolve(null);
    return C.subtle.decrypt({ name: "AES-GCM", iv: unb64(rec.iv) }, dek,
                            unb64(rec.blob))
      .then(function (buf) {
        return JSON.parse(new TextDecoder().decode(new Uint8Array(buf)));
      });
  }

  /* Changing the password rewraps the DEK. It does NOT touch a single record,
     which is the whole reason the password is not the key. */
  function changePassword(vault, dek, next) {
    return wrap(dek, next).then(function (w) {
      vault.wraps.password = w;
      return vault;
    });
  }

  /* The vault's own structure, measured by the engine the rest of the app
     uses. Sources are the ways in; the conclusion is the data. */
  function blastRadius(vault) {
    var ways = Object.keys(vault.wraps).filter(function (k) { return !!vault.wraps[k]; });
    if (!ways.length) return { ways: [], deepest: 1, restsOnOneThread: true, bySource: [] };
    var parts = ["The data", "The key"].concat(ways);
    var links = [["The key", "The data", 1]];
    ways.forEach(function (w) { links.push([w, "The key", 1]); });
    var s = ENG.sound(parts, links, ways, "The data");
    return { ways: ways, deepest: s.deepest,
             restsOnOneThread: s.restsOnOneThread, bySource: s.bySource };
  }

  var API = { create: create, open: open, put: put, get: get,
              changePassword: changePassword, blastRadius: blastRadius,
              recoveryCode: recoveryCode, normalise: normalise,
              ITERATIONS: ITERATIONS, RECOVERY_BITS: RECOVERY_BITS,
              available: !!C };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.VAULT = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
