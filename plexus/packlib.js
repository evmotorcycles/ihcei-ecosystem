/* packlib.js -- the packs themselves. DATA ONLY: no arithmetic lives in here.
 * ===========================================================================
 * NO PACK CARRIES A REAL COMPANY'S RATES, AND THAT IS DELIBERATE
 * Every pack below is a general shape: a metered bill, a payslip, a deposit.
 * None of them says what any named supplier charges.
 *
 * Shipping a specific tariff I cannot verify would be worse than the blank
 * canvas it replaces. A blank canvas tells you nothing; a confidently wrong
 * "what it should be" tells you something false at the exact moment you are
 * least able to notice, which is the failure this whole stack is arranged
 * against. Provider-specific packs belong in the commons, contributed by people
 * holding the actual paper, with provenance attached.
 *
 * NO CURRENCY, ANYWHERE
 * Numbers only. These are used in places with different money and the shape of
 * a metered bill is the same in all of them.
 *
 * EVERY PACK DECLARES WHAT IT TAKES FOR GRANTED
 * A pack with no `assumes` is refused. The flat-rate assumption is the whole
 * reason a stepped tariff will not match, and a person who is not told that
 * will read the difference as an accusation rather than as a fact about the
 * shape of their tariff.
 */
(function (root) {
  "use strict";

  var PACKS = [

    {
      id: "metered-bill",
      title: "A metered bill",
      about: "Water, electricity, gas — anything charged by a reading on a meter " +
             "plus a standing charge.",
      assumes: [
        "One price for every unit. If your tariff charges different prices in bands or steps, this will not match, and the difference is telling you about the shape of the tariff rather than accusing anybody.",
        "The reading now is later than the reading before it.",
        "Nothing else is on the bill — no arrears, no adjustment, no tax added afterwards.",
      ],
      goCheck: [
        "Go and read the meter yourself, now, and see whether it is past the reading they used.",
        "Find the price per unit printed on the bill and check it against the tariff on their website or your contract.",
      ],
      asks: [
        { key: "now", label: "Meter reading now", hint: "The number on the meter this time." },
        { key: "before", label: "Meter reading last time", hint: "Usually printed on the same bill." },
        { key: "rate", label: "Price per unit", hint: "What one unit costs." },
        { key: "fee", label: "Fixed charge", hint: "The standing or monthly charge, before any usage." },
        { key: "printed", label: "The total they printed", hint: "The amount the bill says you owe." },
        { key: "paid", label: "What you actually paid", optional: true,
          hint: "Only if you have paid it. Leave empty otherwise." },
      ],
      derive: [
        { key: "units", label: "Units used", expr: ["-", "now", "before"] },
        { key: "usage", label: "Cost of the units", expr: ["*", "units", "rate"] },
        { key: "total", label: "What the bill should be", expr: ["+", "usage", "fee"] },
        /* TWO carried-forward figures, because there are two, and a single one
           would be ambiguous exactly when it matters. If the printed total and
           these parts disagree, what you are owed depends on which of the two
           is right -- and the pack does not know. They read the same number
           whenever the bill matches, and diverge by precisely the amount under
           dispute when it does not. */
        { key: "carried", label: "Carried to next time, taking their total as correct",
          expr: ["-", "paid", "printed"],
          note: "Positive means you paid more than they asked, so it should appear as credit next time." },
        { key: "carriedIfParts", label: "Carried to next time, if these parts are right",
          expr: ["-", "paid", "total"],
          note: "The same figure as above whenever the bill matches. When it does not, the gap between the two lines is the amount in dispute." },
      ],
      check: { computed: "total", printed: "printed" },
      structure: {
        parts: ["Meter reading now", "Meter reading last time", "Units used",
                "Price per unit", "Fixed charge", "What the bill should be"],
        links: [
          ["Meter reading now", "Units used", 1.0],
          ["Meter reading last time", "Units used", 1.0],
          ["Units used", "What the bill should be", 1.0],
          ["Price per unit", "What the bill should be", 1.0],
          ["Fixed charge", "What the bill should be", 1.0],
        ],
      },
    },

    {
      id: "payslip",
      title: "A payslip",
      about: "What was earned, what was taken off, and whether the take-home follows.",
      assumes: [
        "Every deduction on the slip is one of the four asked for here. If there is a fifth line, put it under other deductions or the total will not match.",
        "Nothing is added after the deductions — no expenses, no reimbursement.",
      ],
      goCheck: [
        "Check the tax figure against a public tax calculator for your own income and allowances.",
        "Ask what the pension line is being taken for, and whether you agreed the rate.",
      ],
      asks: [
        { key: "gross", label: "Gross pay", hint: "Before anything is taken off." },
        { key: "tax", label: "Tax", hint: "The income tax line." },
        { key: "pension", label: "Pension or social contribution" },
        { key: "other", label: "Other deductions", hint: "Everything else taken off. Type 0 if none." },
        { key: "printed", label: "Take-home they printed" },
      ],
      derive: [
        { key: "taken", label: "Taken off altogether", expr: ["+", "tax", "pension", "other"] },
        { key: "net", label: "What the take-home should be", expr: ["-", "gross", "taken"] },
      ],
      check: { computed: "net", printed: "printed" },
      structure: {
        parts: ["Gross pay", "Tax", "Pension", "Other deductions",
                "Taken off altogether", "What the take-home should be"],
        links: [
          ["Tax", "Taken off altogether", 1.0],
          ["Pension", "Taken off altogether", 1.0],
          ["Other deductions", "Taken off altogether", 1.0],
          ["Gross pay", "What the take-home should be", 1.0],
          ["Taken off altogether", "What the take-home should be", 1.0],
        ],
      },
    },

    {
      id: "invoice-with-tax",
      title: "An invoice with tax added",
      about: "A subtotal, a percentage on top, and the total at the bottom.",
      assumes: [
        "The tax is a straight percentage of the subtotal, applied once.",
        "Nothing is exempt. If some lines are taxed and others are not, this will not match.",
      ],
      goCheck: [
        "Check the percentage against the current rate where the work was done, not where you live.",
        "Look at whether any line on the invoice should have been exempt.",
      ],
      asks: [
        { key: "subtotal", label: "Subtotal", hint: "Before tax." },
        { key: "percent", label: "Tax percent", hint: "Just the number, so 18 for eighteen percent." },
        { key: "printed", label: "The total they printed" },
      ],
      derive: [
        { key: "tax", label: "Tax on that", expr: ["*", "subtotal", ["/", "percent", 100]] },
        { key: "total", label: "What the total should be", expr: ["+", "subtotal", "tax"] },
      ],
      check: { computed: "total", printed: "printed" },
      structure: {
        parts: ["Subtotal", "Tax percent", "Tax on that", "What the total should be"],
        links: [
          ["Subtotal", "Tax on that", 1.0],
          ["Tax percent", "Tax on that", 1.0],
          ["Tax on that", "What the total should be", 1.0],
          ["Subtotal", "What the total should be", 1.0],
        ],
      },
    },

    {
      id: "deposit-returned",
      title: "A deposit coming back",
      about: "What was held, what was taken out of it, and what should come back.",
      assumes: [
        "Three deductions is enough. If there are more, add them together and put the sum in one line, and keep the itemised list yourself.",
        "No interest was owed on the deposit while it was held.",
      ],
      goCheck: [
        "Ask for the receipt or quote behind every deduction, in writing.",
        "Compare each deduction against the condition report from when you moved in.",
      ],
      asks: [
        { key: "held", label: "Deposit they held" },
        { key: "d1", label: "First deduction", hint: "Type 0 if there is none." },
        { key: "d2", label: "Second deduction", hint: "Type 0 if there is none." },
        { key: "d3", label: "Third deduction", hint: "Type 0 if there is none." },
        { key: "printed", label: "What they say they are returning" },
      ],
      derive: [
        { key: "taken", label: "Taken out of it", expr: ["+", "d1", "d2", "d3"] },
        { key: "back", label: "What should come back", expr: ["-", "held", "taken"] },
      ],
      check: { computed: "back", printed: "printed" },
      structure: {
        parts: ["Deposit they held", "First deduction", "Second deduction",
                "Third deduction", "Taken out of it", "What should come back"],
        links: [
          ["First deduction", "Taken out of it", 1.0],
          ["Second deduction", "Taken out of it", 1.0],
          ["Third deduction", "Taken out of it", 1.0],
          ["Deposit they held", "What should come back", 1.0],
          ["Taken out of it", "What should come back", 1.0],
        ],
      },
    },

    {
      id: "splitting-a-bill",
      title: "Splitting something between people",
      about: "One total, several people, and what each one owes.",
      assumes: [
        "Everybody pays the same share. If somebody had more, this is the wrong shape and you want the amounts listed separately.",
      ],
      goCheck: [
        "Say the per-person figure out loud to everyone before anybody transfers anything.",
      ],
      asks: [
        { key: "total", label: "The whole amount" },
        { key: "people", label: "How many people" },
      ],
      derive: [
        { key: "each", label: "Each person owes", expr: ["/", "total", "people"] },
      ],
      structure: {
        parts: ["The whole amount", "How many people", "Each person owes"],
        links: [
          ["The whole amount", "Each person owes", 1.0],
          ["How many people", "Each person owes", 1.0],
        ],
      },
    },

    {
      id: "paying-in-instalments",
      title: "Paying for something in instalments",
      about: "What it costs in the end, next to what it costs today.",
      assumes: [
        "Every instalment is the same size, and there are no fees beyond them.",
        "Nothing is added for paying late, because that has not happened yet.",
      ],
      goCheck: [
        "Ask the seller for the cash price if you paid it all today, and put that in the first box.",
        "Ask what happens to the figure if you miss one, and get the answer in writing.",
      ],
      asks: [
        { key: "cash", label: "Price if you paid it all today" },
        { key: "deposit", label: "Deposit up front", hint: "Type 0 if there is none." },
        { key: "each", label: "Each instalment" },
        { key: "howmany", label: "How many instalments" },
      ],
      derive: [
        { key: "instalments", label: "All the instalments together", expr: ["*", "each", "howmany"] },
        { key: "paid", label: "What you will have paid in the end", expr: ["+", "deposit", "instalments"] },
        { key: "extra", label: "What the waiting costs you", expr: ["-", "paid", "cash"],
          note: "This is the whole point of the pack. It is rarely the number on the advertisement." },
      ],
      structure: {
        parts: ["Price if you paid it all today", "Deposit up front", "Each instalment",
                "How many instalments", "All the instalments together",
                "What you will have paid in the end", "What the waiting costs you"],
        links: [
          ["Each instalment", "All the instalments together", 1.0],
          ["How many instalments", "All the instalments together", 1.0],
          ["Deposit up front", "What you will have paid in the end", 1.0],
          ["All the instalments together", "What you will have paid in the end", 1.0],
          ["What you will have paid in the end", "What the waiting costs you", 1.0],
          ["Price if you paid it all today", "What the waiting costs you", 1.0],
        ],
      },
    },

  ];

  var API = { packs: PACKS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.PACKLIB = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
