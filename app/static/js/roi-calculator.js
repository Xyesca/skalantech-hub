/* Skalantech ROI-Rechner — „Was kostet Sie der Papierkram?" (LUMINA UX-Spez)
 *
 * Rechnet NUR mit Nutzer-Inputs (keine erfundenen Branchenwerte), konservative
 * Defaults. Ergebnis: Stunden/Jahr + Arbeitstage + optionaler €-Wert über den
 * Verrechnungssatz (Default 65 €/h, anpassbar).
 *
 * Tracking (LUMINA/PULSE-Taxonomie, Allowlist in analytics.js + analytics.py):
 *   roi_slider_start  — erste Slider-Interaktion (1× pro Session)
 *   roi_calculated    — Wert als BUCKET (h_lt_150 | h_150_400 | h_gt_400),
 *                       nie der Rohwert, keine PII
 *   roi_cta_click     — personalisierter Ergebnis-CTA
 *
 * SENTINEL-Guardrail: roi_calculated ist reines Dashboard-Signal. Quelle der
 * Wahrheit bleiben serverseitige Conversion-Events (form_submit/lead_created).
 * Der CTA übergibt nur den Bucket (roi_context) — kein Rohwert.
 */
(function () {
  "use strict";

  var widget = document.getElementById("roi-calculator");
  if (!widget) return; // nur auf Seiten mit Rechner aktiv

  var BUCKETS = {
    low: "h_lt_150",
    mid: "h_150_400",
    high: "h_gt_400"
  };

  function bucketOf(hours) {
    if (hours < 150) return BUCKETS.low;
    if (hours <= 400) return BUCKETS.mid;
    return BUCKETS.high;
  }

  function track(eventName, props) {
    if (window.SkalantechAnalytics) {
      window.SkalantechAnalytics.track(eventName, props || {});
    }
  }

  var sliders = widget.querySelectorAll(".roi-slider__input");
  var hoursEl = document.getElementById("roi-hours");
  var daysEl = document.getElementById("roi-days");
  var valueEl = document.getElementById("roi-value");
  var textEl = document.getElementById("roi-text");
  var ctaEl = document.getElementById("roi-cta");
  var started = false;

  var RESULT_TEXTS = {};
  var resultTextsEl = document.getElementById("roi-text");
  if (resultTextsEl) {
    // Texte kommen aus dem Content-Dict (VELA/ATLAS) — stehen als data-* nicht
    // im DOM; sie werden über window-Setup vom Template injiziert (siehe unten).
  }

  function readValues() {
    var vals = {};
    sliders.forEach(function (input) {
      vals[input.getAttribute("data-key")] = parseFloat(input.value) || 0;
    });
    return vals;
  }

  function formatNumber(n) {
    return Math.round(n).toLocaleString("de-DE");
  }

  function calculate() {
    var v = readValues();
    // Formel (LUMINA): (Angebots-Std + Rechnungs-Std) × 12 + Anfragen-Std × 52
    var angeboteH = (v.angebote * v.angebot_min) / 60;
    var rechnungenH = (v.rechnungen * v.rechnung_min) / 60;
    var anfragenH = (v.anfragen * v.anfrage_min) / 60;
    var hours = angeboteH * 12 + rechnungenH * 12 + anfragenH * 52;
    var days = hours / 8;
    var rate = v.rate || 0;
    return { hours: hours, days: days, rate: rate };
  }

  function updateOutputs() {
    var r = calculate();
    var rounded = Math.round(r.hours);
    hoursEl.textContent = formatNumber(rounded);
    daysEl.textContent = "≈ " + formatNumber(r.days) + " volle Arbeitstage";
    valueEl.textContent = formatNumber(r.hours * r.rate) + " €/Jahr (bei " + formatNumber(r.rate) + " €/h)";

    var bucket = bucketOf(rounded);
    var texts = {
      low: window.SKALANTECH_ROI_TEXTS && window.SKALANTECH_ROI_TEXTS.low,
      mid: window.SKALANTECH_ROI_TEXTS && window.SKALANTECH_ROI_TEXTS.mid,
      high: window.SKALANTECH_ROI_TEXTS && window.SKALANTECH_ROI_TEXTS.high
    };
    if (textEl && texts[bucket]) {
      textEl.textContent = texts[bucket];
    }

    // Personalisierter CTA (LUMINA): konkreter Wert rein, kein generisches Label
    var campaign = widget.getAttribute("data-campaign") || "branche_handwerk";
    var base = "/?utm_source=organic&utm_medium=landing&utm_campaign=" + campaign;
    ctaEl.href = base + "&roi_context=" + bucket + "#termin";
    var label = ctaEl.querySelector("span");
    ctaEl.innerHTML = formatNumber(rounded) + " Stunden zurückgewinnen – Demo ansehen <span aria-hidden=\"true\">↗</span>";
    ctaEl.setAttribute("data-track", "roi_cta_click");
    ctaEl.setAttribute("data-track-label", bucket);

    return bucket;
  }

  // Live-Berechnung ohne Submit — Ergebnis direkt unter den Slidern sichtbar
  sliders.forEach(function (input) {
    var out = document.getElementById("roi-out-" + input.getAttribute("data-key"));
    input.addEventListener("input", function () {
      if (out) {
        var unit = input.getAttribute("data-unit") || "";
        out.textContent = input.value + (unit ? " " + unit : "");
      }
      if (!started) {
        started = true;
        track("roi_slider_start", {});
      }
      updateOutputs();
    });
  });

  var rateInput = document.getElementById("roi-rate");
  if (rateInput) {
    var rateOut = document.getElementById("roi-out-rate");
    rateInput.addEventListener("input", function () {
      if (rateOut) rateOut.textContent = rateInput.value + " €/h";
      updateOutputs();
    });
  }

  // roi_calculated: nur bei abgeschlossener Interaktion (change = Release), als Bucket
  sliders.forEach(function (input) {
    input.addEventListener("change", function () {
      var r = calculate();
      track("roi_calculated", { bucket: bucketOf(Math.round(r.hours)) });
    });
  });

  // Initial: Ergebnis + CTA einmal setzen (ohne Event — kein Fake-Event)
  updateOutputs();

  // roi_context an das Buchungsformular auf der Startseite übergeben
  // (Bucket aus der URL; serverseitig validiert, nie der Rohwert)
  var ctxInput = document.getElementById("roi-context");
  if (ctxInput) {
    var params = new URLSearchParams(window.location.search);
    var ctx = params.get("roi_context") || "";
    if (/^h_(lt_150|150_400|gt_400)$/.test(ctx)) {
      ctxInput.value = ctx;
    }
  }
})();
