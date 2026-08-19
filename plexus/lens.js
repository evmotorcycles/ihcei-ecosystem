/* lens.js -- the paradigm, as a thing that fails CI. KERNEL: no interface.
 * ===========================================================================
 * A MASK AND A LENS ARE BOTH ABSTRACTIONS. THE DIFFERENCE IS WHAT THEY DO NEXT.
 *
 * "Cloud", "desktop", "folder", "For you" are abstractions that end the enquiry.
 * You are not meant to ask where the file physically is, who ranked the feed, or
 * what was kept. The picture is the destination.
 *
 * "Sole route", "rests on one thread", "no source named" are abstractions that
 * START one. They are deliberately incomplete: each names something a person can
 * then go and check in the world, with their own eyes, outside this software.
 * The picture is a handle.
 *
 * That is the same move Newton made with the cannonball and Einstein with the
 * falling lift. Neither stopped at the picture. The picture existed to get to a
 * measurement, and the measurement was allowed to kill it.
 *
 * WHY THIS FILE IS CODE AND NOT A MANIFESTO
 * A manifesto cannot fail. Every tool in this stack registers three things here:
 *
 *   measures     what it actually computes -- the arithmetic, not the promise
 *   cannot       what it will not tell you, in the words the page must print
 *   goCheck      what a person does NEXT, outside this software, with their own
 *                eyes -- the step that makes the abstraction a lens
 *
 * A tool with no `cannot` is a tool claiming to be an oracle. A tool with no
 * `goCheck` is a tool that expects you to stop at its picture. register()
 * refuses both, with a reason, and test_lens.py asserts every shipped page
 * actually prints its own `cannot`. If a page's promise and its tool's
 * declaration ever drift apart, the build fails in the same commit that did it.
 *
 * WHAT THIS CANNOT DO, WHICH IS THE POINT AND ALSO THE LIMIT
 * It checks that a refusal is PRINTED. It cannot check that a refusal is TRUE,
 * and no test in this repository can. "Lens, not mask" is enforced here at the
 * level of what the software says about itself, which is strictly weaker than a
 * claim about honesty, and should be held at that strength.
 */
(function (root) {
  "use strict";

  var TOOLS = [];
  var byName = {};

  function problems(t) {
    var why = [];
    if (!t || typeof t !== "object") return ["that is not a tool"];
    if (typeof t.name !== "string" || !t.name.trim()) why.push("a tool needs a name");
    if (typeof t.does !== "string" || !t.does.trim()) {
      why.push("a tool must say in one line what it is for");
    }
    if (!Array.isArray(t.measures) || !t.measures.length) {
      why.push(t.name + " does not say what it computes, so nobody can check it");
    }
    if (!Array.isArray(t.cannot) || !t.cannot.length) {
      why.push(t.name + " declares nothing it cannot do, which is what an oracle looks like");
    }
    if (!Array.isArray(t.goCheck) || !t.goCheck.length) {
      why.push(t.name + " gives the reader nowhere to go afterwards, so its picture " +
               "is a destination rather than a handle");
    }
    (t.goCheck || []).forEach(function (g) {
      if (typeof g !== "string" || !g.trim()) why.push(t.name + " has an empty check");
    });
    return why;
  }

  function register(t) {
    var why = problems(t);
    if (why.length) return { ok: false, why: why };
    TOOLS.push(t);
    byName[t.name] = t;
    return { ok: true, why: [] };
  }

  /* ------------------------------------------------------- the register ---- */
  /* Every sentence in `cannot` is load-bearing: test_lens.py requires the
     shipped page for each tool to contain it verbatim. Editing one here without
     editing the page fails the build, which is the only reason any of this is
     worth more than a paragraph in a README. */

  register({
    name: "Plexus",
    page: "index.html",
    does: "Show what a thing is made of and what is holding it up.",
    measures: [
      "effective resistance on the graph you entered, as distance",
      "w x R -- the chance a link is in a random spanning tree",
      "which parts, when removed, break the graph into more pieces",
    ],
    cannot: [
      "It only knows the parts you entered.",
    ],
    goCheck: [
      "Look at the step it called a sole route and ask the person responsible for it what happens when they are away.",
      "Find one part you did not enter and add it, then see whether the answer moves.",
    ],
  });

  register({
    name: "Cairn",
    page: "flint.html",
    does: "Ask what a claim rests on, and separately whether its wording leans on you.",
    measures: [
      "what the claim rests on, from the sources you marked and the joins you drew",
      "separately, lexical marks of pressure in the wording",
    ],
    cannot: [
      "It does not understand what you pasted.",
      "It cannot tell you whether anything is true.",
      "Two sources that secretly share an origin you did not enter will read as independent, and it will be wrong.",
    ],
    goCheck: [
      "Open the source you marked and read the part the claim actually came from.",
      "Check the figure against the original, not against the summary of it.",
      "Ask who the claim is about, and whether that includes you.",
    ],
  });

  register({
    name: "Shapes",
    page: "commons.html",
    does: "Show shapes other people ran into, described two ways.",
    measures: [
      "the same dependence arithmetic, on a contributed structure",
      "the gap between how a thing is usually described and what it rests on",
    ],
    cannot: [
      "A shape that matches your words may not match your situation.",
    ],
    goCheck: [
      "Take the part the shape says everything routes through and confirm, in your own case, that it really does.",
      "Ask who else could do that job if the one thing named stopped.",
    ],
  });

  register({
    name: "Packs",
    page: "packs.html",
    does: "Check a bill, a payslip or a deposit without drawing anything first.",
    measures: [
      "the arithmetic, recomputed from the numbers you typed, against the figure they printed",
      "separately, which steps have no second way round",
    ],
    cannot: [
      "It does not mean the price is fair.",
      "It does not mean the reading is right.",
      "It only means the figure they printed follows from the numbers you typed.",
    ],
    goCheck: [
      "Go and read the meter yourself, now, and see whether it is past the reading they used.",
      "Find the price per unit printed on the bill and check it against the tariff on their website or your contract.",
    ],
  });

  register({
    name: "Press",
    page: "press.html",
    does: "Press a claim and see what runs out — what you could go and check, and which to do first.",
    measures: [
      "how many things in the claim could come back negative",
      "which one, removed, leaves the rest with nothing behind it",
      "how much each single check settles on its own",
    ],
    cannot: [
      "A claim that is completely made up reads exactly like a true one here.",
      "This says how quickly you could find out, not which way it will go.",
      "Nothing here has been checked. Every line above is something for you to go and do.",
    ],
    goCheck: [
      "Open the thing it named first and confirm it exists and says this.",
      "Find the figure in the original, not in the summary of it.",
    ],
  });

  register({
    name: "Lens or mask",
    page: "metaphor.html",
    does: "Ask of a picture what it predicts, and who could make that prediction come true.",
    measures: [
      "how many things the picture puts at risk",
      "how many of those the people showing it to you could not fix by changing their own work",
      "what each single prediction settles on its own",
    ],
    cannot: [
      "This measures pictures, not software.",
      "Every prediction list here was written by a person.",
      "Self-referring is not an accusation of bad faith, and every working demonstration is one.",
    ],
    goCheck: [
      "Take a picture you were shown and write down one thing it predicts that could come back false.",
      "Then ask whether the people who showed it to you could make that come true by changing their own work.",
    ],
  });

  register({
    name: "Agent Gate",
    page: "gate.html",
    does: "Say where an assistant may work in your plan, and where there is no second way round.",
    measures: [
      "which links lie wholly inside the perimeter you set",
      "which links would cross out of it, and what they would reach",
      "which steps have no alternative route, from the same spanning-tree arithmetic",
      "whether your own time-to-fix on flagged problems is rising, against your own history",
    ],
    cannot: [
      "It does not read what the assistant writes.",
      "It cannot tell you an assistant is safe.",
      "With no history it will say so rather than guess.",
    ],
    goCheck: [
      "Take one step it marked as having no alternative and write down, on paper, what you would do if it failed.",
      "Open your own issue tracker and read the three oldest things still open.",
    ],
  });

  /* page: null -- the vault has no interface yet. Naming a page here would
     force that page to print the limits of something nobody can reach from it,
     which is a different kind of dishonesty from the one this file is for. Its
     limits are asserted against vault.js by test_vault.py until it has a
     surface of its own. */
  register({
    name: "The vault",
    page: null,
    does: "Keep what you put in it on this device, under a key nobody else holds.",
    measures: [
      "how many ways in exist, and how much rests on the deepest one",
    ],
    cannot: [
      "Lose both the password and the recovery code and the data is gone permanently.",
      "It does not protect a device somebody else is already inside.",
    ],
    goCheck: [
      "Write the recovery code down somewhere that is not this device, and check tomorrow that you can still read it.",
    ],
  });

  /* --------------------------------------------------------- the readout --- */
  function tools() { return TOOLS.slice(); }
  function get(name) { return byName[name] || null; }

  /* Which sentences a given page is required to print. Used by the suite, and
     by the pages themselves so the wording has exactly one source. */
  function refusalsFor(page) {
    var out = [];
    if (!page) return out;
    TOOLS.forEach(function (t) {
      if (t.page === page) out = out.concat(t.cannot);
    });
    return out;
  }

  function checksFor(page) {
    var out = [];
    TOOLS.forEach(function (t) {
      if (t.page === page) out = out.concat(t.goCheck);
    });
    return out;
  }

  /* The distinction, stated once, where the tests can see it. Not a score and
     not a claim about anybody else's software -- a description of the two ways
     an abstraction can be used, which is what the register is arranged around. */
  var PARADIGM = {
    mask: "An abstraction that ends the enquiry. You are not meant to ask what is underneath.",
    lens: "An abstraction that starts one. It names something you can go and check yourself.",
    test: "After the picture, is there somewhere to go? If not, it was a mask.",
    limit: "This file checks that a refusal is printed. It cannot check that a refusal is true.",
  };

  var API = { register: register, problems: problems, tools: tools, get: get,
              refusalsFor: refusalsFor, checksFor: checksFor, PARADIGM: PARADIGM };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.LENS = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
