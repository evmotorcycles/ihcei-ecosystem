/* gate.js -- Agent Gate. KERNEL: no interface, no network, ever.
 * ===========================================================================
 * WHAT THIS IS NOT BUILT ON, AND WHY THAT IS THE FIRST THING IN THE FILE
 * The obvious design gates an assistant's chain of steps on a FIDELITY PRODUCT:
 * each hop reports how faithfully it carried the meaning, the gate multiplies
 * them, and the chain stops when the product falls below a floor D_min.
 *
 * This project already retired that gate, with its own data. FLOOR_RETIREMENT.md:
 *
 *   - the sensor that would supply D is blind most of the time. D_enc_raw = 0
 *     for 89.8% of pull requests and D_dec_raw = 0 for 83.7% (VS Code cohort,
 *     N = 3,685); it fires on 23.4%. A hard gate on a quantity you cannot
 *     measure three times in four is not operable;
 *   - the pre-registered confirmatory run on an unseen cohort (Kubernetes,
 *     ~4,979 PRs) returned a fully-powered NULL, p = 0.735;
 *   - the replacement -- a probabilistic hazard on enforcement latency -- scored
 *     AUC 0.898 against 0.828 for the deterministic floor.
 *
 * So there is no D_min in this file and no product of per-hop fidelities. A test
 * asserts it stays that way. Putting a retired floor back inside the one tool
 * whose whole claim is that it prints its limits would be the most complete way
 * to falsify the claim.
 *
 * THREE READOUTS, KEPT APART BECAUSE THEY ARE NOT THE SAME KIND OF THING
 *
 *   perimeter    set arithmetic. Which links lie inside the boundary a person
 *                drew, which cross out, and what they would have reached.
 *                Deterministic. No threshold. Measurable right now.
 *
 *   soleRoutes   Foster arithmetic. bearing = w x R = 1.000 means the link is
 *                in EVERY spanning tree: there is no way round it. Not a
 *                tunable, not a score. Measurable right now.
 *
 *   hazard       a port of tau_v_monitor/core.py: is your own time-to-close on
 *                flagged problems rising, against your OWN history. Correlational,
 *                calibrated locally, and on a fresh install it returns
 *                INSUFFICIENT_DATA -- which is every install on day one, and is
 *                the honest answer rather than a defect.
 *
 * The first two are structure and the third is latency. Fusing them into one
 * "agent safety score" would be the most saleable thing this file could produce
 * and the least honest, for the same reason cairn.js refuses to fuse structure
 * with rhetoric. There is no combined field and a test asserts none appears.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  var DAY = 86400.0;

  /* Carried across verbatim from tau_v_monitor/core.py. It is part of the
     result, not a footnote, because a number without it invites exactly the
     transplantation the retirement was about. */
  var DISCLAIMER =
    "tau_v is a correlational, probabilistic early-warning signal, not a " +
    "deterministic oracle. Use as one input to human review; calibrate to your " +
    "own history. Absolute day-counts are not transplantable thresholds.";

  /* The retirement, as a function rather than a document. A person can ask the
     tool why it does not do the obvious thing and get the answer with the
     numbers in it. */
  function retiredFloor() {
    return {
      retired: "D >= D_min, a hard gate on measured two-hop fidelity",
      because: [
        "the semantic sensor is blind most of the time: D_enc_raw = 0 for 89.8% " +
        "and D_dec_raw = 0 for 83.7% of 3,685 pull requests; it fires on 23.4%",
        "the pre-registered confirmatory test on an unseen cohort of ~4,979 pull " +
        "requests returned a fully-powered null, p = 0.735",
      ],
      replacedBy: "a probabilistic hazard on enforcement latency, AUC 0.898 against 0.828",
      record: "FLOOR_RETIREMENT.md",
    };
  }

  /* ------------------------------------------------------- 1 · perimeter --- */
  /* The person says which parts an assistant may touch. Everything else follows
     by set membership -- there is nothing here to tune, and nothing that could
     be quietly loosened to make more chains pass. */
  function perimeter(plan, allowed) {
    var inside = {}, i;
    (allowed || []).forEach(function (p) { inside[p] = true; });

    var within = [], crossing = [], beyond = [];
    (plan.links || []).forEach(function (l) {
      var a = !!inside[l[0]], b = !!inside[l[1]];
      if (a && b) {
        within.push({ from: l[0], to: l[1], weight: l[2] });
      } else if (a || b) {
        crossing.push({ from: l[0], to: l[1], weight: l[2],
                        reaches: a ? l[1] : l[0] });
      } else {
        beyond.push({ from: l[0], to: l[1], weight: l[2] });
      }
    });

    var unknown = (allowed || []).filter(function (p) {
      return (plan.parts || []).indexOf(p) < 0;
    });

    return {
      allowed: (allowed || []).slice(),
      within: within, crossing: crossing, beyond: beyond,
      /* the parts an assistant would have reached by stepping over the edge,
         named, because "denied" without a name is not a reason */
      wouldReach: crossing.map(function (c) { return c.reaches; })
        .filter(function (v, k, arr) { return arr.indexOf(v) === k; }),
      unknown: unknown,
      sealed: crossing.length === 0,
    };
  }

  /* -------------------------------------------------------- 2 · sole routes */
  /* A hop with no alternative. bearing 1.000 means the link is in every spanning
     tree, so if it fails there is no other path -- which is a different question
     from whether the step is important, and the arithmetic answers only the one
     it was asked. */
  function soleRoutes(plan) {
    var b = ENG.bearings(plan.parts, plan.links);
    var rows = b.links.filter(function (r) { return r.soleRoute; })
      .map(function (r) { return { from: r.from, to: r.to, bearing: r.bearing }; });
    return {
      routes: rows,
      count: rows.length,
      totalBearing: b.total,
      expected: b.expected,
      conserved: b.conserved,
      pieces: b.pieces,
      all: b.links.map(function (r) {
        return { from: r.from, to: r.to, bearing: r.bearing, soleRoute: r.soleRoute };
      }),
    };
  }

  /* ------------------------------------------------------------ 3 · hazard --
   * A port of tau_v_monitor/core.py. test_gate.py runs both over the same
   * histories and fails on any disagreement past 1e-9: a port nobody checks
   * drifts, and then the thing that was tested and the thing on the phone stop
   * being the same thing.
   */
  function median(xs) {
    if (!xs.length) return null;
    var s = xs.slice().sort(function (a, b) { return a - b; });
    var m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  function percentile(xs, q) {
    if (!xs.length) return null;
    var s = xs.slice().sort(function (a, b) { return a - b; });
    if (s.length === 1) return s[0];
    var rank = (q / 100) * (s.length - 1);
    var lo = Math.floor(rank), hi = Math.ceil(rank);
    if (lo === hi) return s[lo];
    var frac = rank - lo;
    return s[lo] * (1 - frac) + s[hi] * frac;
  }

  function theilSen(ys) {
    var n = ys.length, slopes = [], i, j;
    if (n < 2) return null;
    for (i = 0; i < n; i++) {
      for (j = i + 1; j < n; j++) slopes.push((ys[j] - ys[i]) / (j - i));
    }
    return slopes.length ? median(slopes) : null;
  }

  function sign(x) { return (x > 0 ? 1 : 0) - (x < 0 ? 1 : 0); }

  /* erf is not in the language, and Python's math.erf is correct to about one
     unit in the last place. The parity test asserts agreement to 1e-9, so the
     usual Abramowitz & Stegun rational approximation (fractional error 1.2e-7)
     is not good enough on its own and is used only where it cannot matter.

       |x| < 3   Taylor series, which converges quickly here and lands at
                 machine precision
       |x| >= 3  the A&S form. erfc(3) is 2.2e-5, so a fractional error of
                 1.2e-7 there is an ABSOLUTE error near 2.6e-12, and it shrinks
                 from there. p is an erfc, so absolute error is what matters. */
  var TWO_OVER_SQRT_PI = 2 / Math.sqrt(Math.PI);

  function erf(x) {
    if (Math.abs(x) < 3) {
      /* erf(x) = 2/sqrt(pi) * sum_{n>=0} (-1)^n x^(2n+1) / (n! (2n+1)) */
      var sum = 0, term = x, n = 0, add;
      while (n < 200) {
        add = term / (2 * n + 1);
        sum += add;
        if (Math.abs(add) <= 1e-18 * Math.abs(sum)) break;
        n += 1;
        term = -term * x * x / n;
      }
      return TWO_OVER_SQRT_PI * sum;
    }
    var z = Math.abs(x), t = 1 / (1 + z / 2);
    var r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 +
      t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 +
      t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? 1 - r : r - 1;
  }

  function normCdf(z) { return 0.5 * (1 + erf(z / Math.sqrt(2))); }

  function mannKendall(ys) {
    var n = ys.length, s = 0, i, j;
    if (n < 3) return { s: 0, p: 1, direction: "no trend" };
    for (i = 0; i < n - 1; i++) {
      for (j = i + 1; j < n; j++) s += sign(ys[j] - ys[i]);
    }
    var counts = {}, k;
    ys.forEach(function (y) { counts[y] = (counts[y] || 0) + 1; });
    var v = n * (n - 1) * (2 * n + 5);
    for (k in counts) {
      if (counts[k] > 1) { var t = counts[k]; v -= t * (t - 1) * (2 * t + 5); }
    }
    v /= 18;
    if (v <= 0) return { s: s, p: 1, direction: "no trend" };
    var z = s > 0 ? (s - 1) / Math.sqrt(v) : (s < 0 ? (s + 1) / Math.sqrt(v) : 0);
    var p = 2 * (1 - normCdf(Math.abs(z)));
    p = Math.min(Math.max(p, 0), 1);
    var direction = (p < 0.05 && s > 0) ? "increasing"
      : (p < 0.05 && s < 0) ? "decreasing" : "no trend";
    return { s: s, p: p, direction: direction };
  }

  /* An event is one flagged problem: opened when somebody said it was a problem,
     closed when it stopped being one. Seconds since the epoch, so nothing in
     here has to parse a date. */
  function latencyDays(e, capDays) {
    if (e.closedAt === null || e.closedAt === undefined) return null;
    var d = Math.max((e.closedAt - e.openedAt) / DAY, 0);
    return capDays ? Math.min(d, capDays) : d;
  }

  function buildWindows(events, opts) {
    var o = opts || {};
    var windowDays = o.windowDays === undefined ? 30 : o.windowDays;
    var nWindows = o.nWindows === undefined ? 12 : o.nWindows;
    var capDays = o.capDays === undefined ? 365 : o.capDays;
    var now = o.now;
    if (now === undefined || now === null) {
      var stamps = [];
      events.forEach(function (e) {
        if (e.closedAt !== null && e.closedAt !== undefined) stamps.push(e.closedAt);
        stamps.push(e.openedAt);
      });
      now = stamps.length ? Math.max.apply(null, stamps) : 0;
    }
    var win = windowDays * DAY, out = [], k;
    for (k = 0; k < nWindows; k++) {
      var end = now - k * win, start = end - win;
      var closed = [], openAges = [];
      events.forEach(function (e) {
        if (e.closedAt !== null && e.closedAt !== undefined
            && e.closedAt >= start && e.closedAt < end) {
          var lat = latencyDays(e, capDays);
          if (lat !== null) closed.push(lat);
        }
        if (e.openedAt < end
            && (e.closedAt === null || e.closedAt === undefined || e.closedAt >= end)) {
          var age = (end - e.openedAt) / DAY;
          age = capDays ? Math.min(age, capDays) : age;
          if (age >= 0) openAges.push(age);
        }
      });
      var pool = closed.concat(openAges);
      out.push({
        start: start, end: end,
        nClosed: closed.length, nOpenBacklog: openAges.length,
        tauVMean: closed.length ? closed.reduce(function (a, b) { return a + b; }, 0) / closed.length : null,
        tauVMedian: closed.length ? median(closed) : null,
        tailP95: percentile(pool, 95),
        backlogP95Age: percentile(openAges, 95),
      });
    }
    out.reverse();
    return out;
  }

  function hazard(events, opts) {
    var o = opts || {};
    var baselineWindows = o.baselineWindows === undefined ? 4 : o.baselineWindows;
    var robustZWatch = o.robustZWatch === undefined ? 1.5 : o.robustZWatch;
    var robustZAlert = o.robustZAlert === undefined ? 3.0 : o.robustZAlert;
    var tailRatioAlert = o.tailRatioAlert === undefined ? 1.5 : o.tailRatioAlert;
    var minClosed = o.minClosedPerWindow === undefined ? 3 : o.minClosedPerWindow;

    var windows = buildWindows(events || [], o);
    var series = windows.map(function (w) { return w.tauVMean; });
    var tails = windows.map(function (w) { return w.tailP95; });

    var populated = [];
    windows.forEach(function (w, i) {
      if (series[i] !== null && w.nClosed >= minClosed) populated.push(series[i]);
    });
    var need = Math.max(baselineWindows + 1, 3);
    if (populated.length < need) {
      return {
        status: "INSUFFICIENT_DATA",
        reasons: ["Only " + populated.length + " windows have >= " + minClosed +
                  " closed items; need >= " + need + " to calibrate a local " +
                  "baseline. Widen the window or extend the history."],
        trendDirection: "no trend", trendP: 1, trendSlopePerWindow: null,
        baselineTauV: null, currentTauV: null, robustZ: null, tailRatio: null,
        windows: windows, disclaimer: DISCLAIMER,
      };
    }

    var baseVals = populated.slice(0, baselineWindows);
    var current = populated[populated.length - 1];
    var baseMedian = median(baseVals);
    var q75 = percentile(baseVals, 75), q25 = percentile(baseVals, 25);
    var iqr = (q75 === null ? baseMedian : q75) - (q25 === null ? baseMedian : q25);
    iqr = (iqr && iqr > 1e-9) ? iqr : Math.max(baseMedian * 0.5, 1e-6);
    var robustZ = (current - baseMedian) / iqr;

    var baseTails = [];
    tails.forEach(function (t, i) {
      if (i < baselineWindows && t !== null) baseTails.push(t);
    });
    baseTails = baseTails.slice(0, baselineWindows);
    var curTail = null, i;
    for (i = tails.length - 1; i >= 0; i--) { if (tails[i] !== null) { curTail = tails[i]; break; } }
    var bt = baseTails.length ? median(baseTails) : null;
    var tailRatio = (curTail && bt && bt > 0) ? curTail / bt : null;

    var mk = mannKendall(populated);
    var slope = theilSen(populated);

    var rising = mk.direction === "increasing";
    var elevatedZ = robustZ >= robustZAlert;
    var elevatedTail = tailRatio !== null && tailRatio >= tailRatioAlert;
    var elevated = elevatedZ || elevatedTail;
    var watchLevel = robustZ >= robustZWatch;

    var reasons = [];
    if (rising) {
      reasons.push("Time to close flagged problems is rising across windows " +
                   "(Mann-Kendall p=" + mk.p.toFixed(3) + ", slope=" +
                   (slope >= 0 ? "+" : "") + slope.toFixed(2) + " days per window).");
    }
    if (elevatedZ) {
      reasons.push("Currently " + current.toFixed(1) + " days, which is " +
                   robustZ.toFixed(1) + " robust-SD above your own baseline of " +
                   baseMedian.toFixed(1) + " days.");
    }
    if (elevatedTail) {
      reasons.push("The oldest unresolved items are " + tailRatio.toFixed(2) +
                   "x as old as they were at baseline -- the pile is widening.");
    }

    var status;
    if (rising && elevated) {
      status = "ALERT";
    } else if (rising || elevated || watchLevel) {
      status = "WATCH";
      if (!reasons.length) {
        reasons.push("Currently " + current.toFixed(1) + " days, which is " +
                     robustZ.toFixed(1) + " robust-SD above baseline (watch level).");
      }
    } else {
      status = "OK";
      reasons.push("Time to close is steady near your own baseline (currently " +
                   current.toFixed(1) + " days against " + baseMedian.toFixed(1) +
                   "; no significant trend, p=" + mk.p.toFixed(3) + ").");
    }

    return {
      status: status, reasons: reasons,
      trendDirection: mk.direction, trendP: mk.p, trendSlopePerWindow: slope,
      baselineTauV: baseMedian, currentTauV: current,
      robustZ: robustZ, tailRatio: tailRatio,
      windows: windows, disclaimer: DISCLAIMER,
    };
  }

  /* --------------------------------------------------------------- review -- */
  /* All three, side by side, never added together. `combined` is absent on
     purpose and a test asserts no such field appears -- the same rule cairn.js
     applies to structure and rhetoric, for the same reason. */
  function review(plan, allowed, events, opts) {
    return {
      perimeter: perimeter(plan, allowed),
      soleRoutes: soleRoutes(plan),
      hazard: hazard(events || [], opts),
      retiredFloor: retiredFloor(),
    };
  }

  var API = { perimeter: perimeter, soleRoutes: soleRoutes, hazard: hazard,
              review: review, retiredFloor: retiredFloor,
              buildWindows: buildWindows, theilSen: theilSen,
              mannKendall: mannKendall, percentile: percentile, median: median,
              DISCLAIMER: DISCLAIMER, DAY: DAY };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.GATE = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
