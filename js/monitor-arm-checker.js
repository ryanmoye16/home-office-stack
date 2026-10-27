/* Monitor Arm Compatibility Checker (P2 #18, full-ownership plan).
   Checks a reader's monitor against the three monitor arms reviewed on
   Home Office Stack, using ONLY the manufacturer specs recorded in
   data/featured-products.json and each arm's review (size range, weight
   range, VESA patterns). Verdicts are strict-spec: an arm that is outside
   its own published range for this panel is reported as outside spec,
   never softened. Amazon links are rendered only for arms that fit. */
(function () {
  "use strict";

  var ARMS = [
    {
      slug: "huanuo-single-monitor-arm",
      name: "HUANUO Single Monitor Arm",
      asin: "B0CMQ5C9NQ",
      minSize: 13,
      maxSize: 32,
      sizeLabel: "13–32 in",
      minWeight: 4.4,
      maxWeight: 22,
      weightLabel: "4.4–22 lb",
      vesa: [75, 100],
      mechanism: "Gas spring"
    },
    {
      slug: "north-bayou-f80-monitor-arm",
      name: "NB North Bayou F80 Gas Spring Monitor Arm",
      asin: "B01AI2YGK4",
      minSize: 17,
      maxSize: 30,
      sizeLabel: "17–30 in (manual range)",
      minWeight: 4.4,
      maxWeight: 19.8,
      weightLabel: "4.4–19.8 lb",
      vesa: [75, 100],
      mechanism: "Gas spring"
    },
    {
      slug: "amazon-basics-monitor-arm",
      name: "Amazon Basics Single Monitor Arm",
      asin: "B0CQXMT3QC",
      minSize: null,
      maxSize: 32,
      sizeLabel: "Up to 32 in",
      minWeight: null,
      maxWeight: 20,
      weightLabel: "Up to 20 lb",
      vesa: [75, 100],
      mechanism: "Friction adjust — not a gas spring"
    }
  ];

  /* Comfortable-headroom rule used across the site's arm guides: an arm
     rated at least a third above the panel weight is the comfortable
     zone, i.e. panel weight <= 75% of the arm's ceiling. */
  var COMFORT_RATIO = 0.75;

  function evaluateArm(arm, input) {
    var fails = [];
    var notes = [];

    if (arm.minSize !== null && input.size < arm.minSize) {
      fails.push("Your " + fmt(input.size) + " in screen is below this arm's stated minimum size of " + arm.minSize + " in.");
    }
    if (input.size > arm.maxSize) {
      fails.push("Your " + fmt(input.size) + " in screen is above this arm's stated maximum of " + arm.maxSize + " in.");
    }
    if (arm.minWeight !== null && input.weight < arm.minWeight) {
      fails.push("Your panel weighs " + fmt(input.weight) + " lb without its stand — under this gas spring's " + arm.minWeight + " lb minimum, so it would tend to float up instead of staying put.");
    }
    if (input.weight > arm.maxWeight) {
      fails.push("Your panel weighs " + fmt(input.weight) + " lb without its stand — over this arm's " + arm.maxWeight + " lb ceiling.");
    }
    if (input.vesa === "200") {
      fails.push("Your VESA pattern is 200×100mm. This arm accepts 75×75 and 100×100 only.");
    }
    if (input.vesa === "none") {
      fails.push("Your monitor has no VESA mounting pattern. No standard arm fits it without the monitor maker's own adapter.");
    }

    var status;
    if (fails.length) {
      status = "outside";
    } else if (input.weight > arm.maxWeight * COMFORT_RATIO) {
      status = "tight";
      notes.push("It fits on paper, but with tight headroom: " + fmt(input.weight) + " lb is over 75% of the " + arm.maxWeight + " lb ceiling. An arm running near its rating is the one owners describe slowly sinking at full extension — treat this as a borderline fit, not a comfortable one.");
    } else {
      status = "fits";
      notes.push("Inside every stated limit with real headroom: " + fmt(input.weight) + " lb is at or under 75% of the " + arm.maxWeight + " lb ceiling.");
    }

    if (status !== "outside" && input.vesa === "unknown") {
      notes.push("Provisional on VESA: you marked the pattern as not checked. This verdict holds only if your pattern turns out to be 75×75 or 100×100 — measure the hole spacing on the back of the panel before ordering.");
    }
    if (status !== "outside" && input.curve === "deep") {
      notes.push("Deep-curve caution: a 1000R-class curve pushes the panel's weight farther from the mount and loads the tilt joint harder than the same weight in a flat panel. Owners describe that failure as the screen nodding down even when the height holds — prefer the arm with the most headroom.");
    }
    if (status !== "outside" && arm.asin === "B0CQXMT3QC" && input.move === "often") {
      notes.push("Fit is not the whole story here: this is a friction-adjust arm, and owners who reposition several times a day feel that stiffness on every move. A gas-spring arm above is the better tool for your routine, even though this one fits on spec.");
    }
    if (status !== "outside" && arm.mechanism === "Gas spring" && input.move === "often") {
      notes.push("The gas spring suits your routine: once its tension is set for your panel's weight, height moves take one hand and little effort.");
    }

    return {
      arm: arm,
      status: status,
      fails: fails,
      notes: notes,
      headroomRatio: input.weight / arm.maxWeight
    };
  }

  function evaluate(input) {
    var results = ARMS.map(function (arm) { return evaluateArm(arm, input); });
    var rank = { fits: 0, tight: 1, outside: 2 };
    results.sort(function (a, b) {
      if (rank[a.status] !== rank[b.status]) return rank[a.status] - rank[b.status];
      return a.headroomRatio - b.headroomRatio;
    });
    return results;
  }

  function fmt(n) {
    return (Math.round(n * 10) / 10).toString().replace(/\.0$/, "");
  }

  /* ---- Browser wiring (skipped when loaded under Node for tests) ---- */
  if (typeof document === "undefined") {
    if (typeof module !== "undefined" && module.exports) {
      module.exports = { ARMS: ARMS, evaluate: evaluate, evaluateArm: evaluateArm };
    }
    return;
  }

  var form = document.getElementById("arm-checker-form");
  if (!form) return;
  var resultsEl = document.getElementById("checker-results");

  function readInput() {
    return {
      size: parseFloat(form.elements["size"].value),
      weight: parseFloat(form.elements["weight"].value),
      vesa: form.elements["vesa"].value,
      move: form.elements["move"].value,
      curve: form.elements["curve"].value
    };
  }

  function badgeText(status) {
    if (status === "fits") return "Fits comfortably";
    if (status === "tight") return "Fits — tight headroom";
    return "Outside spec for your monitor";
  }

  function render(input) {
    var results = evaluate(input);
    var fitCount = results.filter(function (r) { return r.status === "fits"; }).length;
    var tightCount = results.filter(function (r) { return r.status === "tight"; }).length;

    var html = "";
    if (fitCount) {
      html += '<p class="checker-summary"><strong>' + fitCount + " of the 3 arms we review fit" + (tightCount ? ", plus " + tightCount + " borderline" : "") + ".</strong> Verdicts use the manufacturers' stated ranges — nothing here is stretched to make a sale.</p>";
    } else if (tightCount) {
      html += '<p class="checker-summary"><strong>No comfortable fit — ' + tightCount + " borderline arm" + (tightCount > 1 ? "s" : "") + " only.</strong> Each one fits on paper but runs near its weight ceiling with your panel. Read the headroom notes before choosing one over a heavier-duty arm.</p>";
    } else {
      html += '<p class="checker-summary"><strong>None of the 3 arms we review fits this monitor.</strong> That is a real answer, not a dead end: the “when none of these fits” section below lists exactly what to look for in an arm that does.</p>';
    }

    results.forEach(function (r) {
      var arm = r.arm;
      html += '<div class="checker-result checker-result--' + r.status + '">';
      html += '<div class="checker-result-head"><h3>' + arm.name + '</h3><span class="fit-badge fit-badge--' + r.status + '">' + badgeText(r.status) + "</span></div>";
      html += '<p class="checker-result-specs">' + arm.mechanism + " · Stated size " + arm.sizeLabel + " · Holds " + arm.weightLabel + " · VESA 75×75 / 100×100</p>";
      r.fails.forEach(function (f) { html += '<p class="checker-reason">✗ ' + f + "</p>"; });
      r.notes.forEach(function (n) { html += '<p class="checker-reason">' + n + "</p>"; });
      html += '<p class="checker-result-links"><a href="../reviews/' + arm.slug + '.html" class="accent-link">Read our full review →</a>';
      if (r.status !== "outside") {
        html += ' &nbsp;<a href="https://www.amazon.com/dp/' + arm.asin + '?tag=homeofficestack-20" target="_blank" rel="nofollow noopener sponsored" class="btn btn-primary btn-sm">Check price on Amazon →</a>';
      } else {
        html += ' <span class="checker-nocta">No buying link — we don’t link a purchase we just told you doesn’t fit.</span>';
      }
      html += "</p></div>";
    });

    resultsEl.innerHTML = html;
    resultsEl.hidden = false;
  }

  function runFromForm(pushUrl) {
    var input = readInput();
    if (!(input.size > 0) || !(input.weight > 0)) {
      resultsEl.innerHTML = '<p class="checker-summary">Enter both your screen size and the panel weight without its stand — those two numbers decide most of the verdict.</p>';
      resultsEl.hidden = false;
      return;
    }
    render(input);
    if (pushUrl && window.history && window.history.replaceState) {
      var q = "?size=" + encodeURIComponent(input.size) + "&weight=" + encodeURIComponent(input.weight) + "&vesa=" + encodeURIComponent(input.vesa) + "&move=" + encodeURIComponent(input.move) + "&curve=" + encodeURIComponent(input.curve);
      window.history.replaceState(null, "", q);
    }
    if (typeof window.gtag === "function") {
      window.gtag("event", "arm_checker_run", { page_path: window.location.pathname });
    }
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    runFromForm(true);
    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  /* Pre-fill from a shared link (?size=27&weight=13&vesa=100…) and run. */
  try {
    var params = new URLSearchParams(window.location.search);
    var has = false;
    ["size", "weight"].forEach(function (k) {
      if (params.get(k)) { form.elements[k].value = params.get(k); has = true; }
    });
    ["vesa", "move", "curve"].forEach(function (k) {
      if (params.get(k)) { form.elements[k].value = params.get(k); has = true; }
    });
    if (has) runFromForm(false);
  } catch (err) { /* a malformed query string should never break the page */ }
})();
