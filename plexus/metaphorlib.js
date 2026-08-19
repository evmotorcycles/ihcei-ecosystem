/* metaphorlib.js -- the metaphors audited. DATA ONLY: no arithmetic in here.
 * ===========================================================================
 * OUR OWN ARE IN THE SAME TABLE, ON PURPOSE
 * An audit that puts somebody else's pictures under a standard and its own in a
 * section headed "why ours are different" is not an audit. Everything this
 * stack ships is in this list, judged by the same rule, and a test asserts that
 * every one of ours comes out a lens. If one does not, the honest response is
 * to give it a real prediction or stop calling it a lens -- not to soften the
 * rule.
 *
 * EVERY PREDICTION LIST IS HAND-WRITTEN
 * These are a reading. The arithmetic over them is not. Anyone who thinks a
 * prediction has been missed can add it and the class will change, which is the
 * only honest way to publish a judgement about somebody else's design.
 *
 * `presenterControls` IS THE WHOLE QUESTION
 * Not "is this true" and not "is this good". Only: if this came back false,
 * could the people showing you the picture fix it by changing their own work?
 * Newton could not have rescued corpuscles by editing anything but the theory.
 * A vendor whose pipe does not widen throughput can ship a patch on Tuesday.
 */
(function (root) {
  "use strict";

  var METAPHORS = [

    /* ------------------------------------------------- the ones that worked -- */
    {
      id: "corpuscles",
      name: "Light as tiny billiard balls",
      says: "A beam is a stream of small hard particles, so it bounces and " +
            "swerves the way thrown things do.",
      where: "Newton's optics, and the two experiments that later contradicted it",
      killed: true,
      killedBy: "Light was measured travelling SLOWER in water, not faster, and " +
                "light does bend round a sharp edge. Both predictions came back " +
                "false and the picture went with them.",
      predicts: [
        { says: "The angle a beam leaves a mirror equals the angle it arrived at.",
          presenterControls: false },
        { says: "Light entering glass or water bends toward the normal because it " +
                "speeds UP in the denser material.",
          presenterControls: false },
        { says: "Light passing a sharp edge casts a perfectly sharp shadow and " +
                "does not bend around it.",
          presenterControls: false },
      ],
    },

    {
      id: "falling-lift",
      name: "A person in a windowless falling lift",
      says: "Standing in gravity and accelerating through empty space feel the " +
            "same from inside the box.",
      where: "Einstein's equivalence thought experiment, and the eclipse " +
             "measurements that followed",
      predicts: [
        { says: "No experiment performed inside the sealed box can tell falling " +
                "from floating.",
          presenterControls: false },
        { says: "A beam crossing the box travels a bent path seen from outside, " +
                "so starlight grazing the sun is deflected by a specific amount.",
          presenterControls: false },
      ],
    },

    /* ----------------------------------------------------- what this ships -- */
    {
      id: "sole-route",
      name: "A step with no way round it",
      says: "Some steps are the only path through; take one away and what was " +
            "one thing becomes two things that cannot reach each other.",
      where: "plexus/engines.js, and any structure a person enters themselves",
      predicts: [
        { says: "Remove the step it marked and the structure really does separate " +
                "into pieces that cannot reach each other.",
          presenterControls: false },
        { says: "The numbers across every step add up to the parts minus the " +
                "pieces, exactly.",
          presenterControls: true },
      ],
    },

    {
      id: "handles",
      name: "Handles on a claim",
      says: "A claim you can grip has a named source, a figure, a method, a date " +
            "and a scope; one you cannot grip has none of them.",
      where: "cairn/ei_engine.js and plexus/press.js",
      predicts: [
        { says: "Go to the thing it named and it will exist, and it will say this.",
          presenterControls: false },
      ],
    },

    {
      id: "what-the-bill-should-be",
      name: "Working the bill out again from its parts",
      says: "A bill is its parts put together in one particular way, so you can " +
            "do it again yourself and compare.",
      where: "plexus/packlib.js, against any bill a person is holding",
      predicts: [
        { says: "Recompute from the printed inputs and you get the printed total.",
          presenterControls: false },
      ],
    },

    /* ------------------------------------- the ones from the MetaphorOS brief */
    {
      id: "wider-pipe",
      name: "A wider pipe means more bandwidth",
      says: "Data is water, a connection is piping, and dragging the pipe wider " +
            "gives the connection more room.",
      where: "the MetaphorOS brief, Flow Engine",
      predicts: [
        { says: "Drag the pipe wider and throughput actually rises.",
          presenterControls: true },
      ],
    },

    {
      id: "scale-slider",
      name: "Stretch the boundary to serve a million people",
      says: "Zooming out or stretching the edge of the map tells the system to " +
            "allocate more machines, so nobody has to think about servers.",
      where: "the MetaphorOS brief, Scale Slider",
      predicts: [
        { says: "Stretch it and the application really does serve the larger " +
                "number without falling over.",
          presenterControls: true },
      ],
    },

    {
      id: "snapping-bricks",
      name: "Snapping two bricks together",
      says: "Clicking two shapes into each other writes the integration between " +
            "two applications.",
      where: "the MetaphorOS brief, Blueprint Engine",
      predicts: [
        { says: "Snap them and the two applications really do exchange what the " +
                "shapes suggest they exchange.",
          presenterControls: true },
      ],
    },

    {
      id: "water-grid-budget",
      name: "Water filling reservoirs, gates opening when full",
      says: "Money is water; a payout is a gate that opens when its reservoir " +
            "reaches the line.",
      where: "the MetaphorOS brief, Metaphor Library",
      predicts: [
        { says: "Fill the reservoir to the line and the payout really is sent.",
          presenterControls: true },
      ],
    },

    /* ------------------------------------------------------- pure covering -- */
    {
      id: "cloud-storage",
      name: "The cloud",
      says: "Your files float safely somewhere above you.",
      where: "consumer storage products generally",
      predicts: [],
    },

    {
      id: "desktop-and-folders",
      name: "A desktop with folders on it",
      says: "Your work sits on a wooden surface in paper wallets you can open.",
      where: "every graphical operating system since the early eighties",
      predicts: [],
    },

    {
      id: "for-you",
      name: "Chosen for you",
      says: "What you are shown was picked with your interests in mind.",
      where: "ranked feeds generally",
      predicts: [],
    },

  ];

  var OURS = ["sole-route", "handles", "what-the-bill-should-be"];

  var API = { metaphors: METAPHORS, OURS: OURS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.METAPHORLIB = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
