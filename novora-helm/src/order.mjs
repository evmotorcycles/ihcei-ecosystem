// order.mjs — the Governance and Reasoning hierarchy, as something that refuses.
// ============================================================================
// TERMINOLOGY-FREE BY CONSTRUCTION. The logic below is carried entirely by
// ordinary English nouns. No term from any tradition's vocabulary appears here
// or in any consumer-facing string, and a test greps for that. The logic is the
// asset; the vocabulary is not, and importing the vocabulary would import a
// readership test the software has no way to pass.
//
// THE HIERARCHY — THREE LAYERS, STRICT SUBSET
//
//     reach  ⊂  order  ⊂  domain
//
//   reach    What instruments actually get to. Weighable, repeatable, and the
//            only layer any software in this repository can measure.
//   order    The working order the measured world runs inside: what things are,
//            who holds what, what is owed, where the boundaries sit, what
//            follows from breaking them. Larger than reach — an obligation is
//            real and no instrument weighs it.
//   domain   Everything there is, whether or not anything reaches it. Larger
//            than order for the same reason order is larger than reach.
//
// WHY THIS IS IN THE SOFTWARE AND NOT IN A README
// The subset relation is not decoration. Two rules this repository already
// enforces are CONSEQUENCES of it, and stating the hierarchy is what makes them
// one rule instead of two coincidences:
//
//   1. An instrument returning nothing is a fact about the instrument's REACH,
//      never about the domain. That is exactly why "nothing to check" is not an
//      error and gets no number at all (test_fog_returns_no_number_at_all).
//      Empty is not false. The hierarchy is the reason.
//
//   2. A reading taken at one layer cannot settle a question that lives at a
//      wider one. Escalation is the error, and `escalation()` below computes it
//      rather than trusting anyone to notice. A regex count over wording is a
//      reading at `reach`; "this person is lying" is a question at `domain`;
//      the gap between them is the whole reason this file exists.
//
// This is a lens by the register's own test: it names something a person goes
// and checks (which layer does this claim live at, and does the reading
// escalate?), and it can come back false — if a reading at `reach` is ever
// shown to settle a `domain` question, the hierarchy was wrong.

export const LAYERS = [
  {
    id: 'reach',
    n: 1,
    name: 'What instruments reach',
    is: 'Weighable, repeatable, countable. Anything a device can put a number on.',
    examples: ['a meter reading', 'a word count', 'how long a fix took', 'a posterior over wording'],
    software: 'HELM measures here and nowhere else.',
  },
  {
    id: 'order',
    n: 2,
    name: 'The working order',
    is: 'What things are, who holds what, what is owed, where the boundaries sit, and what follows from crossing them.',
    examples: ['a permission', 'a debt', 'a role', 'a consequence for breaking a rule'],
    software: 'HELM can check whether an order was WRITTEN DOWN. It cannot check whether it is right.',
  },
  {
    id: 'domain',
    n: 3,
    name: 'The whole domain',
    is: 'Everything there is, reached or not. The layer no instrument exhausts.',
    examples: ['whether a thing is true', 'whether a person meant it', 'what has not been looked at'],
    software: 'HELM measures nothing here and says so.',
  },
];

const RANK = { reach: 1, order: 2, domain: 3 };
export const layer = id => LAYERS.find(l => l.id === id) || null;

// ── the escalation check ─────────────────────────────────────────────────────
// A reading is taken AT one layer and is being used to answer a question that
// LIVES at another. Answering inward is fine and ordinary (a domain question
// narrowed to something measurable is what science is). Answering OUTWARD is
// the error this whole stack is arranged against.
export function escalation({ measuredAt, answers, where }) {
  if (!RANK[measuredAt]) return { ok: false, why: `unknown layer: ${measuredAt}` };
  if (!RANK[answers]) return { ok: false, why: `unknown layer: ${answers}` };
  if (typeof where !== 'string' || !where.trim()) {
    return { ok: false, why: 'every placement carries a `where`: who assigned these layers, and on what' };
  }
  const gap = RANK[answers] - RANK[measuredAt];
  return {
    ok: gap <= 0,
    gap,
    measuredAt, answers, where,
    why: gap <= 0
      ? null
      : `a reading taken at "${layer(measuredAt).name}" is being used to settle a question ` +
        `that lives at "${layer(answers).name}", ${gap} layer${gap > 1 ? 's' : ''} out. ` +
        `The reading is not wrong; the question is bigger than the instrument.`,
  };
}

// ── the six stages: GOVERNANCE sets the order, REASONING works inside it ─────
// Stages 1-4 establish what a thing IS and what rests on what — nothing is
// built and nothing is claimed. Stages 5-6 are where a person can be wrong on
// purpose: propose something, then say what was actually measured.
export const STAGES = [
  { n: 1, band: 'governance', name: 'Invariant',
    asks: 'What survives when every particular of this is changed?',
    refuses: 'Nothing stated. A picture chosen before the invariant is chosen for its decoration.' },
  { n: 2, band: 'governance', name: 'Carrier',
    asks: 'What physical thing is this like?',
    refuses: 'A picture that risks nothing. That is notation, and notation cannot be wrong.' },
  { n: 3, band: 'governance', name: 'Order',
    asks: 'Which of the ten does this actually settle?',
    refuses: 'A blank element. A plan silent on who is owed what has not been thought through, it has been written up.' },
  { n: 4, band: 'governance', name: 'Structure',
    asks: 'What rests on what, and what has no second way round?',
    refuses: 'A number written by hand. Parts and links go in; the reading comes out of the engine.' },
  { n: 5, band: 'reasoning', name: 'Proposal',
    asks: 'What would you build, and what would show it wrong?',
    refuses: 'A proposal with nothing that could falsify it.' },
  { n: 6, band: 'reasoning', name: 'Evidence',
    asks: 'What was actually measured?',
    refuses: 'A claimed result with no locked prediction behind it.' },
];

export const GOVERNANCE = STAGES.filter(s => s.band === 'governance');
export const REASONING = STAGES.filter(s => s.band === 'reasoning');

// The ten elements of stage 3. Terminology-free; these are the things a
// workable order settles, and a plan that leaves one blank has left it blank.
export const TEN = [
  { id: 'terms',        asks: 'Are the words defined, or are two people using one word for two things?' },
  { id: 'roles',        asks: 'Who does what? Named, not implied.' },
  { id: 'dues',         asks: 'What is owed, by whom, to whom, and by when?' },
  { id: 'boundaries',   asks: 'Where does this stop? What is outside it?' },
  { id: 'rules',        asks: 'What must happen, and what must not?' },
  { id: 'standards',    asks: 'How good counts as good enough, in a number someone can read?' },
  { id: 'steps',        asks: 'In what order, and what cannot start before what?' },
  { id: 'consequences', asks: 'What follows when a rule is broken? Stated before it is broken.' },
  { id: 'where',        asks: 'Where does this apply, and where does it not?' },
  { id: 'exceptions',   asks: 'What is deliberately outside the rule, and who decides?' },
];

// ── the standard procedures ──────────────────────────────────────────────────
// Each one is a procedure a person performs, and each one names what it refuses.
// A procedure with no refusal is advice.
export const SOPS = [
  { n: 1, band: 'governance', does: 'State the invariant before choosing any picture for it.',
    refuse: 'A carrier proposed first. Reorder or the picture picks the argument.',
    check: 'Change every particular you can think of. If the statement dies, it was not the invariant.' },
  { n: 2, band: 'governance', does: 'Make the picture predict one thing its own presenter cannot fix by editing their own work.',
    refuse: 'A picture whose every prediction is under the presenter\'s control. That is a demonstration, not an instrument.',
    check: 'Write down one prediction. Then ask who could make it come true by changing their own code.' },
  { n: 3, band: 'governance', does: 'Fill all ten elements, and write down what the carrier leaks.',
    refuse: 'A blank element rendered as a zero. Blank is blank; it makes its row vanish.',
    check: 'Read the ten aloud to someone who was not in the room. Count the ones they cannot answer.' },
  { n: 4, band: 'governance', does: 'Enter the parts and the links. Let the engine produce the reading.',
    refuse: 'Any number typed in by the person who wanted that number.',
    check: 'Add one part nobody entered and see whether the answer moves.' },
  { n: 5, band: 'reasoning', does: 'Propose, and attach what would show the proposal wrong.',
    refuse: 'A proposal that no outcome could embarrass.',
    check: 'Name the result you would least like to see. If there is none, there is no proposal.' },
  { n: 6, band: 'reasoning', does: 'Lock the prediction, hash the file, then run it.',
    refuse: 'A result claimed with no hash behind it, and a hash edited after the run.',
    check: 'Re-hash the file. If it moved, the prediction moved with it.' },
];

// ── what this app cannot do, in one place ───────────────────────────────────
// The page RENDERS this array; it does not restate it. Editing a limit here
// edits the screen, which is the only arrangement under which a printed limit
// means anything. Each sentence is asserted present by the suite.
export const LIMITS = [
  'This does not understand what you pasted. It matches patterns in the wording.',
  'It cannot tell you whether anything is true, or whether the person sending it meant well.',
  'A message written to look manipulative and a real one read the same here.',
  'Saying nothing is the ordinary result. It does not mean a message was found safe.',
];

// What a person does next, outside this screen. A picture with nowhere to go
// after it was a mask.
export const GO_CHECK = [
  'If it asks for money or a code, hang up and call back on a number you already had.',
  'Tell one person you trust before you act on anything urgent.',
  'Look up the organisation yourself instead of using the number in the message.',
];

// ── stage 3 as arithmetic: how much of the order is actually settled ─────────
// Returns counts and the blanks BY NAME. It does not return a grade, and there
// is deliberately no percentage here: the number a person holds is how many
// questions are still open, not a mark out of ten.
export function settled(fills) {
  const f = fills && typeof fills === 'object' ? fills : {};
  const open = TEN.filter(t => {
    const v = f[t.id];
    return !(typeof v === 'string' && v.trim().length > 0);
  });
  return {
    open: open.map(t => t.id),
    openCount: open.length,
    filled: TEN.length - open.length,
    of: TEN.length,
  };
}
