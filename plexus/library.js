/* library.js -- the seed structures. DATA ONLY: no arithmetic lives in here.
 * ===========================================================================
 * WHERE THESE CAME FROM, AND WHERE THEY DID NOT
 * The task was to find real problems in open-source projects and turn them into
 * a library of shapes. Two limits applied and neither was worked around:
 *
 *   - this session's GitHub access is scoped to two repositories, so
 *     repository-wide and global code search were out of scope and unused;
 *   - no paid API, no keys, no scraping.
 *
 * So nothing here was mined. Every entry is one of two things and says which:
 *
 *   measured-here  a defect found and measured inside this repository, with
 *                  the file named, so the claim can be checked by reading it
 *   cited          a documented, independently checkable property of a
 *                  well-known open-source mechanism -- caches.addAll being
 *                  atomic, script-src forbidding external sources, a package
 *                  registry being one host
 *
 * validate() refuses an entry with neither label. That rule is the epistemic
 * firewall applied to the commons itself: a structure taken from a real problem
 * and a structure somebody imagined must never sit in the same shape without a
 * word separating them, because after a hundred entries nobody will remember
 * which was which.
 *
 * WHAT A GOOD ENTRY LOOKS LIKE
 * Not a fragile thing with a bad number. A gap: the drawing people already
 * carry, next to the dependencies actually there. If drawn and actual measure
 * the same, the entry teaches nothing and should not be in the library -- there
 * is no blind spot to hand anybody.
 *
 * THE ONE ENTRY THAT MEASURES ZERO, AND WHY IT STAYS
 * two-ways-into-the-vault has a blind spot of exactly 0.000: everybody already
 * knows a password is a single point. It is kept because its RELIEF is 0.750,
 * and an entry whose value is entirely in the remedy is a different and
 * perfectly good kind of entry. Deleting it to make the average look better
 * would be tuning the library after seeing the numbers.
 */
(function (root) {
  "use strict";

  var CC0 = "CC0-1.0";

  /* Many things, one hub: n workers, each doing part of the job, all of them
     the same one thing underneath. The shape that appeared four separate times
     while this repository was being built, which is why it is parameterised
     rather than typed out three times. */
  function hub(hubName, workers, conclusion, secondHub) {
    var parts = [hubName].concat(workers, [conclusion]);
    var links = [];
    workers.forEach(function (w) { links.push([hubName, w, 1.0]); });
    workers.forEach(function (w) { links.push([w, conclusion, 1.0]); });
    var out = {
      drawn: { parts: parts, links: links, sources: workers.slice(), conclusion: conclusion },
      actual: { parts: parts, links: links, sources: [hubName], conclusion: conclusion },
    };
    if (secondHub) {
      var p2 = parts.concat([secondHub]);
      var l2 = links.slice();
      workers.forEach(function (w) { l2.push([secondHub, w, 1.0]); });
      out.remedy = { parts: p2, links: l2, sources: [hubName, secondHub], conclusion: conclusion };
    }
    return out;
  }

  function numbered(prefix, n) {
    var out = [], i;
    for (i = 1; i <= n; i++) out.push(prefix + " " + i);
    return out;
  }

  /* ------------------------------------------------------- the entries ---- */
  var ENTRIES = [];

  ENTRIES.push(Object.assign({
    id: "sole-maintainer",
    title: "One person, three jobs",
    problem:
      "A widely used package lists review, release signing and security response as three " +
      "separate processes. Three processes sounds like three ways the project keeps working. " +
      "One person does all three, and when they stop, all three stop at once.",
    provenance: {
      kind: "cited",
      where: "the standard single-maintainer failure in open-source projects; the shape is " +
             "checkable against any repository by asking who can merge, who holds the signing " +
             "key and who answers a security report",
      licence: CC0,
    },
    note: "The remedy is not more process. It is a second person attached to the same three jobs.",
  }, hub("The maintainer",
         ["Review", "Release signing", "Security response"],
         "The project ships",
         "A second maintainer")));

  ENTRIES.push(Object.assign({
    id: "three-audits-one-threat-model",
    title: "Three audits, one threat model",
    problem:
      "A system is signed off by three independent auditors. All three worked from the same " +
      "threat model, so all three are blind to the same thing, and three signatures read as " +
      "three chances to catch it when they are one.",
    provenance: {
      kind: "cited",
      where: "the standard correlated-assurance failure in security review; the shape is " +
             "checkable by asking each auditor which document scoped their work",
      licence: CC0,
    },
    note: "Identical arithmetic to sole-maintainer with no word in common. That is the test.",
  }, hub("The threat model",
         ["Audit A", "Audit B", "Audit C"],
         "The system is secure",
         "A second threat model")));

  ENTRIES.push(Object.assign({
    id: "inline-only-under-csp",
    title: "Three script files, one policy directive",
    problem:
      "A page loads three scripts and works. Its Content-Security-Policy has script-src " +
      "'unsafe-inline' and no 'self'. That permits inline script and FORBIDS <script src>, so " +
      "all three fail together and the page renders blank with nothing in the console that " +
      "names the cause. Three files, one directive.",
    provenance: {
      kind: "measured-here",
      where: "plexus/build.py and plexus/test_manifold.py, which asserts no shipped page " +
             "carries a script with a src attribute; this repository shipped a blank page " +
             "for exactly this reason",
      licence: CC0,
    },
    note: "The remedy shown is the one this repository took: inline the code, so its presence " +
          "no longer routes through the policy at all.",
  }, hub("The policy directive",
         ["engines.js", "eti.js", "vault.js"],
         "The app runs",
         "The code is inlined into the page")));

  ENTRIES.push({
    id: "atomic-install-list",
    title: "Twelve assets, all or nothing",
    problem:
      "A service worker calls caches.addAll with twelve URLs. addAll is atomic: one 404 " +
      "rejects the whole promise, install fails, the worker never activates and the app is " +
      "not installable -- with no error at the asset that was missing. The list looks like " +
      "twelve independent fetches and behaves like a chain of twelve.",
    provenance: {
      kind: "cited",
      where: "the Service Worker specification: caches.addAll rejects if any request fails. " +
             "Checkable by removing one file from any addAll list and watching install fail",
      licence: CC0,
    },
    note:
      "This is the entry that shows a limit of the engine rather than of the world. FATHOM's " +
      "sources are disjunctive -- more of them always means less rests on each. A conjunction " +
      "has no operator here and has to be drawn as a chain. The star anybody would draw is " +
      "wrong, and the engine cannot tell them so.",
    drawn: {
      parts: ["The app installs"].concat(numbered("Asset", 12)),
      links: numbered("Asset", 12).map(function (a) { return [a, "The app installs", 1.0]; }),
      sources: numbered("Asset", 12),
      conclusion: "The app installs",
    },
    actual: (function () {
      var a = numbered("Asset", 12);
      var links = [["The app installs", a[11], 1.0]], i;
      for (i = 11; i > 0; i--) links.push([a[i], a[i - 1], 1.0]);
      return { parts: ["The app installs"].concat(a), links: links,
               sources: [a[0]], conclusion: "The app installs" };
    })(),
    remedy: {
      parts: ["The app installs"].concat(numbered("Asset", 12)),
      links: numbered("Asset", 12).map(function (a) { return [a, "The app installs", 1.0]; }),
      sources: numbered("Asset", 12),
      conclusion: "The app installs",
    },
  });

  ENTRIES.push({
    id: "two-ways-into-the-vault",
    title: "A password is one way in",
    problem:
      "Encrypting records under a key derived from a master password gives exactly one way in. " +
      "Forgetting the password destroys the data, and changing it means re-encrypting every " +
      "record. Both faults are the same fault.",
    provenance: {
      kind: "measured-here",
      where: "plexus/vault.js and plexus/test_vault.py, where 1.000 and 0.250 are asserted " +
             "against the shipped implementation",
      licence: CC0,
    },
    note:
      "Blind spot 0.000 on purpose: nobody is surprised that a password is a single point. " +
      "The value of this entry is the remedy, and 0.250 rather than 0.500 because contracting " +
      "two ways in puts two conductances in parallel.",
    drawn: {
      parts: ["The data", "The key", "The password"],
      links: [["The key", "The data", 1.0], ["The password", "The key", 1.0]],
      sources: ["The password"], conclusion: "The data",
    },
    actual: {
      parts: ["The data", "The key", "The password"],
      links: [["The key", "The data", 1.0], ["The password", "The key", 1.0]],
      sources: ["The password"], conclusion: "The data",
    },
    remedy: {
      parts: ["The data", "The key", "The password", "The recovery code"],
      links: [["The key", "The data", 1.0], ["The password", "The key", 1.0],
              ["The recovery code", "The key", 1.0]],
      sources: ["The password", "The recovery code"], conclusion: "The data",
    },
  });

  ENTRIES.push({
    id: "benchmark-contamination",
    title: "Two evaluations, one corpus",
    problem:
      "A model scores well on two benchmarks and the two results are reported as independent " +
      "evidence that it generalises. Both benchmarks were built from the same public crawl the " +
      "model was trained on. Two results, one origin, and the second one adds almost nothing.",
    provenance: {
      kind: "cited",
      where: "benchmark contamination in publicly released models; checkable from a model " +
             "card by comparing the training corpus against the provenance of each eval set",
      licence: CC0,
    },
    note: "The same shape as three-audits-one-threat-model at n = 2 rather than n = 3.",
    drawn: {
      parts: ["Eval A", "Eval B", "The model generalises"],
      links: [["Eval A", "The model generalises", 1.0], ["Eval B", "The model generalises", 1.0]],
      sources: ["Eval A", "Eval B"], conclusion: "The model generalises",
    },
    actual: {
      parts: ["The shared corpus", "Eval A", "Eval B", "The model generalises"],
      links: [["The shared corpus", "Eval A", 1.0], ["The shared corpus", "Eval B", 1.0],
              ["Eval A", "The model generalises", 1.0], ["Eval B", "The model generalises", 1.0]],
      sources: ["The shared corpus"], conclusion: "The model generalises",
    },
    remedy: {
      parts: ["Corpus A", "Corpus B", "Eval A", "Eval B", "The model generalises"],
      links: [["Corpus A", "Eval A", 1.0], ["Corpus B", "Eval B", 1.0],
              ["Eval A", "The model generalises", 1.0], ["Eval B", "The model generalises", 1.0]],
      sources: ["Corpus A", "Corpus B"], conclusion: "The model generalises",
    },
  });

  ENTRIES.push(Object.assign({
    id: "one-mirror-many-packages",
    title: "Forty packages, one registry",
    problem:
      "A build pulls forty packages from forty different projects with forty different " +
      "maintainers. Every one of them arrives from a single registry. Forty independent " +
      "dependencies read as very little resting on any one of them, and the number is right " +
      "about the packages and silent about the registry.",
    provenance: {
      kind: "cited",
      where: "the single-registry dependency of ordinary package installs; checkable from any " +
             "lockfile by reading the resolved host of every entry",
      licence: CC0,
    },
    note: "The largest blind spot in the library, and it grows with the number of dependencies: " +
          "the more independent things you list, the more reassuring the number and the wider " +
          "the gap.",
  }, hub("The registry", numbered("Package", 40), "The build succeeds", "A second registry")));

  ENTRIES.push(Object.assign({
    id: "model-weights-one-host",
    title: "Six models, one hub",
    problem:
      "An application loads six models from six different authors under six different licences " +
      "and treats that as six independent components. All six are fetched from one hub at " +
      "start-up, so the hub being unreachable, rate-limiting, or removing a repository takes " +
      "all six at once.",
    provenance: {
      kind: "cited",
      where: "the single-host dependency of model downloads at run time; checkable by reading " +
             "the resolved host of every weights fetch in an application's start-up path",
      licence: CC0,
    },
    note: "Same shape as sole-maintainer at n = 6. Caching the weights on device is the remedy " +
          "the shape actually points at: a second route to each model, not a second hub.",
  }, hub("The hub", numbered("Model", 6), "The app answers", "A local cache of the weights")));

  var API = { entries: ENTRIES, hub: hub, numbered: numbered, LICENCE: CC0 };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.LIBRARY = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
