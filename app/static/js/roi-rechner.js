/* ═══════════════════════════════════════════════════════════════════════
 * Skalantech ROI-Rechner (P1) — /rechner + Homepage-Sektion
 * Port 1:1 des verifizierten LUMINA-Prototyps (t_ce7fda15).
 * Formel exakt nach 03_FORMEL-INTERAKTION.md §1, Trigger nach §5,
 * Props nach 04_EVENT-SPEC-ROI-CALCULATED.md.
 * Vanilla JS, keine Dependencies. Auto-Init auf [data-roi-rechner].
 * Tracking-Guard: window.SkalantechAnalytics.track — Widget funktioniert
 * auch ohne Tracker (analytics.js fehlt → kein Event, kein Fehler).
 * ═══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var ARBEITSWOCHEN = 47;

  var nfEuro = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 0 });
  var nfHour = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 1 });

  // Kleinstwerte exakt, sonst auf 100 € runden (03 §1)
  function roundEuro(x) {
    return x >= 100 ? Math.round(x / 100) * 100 : Math.round(x);
  }

  function calc(v) {
    var zeitWoche = (v.minutes / 60) * v.frequency;
    var nacharbeit = zeitWoche * (v.error / 100);
    var gesamtWoche = zeitWoche + nacharbeit;
    var gesamtJahr = gesamtWoche * ARBEITSWOCHEN;
    var kosten = gesamtJahr * v.rate;
    var sparH = gesamtJahr * (v.auto / 100);
    var sparEuro = sparH * v.rate;
    return {
      hours_per_week: Math.round(gesamtWoche * 10) / 10,
      hours_per_year: Math.round(gesamtJahr * 100) / 100,
      annual_cost: roundEuro(kosten),
      savings_hours: Math.round(sparH),
      savings_euro: roundEuro(sparEuro)
    };
  }

  function readInputs(root) {
    var q = function (sel) { return root.querySelector(sel); };
    return {
      process: q("#roi-process") ? q("#roi-process").value : "angebote",
      minutes: parseInt(q("#roi-minutes").value, 10) || 30,
      frequency: parseInt(q("#roi-frequency").value, 10) || 5,
      error: parseInt(q("#roi-error").value, 10) || 10,
      rate: parseInt(q("#roi-rate").value, 10) || 55,
      auto: parseInt(q("#roi-auto").value, 10) || 70
    };
  }

  function fireEvent(props) {
    if (window.SkalantechAnalytics && window.SkalantechAnalytics.track) {
      window.SkalantechAnalytics.track("roi_calculated", props);
    }
  }

  /* ── Debounce/Throttle/Cap (03 §5) ─────────────────────────────────── */
  function makeTracker(root, source) {
    var lastFire = 0;
    var timer = null;
    var count = 0;
    var CAP = 20;
    var key = "skalantech:roi_count:" + source;
    try { count = parseInt(window.sessionStorage.getItem(key), 10) || 0; } catch (e) { count = 0; }

    function buildProps(v, action) {
      var r = calc(v);
      return {
        process: v.process,
        source: source,
        minutes: v.minutes,
        frequency: v.frequency,
        error_share: v.error,
        rate: v.rate,
        automation_share: v.auto,
        hours_per_week: r.hours_per_week,
        hours_per_year: r.hours_per_year,
        annual_cost: r.annual_cost,
        savings_hours: r.savings_hours,
        savings_euro: r.savings_euro,
        action: action
      };
    }

    function send(action, v) {
      if (count >= CAP) return;
      count += 1;
      try { window.sessionStorage.setItem(key, String(count)); } catch (e) {}
      fireEvent(buildProps(v, action));
    }

    return {
      onInput: function (v) {
        var now = Date.now();
        clearTimeout(timer);
        timer = setTimeout(function () {
          if (now - lastFire >= 3000) {   // Throttle: max 1×/3 s
            lastFire = now;
            send("recalc", v);
          }
        }, 800);                          // Debounce: 800 ms nach letzter Änderung
      },
      onCta: function (v) {
        clearTimeout(timer);
        send("cta", v);
      }
    };
  }

  /* ── Rendering ──────────────────────────────────────────────────────── */
  function formatEuro(x) { return nfEuro.format(x); }
  function formatHour(x) { return nfHour.format(x); }

  function render(root, v, r) {
    var out = function (sel) { return root.querySelector(sel); };
    if (out("#roi-minutes-out")) {
      out("#roi-minutes-out").textContent = v.minutes + " Minuten";
      out("#roi-minutes-out").setAttribute("aria-valuetext", v.minutes + " Minuten pro Durchlauf");
    }
    if (out("#roi-frequency-out")) out("#roi-frequency-out").textContent = v.frequency + " × pro Woche";
    if (out("#roi-error-out")) out("#roi-error-out").textContent = v.error + " %";
    if (out("#roi-rate-out")) out("#roi-rate-out").textContent = v.rate + " €/h";
    if (out("#roi-auto-out")) out("#roi-auto-out").textContent = v.auto + " %";

    // Ranges: aria-valuetext synchron halten
    ["#roi-minutes", "#roi-error", "#roi-auto"].forEach(function (sel) {
      var el = root.querySelector(sel);
      if (!el) return;
      var labels = {
        "#roi-minutes": v.minutes + " Minuten pro Durchlauf",
        "#roi-error": v.error + " Prozent Nacharbeit",
        "#roi-auto": v.auto + " Prozent automatiserbar"
      };
      el.setAttribute("aria-valuetext", labels[sel]);
    });

    var costEl = root.querySelector(".roi-result__cost .roi-cost-val") ||
                 root.querySelector("#roi-cost");
    if (costEl) costEl.textContent = "≈ " + formatEuro(r.annual_cost) + " €";
    var savEl = root.querySelector(".roi-result__detail .roi-savings-val") ||
                root.querySelector("#roi-savings");
    if (savEl) savEl.textContent = formatEuro(r.savings_euro) + " €";
    var hoursEl = root.querySelector(".roi-result__detail .roi-hours-val") ||
                  root.querySelector("#roi-hours");
    if (hoursEl) hoursEl.textContent = formatHour(r.savings_hours) + " h";
  }

  /* ── Init ───────────────────────────────────────────────────────────── */
  function init(root) {
    var source = root.getAttribute("data-source") || "rechner";
    var idx = Array.prototype.indexOf.call(document.querySelectorAll("[data-roi-rechner]"), root);
    var suffix = idx > 0 ? "-" + (idx + 1) : "";

    // Eindeutige IDs bei mehreren Instanzen (P1: eine je Seite, trotzdem robust)
    ["roi-process", "roi-minutes", "roi-frequency", "roi-error", "roi-rate", "roi-auto",
     "roi-minutes-out", "roi-frequency-out", "roi-error-out", "roi-rate-out", "roi-auto-out"]
      .forEach(function (id) {
        var el = root.querySelector("#" + id);
        if (el && suffix) el.id = id + suffix;
        // Label-for synchron halten (A11y bei Multi-Instanz)
        var label = root.querySelector('label[for="' + id + '"]');
        if (label && suffix) label.setAttribute("for", id + suffix);
      });

    var q = function (sel) { return root.querySelector(sel); };
    var inputs = ["#roi-minutes", "#roi-frequency", "#roi-error", "#roi-rate", "#roi-auto", "#roi-process"]
      .map(function (sel) { return q(sel); })
      .filter(Boolean);

    var tracker = makeTracker(root, source);

    function update() {
      var v = readInputs(root);
      var r = calc(v);
      render(root, v, r);
      return v;
    }

    inputs.forEach(function (el) {
      el.addEventListener("input", function () {
        var v = update();
        tracker.onInput(v);
      });
      el.addEventListener("change", function () {
        var v = update();
        tracker.onInput(v);
      });
    });

    // Number-Inputs klemmend bei blur (03 §3) — nie blockierend
    ["#roi-frequency", "#roi-rate"].forEach(function (sel) {
      var el = q(sel);
      if (!el) return;
      el.addEventListener("blur", function () {
        var min = parseInt(el.min, 10), max = parseInt(el.max, 10);
        var val = parseInt(el.value, 10);
        if (isNaN(val)) val = min;
        val = Math.max(min, Math.min(max, val));
        el.value = val;
        update();
      });
    });

    // Enter macht nichts (kein Form-Reload)
    root.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target && e.target.tagName === "INPUT") {
        e.preventDefault();
      }
    });

    // CTA-Event (03 §5.2) — immer feuern, auch wenn gerade Recalc lief
    var cta = root.querySelector(".roi-result__cta, .roi-cta-link");
    if (cta) {
      cta.addEventListener("click", function () {
        tracker.onCta(readInputs(root));
      });
    }

    // Initial rendern (kein Event — 03 §5.1)
    update();
  }

  document.querySelectorAll("[data-roi-rechner]").forEach(init);
})();
