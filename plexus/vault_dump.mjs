import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const V = require(join(here, "vault.js"));

const out = {};
const t0 = Date.now();
const { vault, recoveryCode } = await V.create("correct horse battery staple");
out.setupMs = Date.now() - t0;
out.recoveryCode = recoveryCode;
out.codeEntropyBits = V.RECOVERY_BITS;
out.iterations = V.ITERATIONS;
out.wraps = Object.keys(vault.wraps);

// data goes in under the password
let o = await V.open(vault, "correct horse battery staple");
out.openedWith = o.usedWay;
await V.put(vault, o.dek, "water bill", { amount: 42150, meter: "A-77" });
out.recordNames = Object.keys(vault.records);
out.ciphertextLooksNothingLikeInput =
  !JSON.stringify(vault.records).includes("42150") &&
  !JSON.stringify(vault.records).includes("A-77");

// the forgotten-password path: the recovery code opens the SAME data
const o2 = await V.open(vault, recoveryCode);
out.recoveredWith = o2.usedWay;
out.recoveredValue = await V.get(vault, o2.dek, "water bill");

// a lowercase, space-mangled code must still work
const o3 = await V.open(vault, recoveryCode.toLowerCase().replace(/-/g, " "));
out.sloppyCodeWorks = o3.usedWay === "recovery";

// wrong secrets open nothing
out.wrongPassword = await V.open(vault, "hunter2").then(() => "OPENED", e => e.message);

// changing the password must not touch a single record
const before = JSON.stringify(vault.records);
await V.changePassword(vault, o.dek, "a new master password");
out.recordsUntouchedByPasswordChange = before === JSON.stringify(vault.records);
out.oldPasswordNowFails = await V.open(vault, "correct horse battery staple")
  .then(r => r.usedWay, () => "rejected");
const o4 = await V.open(vault, "a new master password");
out.newPasswordValue = await V.get(vault, o4.dek, "water bill");
out.recoveryStillWorksAfterChange = (await V.open(vault, recoveryCode)).usedWay;

// blast radius, measured by the same engine
out.twoWays = V.blastRadius(vault);
const single = JSON.parse(JSON.stringify(vault));
delete single.wraps.recovery;
out.oneWay = V.blastRadius(single);

process.stdout.write(JSON.stringify(out));
