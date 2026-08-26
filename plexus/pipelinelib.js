/* pipelinelib.js -- one claim, two presses. DATA ONLY, no arithmetic here.
 * ===========================================================================
 * The claim: the value is at the point of use, where hundreds of millions of
 * people act on what an assistant told them.
 *
 * TWO PICTURES OF IT, AND THE SECOND ONE THREATENS THE BUSINESS MODEL.
 * Running one press and stopping is how a process fixes its own answer. So the
 * same claim is pressed twice, by two pictures that predict different things
 * about how a check reaches people, and the topology of each is measured rather
 * than argued. The second is the uncomfortable one and it is here for that
 * reason.
 *
 * BOTH ARE CHAINS, NOT STARS, AND THAT IS DELIBERATE.
 * The conditions are conjunctive: people must be using assistants for things
 * that matter before wrong answers cost anything; answers must be costly before
 * a check is worth having; a check must exist before anyone can use it; people
 * must use it before anyone pays. Each really does presuppose the last. Drawing
 * that as a star -- four independent supports -- would understate it exactly as
 * the twelve-asset install did, which is the lesson already recorded in the
 * Shapes library as atomic-install-list.
 */
(function (root) {
  "use strict";

  var PROJECTS = [

    {
      id: "check-at-the-tap",
      invariant: "A judgement is made at the moment an output meets an action, "
                 + "and whoever holds that moment holds the position that matters "
                 + "-- independent of who produced the output.",
      claim: "The value is at the point of use: a check a person can run on what " +
             "an assistant told them, before they act on it.",
      press: {
        id: "test-at-the-tap",
        name: "Testing the water at the tap, not at the reservoir",
        says: "A city drinks from one supply. What makes a glass safe to drink " +
              "is not the purity of the reservoir but a test you can run at the " +
              "tap, where the water is actually poured.",
        where: "the claim as put, pressed into a physical picture",
        predicts: [
          { says: "A test that costs more effort than the drink is worth will " +
                  "not be run, however good it is.",
            presenterControls: false },
          { says: "People will not walk to a testing station. The test has to be " +
                  "where the tap already is.",
            presenterControls: false },
          { says: "Improving the reservoir does not remove the need for the tap " +
                  "test, because the pipe between them is where most trouble " +
                  "enters.",
            presenterControls: false },
        ],
      },
      schema: {
        says: "Value accrues where an output meets an action, not where the " +
              "output is produced. Whoever holds the moment before acting holds " +
              "the position that matters, regardless of who built the model.",
        provesNothing: true,
        fills: {
          terminology: "tap, supply, reservoir, pipe, test strip, a reading",
          roles: "the person pouring; whoever runs the supply; whoever makes the strip",
          dues: "the drinker owes the test; the supplier owes a supply fit to test",
          authorities: "a strip reports on the water in this glass and no other",
          rules: "a reading below the line means do not drink it yet",
          policies: "test at the point of use, not at the source",
          procedures: "fill, dip, wait the stated seconds, read",
          results: "a reading, and whether the glass was drunk",
          domains: "this tap, this glass, now -- not the mains and not tomorrow",
          exceptions: "a strip that has expired, and water hot enough to skew it",
        },
        leaks: [
          "A test strip returns a number in seconds. A check on a claim returns an errand that may take days, so the feedback the carrier promises is not the feedback the target gives.",
          "Water is homogeneous within the glass; a paragraph is not. One sentence can be checkable and the next fog, and the strip has no equivalent of that.",
          "A strip has a manufacturer who can be held to account for a wrong reading. Nobody stands behind a regex.",
        ],
      },
      guidelines: [
        "Count how many seconds the check adds before somebody acts. If it is more than the reading, it will not be run.",
        "Find one person who used it twice without being asked. Once is curiosity.",
        "Ask what they did differently afterwards. If nothing, the check was decoration.",
        "Check whether they could have got the same answer by simply reading it again more carefully.",
      ],
      topology: {
        parts: [
          "People use assistants for things that matter",
          "Some answers are wrong in ways that cost something",
          "A check exists at the moment of use",
          "People use the check",
          "Someone pays for it",
          "The value is at the point of use",
        ],
        links: [
          ["People use assistants for things that matter",
           "Some answers are wrong in ways that cost something", 1.0],
          ["Some answers are wrong in ways that cost something",
           "A check exists at the moment of use", 1.0],
          ["A check exists at the moment of use", "People use the check", 1.0],
          ["People use the check", "Someone pays for it", 1.0],
          ["Someone pays for it", "The value is at the point of use", 1.0],
        ],
        sources: ["People use assistants for things that matter"],
        conclusion: "The value is at the point of use",
      },
      solutions: [
        { build: "A paste page that presses any assistant output on a phone, offline, in one screen.",
          wrongIf: "People paste once and never return. Measured as: fewer than one in five who use it once use it again within thirty days." },
        { build: "Pre-built structures for the ordinary papers people hold, so nobody draws a graph to check a bill.",
          wrongIf: "Buyers do not contribute a structure back. Measured as: fewer than 5% within 60 days of buying." },
      ],
      evidence: {
        status: "not-yet",
        when: "when a pack has shipped to real buyers and sixty days have passed",
        note: "The paste page exists and is tested. Nothing has been sold, so " +
              "the contribution rate is absent rather than low, and every " +
              "adoption number in the solutions above is unmeasured.",
      },
    },

    {
      id: "the-seatbelt-reading",
      invariant: "A judgement is made at the moment an output meets an action, "
                 + "and whoever holds that moment holds the position that matters "
                 + "-- independent of who produced the output.",
      claim: "The value is at the point of use: a check a person can run on what " +
             "an assistant told them, before they act on it.",
      press: {
        id: "the-seatbelt",
        name: "A seatbelt",
        says: "Cheap, always there, unnoticed until the one moment it matters. " +
              "Nobody shops for one. It reached everybody by becoming the " +
              "default fitting in the car, and then by being required.",
        where: "written as a RIVAL to the tap picture, and it is the one that " +
               "threatens the business model rather than supporting it",
        predicts: [
          { says: "A point-of-use safety check reaches everybody only when it is " +
                  "on by default, not when it is offered for sale.",
            presenterControls: false },
          { says: "The people who would buy such a check voluntarily are the ones " +
                  "already careful enough to need it least.",
            presenterControls: false },
        ],
      },
      schema: {
        says: "Adoption at population scale runs through defaults and through " +
              "whoever controls the surface, not through purchase. A tool sold " +
              "one at a time reaches the worried, not the many.",
        provesNothing: true,
        fills: {
          terminology: "belt, buckle, anchor point, pretensioner, the click",
          roles: "the occupant; the fitter; the regulator who required it",
          dues: "the occupant owes the click; the maker owes an anchor that holds",
          authorities: "a belt restrains the person in that seat and nobody else",
          rules: "worn on every journey, however short",
          policies: "fitted as standard, not sold as an option",
          procedures: "sit, draw across, click, tug to check it locked",
          results: "in the ordinary case nothing happens, which is the point",
          domains: "vehicles in motion -- not a stationary car, not a bicycle",
          exceptions: "medical exemptions; a belt cut away after a crash",
        },
        leaks: [
          "A belt costs the wearer nothing per journey once fitted. A check on a claim costs attention every single time, so the adoption argument does not transfer as cleanly as the picture suggests.",
          "A belt's benefit is invisible until a crash. A check on a claim gives something back immediately -- an errand -- so the carrier understates what the target offers.",
          "Seatbelt adoption was driven by law. Nobody can legislate a check on what an assistant said, which is exactly the condition the carrier presupposes and the target lacks.",
        ],
      },
      guidelines: [
        "Ask who could switch this on for a million people without asking any of them, and whether they have any reason to.",
        "Count how many of the people who bought it were already checking things by hand before.",
        "Look for one adoption at scale, anywhere, of a voluntary point-of-use check that was sold rather than defaulted.",
      ],
      topology: {
        parts: [
          "People use assistants for things that matter",
          "Some answers are wrong in ways that cost something",
          "A check exists at the moment of use",
          "The check is on by default",
          "People use the check",
          "Someone pays for it",
          "The value is at the point of use",
        ],
        links: [
          ["People use assistants for things that matter",
           "Some answers are wrong in ways that cost something", 1.0],
          ["Some answers are wrong in ways that cost something",
           "A check exists at the moment of use", 1.0],
          ["A check exists at the moment of use", "The check is on by default", 1.0],
          ["The check is on by default", "People use the check", 1.0],
          ["People use the check", "Someone pays for it", 1.0],
          ["Someone pays for it", "The value is at the point of use", 1.0],
        ],
        sources: ["People use assistants for things that matter"],
        conclusion: "The value is at the point of use",
      },
      solutions: [
        { build: "The engines as a library other people's software calls, wired so the integrator never sends anyone's text anywhere.",
          wrongIf: "No integrator switches it on within twelve months even when it is free." },
        { build: "A build for institutions who already stand between people and consequences -- advice centres, clinics, unions -- where the check is default because the desk uses it.",
          wrongIf: "No institution adopts it, or those that do stop within a year." },
      ],
      evidence: {
        status: "untestable-here",
        missing: "any deployment where the check is on by default rather than " +
                 "chosen. Nothing has shipped, no integrator exists, and no " +
                 "institution has a build. There is no observation to make.",
      },
    },

  ];

  var API = { projects: PROJECTS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.PIPELINELIB = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
