/* substratelib.js -- two pictures of the same thing. DATA ONLY, no arithmetic.
 * ===========================================================================
 * Audited by metaphor.js, the same instrument used on MetaphorOS's pictures and
 * on this stack's own. Kept in a SEPARATE file from metaphorlib.js on purpose:
 * that library's counts were pre-registered and locked at twelve entries, and
 * adding to it afterwards would quietly move a number somebody had committed to.
 *
 * ONE OF THESE WAS WRITTEN AFTER THE ANSWER WAS KNOWN, AND SAYS SO.
 * The bedrock/sand picture is the claim as received. The pier picture is a rival
 * written knowing what happened in March 2023, so it is not a prediction about
 * that event and is not offered as one. Both are marked in `where`, and a test
 * asserts the second carries the admission.
 */
(function (root) {
  "use strict";

  var METAPHORS = [

    {
      id: "bedrock-and-sand",
      name: "A bridge on bedrock, and a bridge on liquefiable sand",
      says: "Money fully backed by reserved assets rests on bedrock. Money made " +
            "by lending or by unbacked expansion rests on sand, and when the " +
            "earthquake comes the sand liquefies.",
      where: "the claim as received, before any of it was checked",
      predicts: [
        { says: "Under a common shock, fully reserved settlement assets fall " +
                "less far from par than fractional or algorithmic ones.",
          presenterControls: false },
        { says: "Fully reserved assets return to par faster than fractional or " +
                "algorithmic ones.",
          presenterControls: false },
        { says: "Fractional and algorithmic assets fail discontinuously -- a " +
                "cliff -- rather than deforming and recovering.",
          presenterControls: false },
      ],
    },

    {
      id: "one-pier-on-bedrock",
      name: "One pier sunk into bedrock, and several piers sunk into bedrock",
      says: "Full backing says what the reserve IS. It says nothing about how " +
            "many independent places it is held. A pier on bedrock is still one " +
            "pier, and a bridge on one pier falls when that pier does.",
      where: "written AFTER March 2023 was known, as a rival to the picture " +
             "above rather than a prediction about that event. It has never been " +
             "tested against a shock nobody had seen",
      predicts: [
        { says: "Among fully reserved assets only, the further the reserve is " +
                "concentrated in one custodian, the further from par it falls.",
          presenterControls: false },
        { says: "A fully reserved asset whose custodian fails behaves like an " +
                "unbacked one for the duration of that failure, however complete " +
                "the backing.",
          presenterControls: false },
      ],
    },

  ];

  var API = { metaphors: METAPHORS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.SUBSTRATELIB = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
