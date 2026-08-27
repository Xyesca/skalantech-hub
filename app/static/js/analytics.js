/* Skalantech Analytics — First-Party, cookie-less Conversion Tracking.
 *
 * Erfasst anonyme Interaktions-Events (Allowlist unten) und sendet sie per
 * sendBeacon/fetch an den eigenen Endpoint /analytics/event. Keine Cookies,
 * kein externer Dienst, keine personenbezogenen Inhalte.
 *
 * Session: ID + UTM/Referrer liegen nur in sessionStorage (Tab-Session).
 * Conversions (lead_created, demo_completed, meeting_booked) schreibt der
 * Server beim Formular-POST — dieser Client ergänzt dafür die Attribution
 * als Hidden-Fields im Formular.
 *
 * API (auch für zukünftige Widgets wie den ROI-Rechner):
 *   window.SkalantechAnalytics.track("roi_calculated", {savings_hours: 8});
 */
(function () {
  "use strict";

  var ENDPOINT = "/analytics/event";
  var SESSION_KEY = "skalantech:session";
  var VIEWED_KEY = "skalantech:viewed";
  var MAX_BODY = 8192;

  var EVENT_NAMES = [
    "page_view",
    "demo_started",
    "demo_completed",
    "contact_clicked",
    "calendar_opened",
    "meeting_booked",
    "booking_confirmed",
    "service_viewed",
    "case_study_viewed",
    "roi_calculated",
    "lead_created",
    "hero_cta_click",
    "quickwin_cta_click",
    "erechnung_cta_click",
    "faq_open",
    "check_cta_click",
    "form_start",
    "form_submit",
    "roi_slider_start",
    "roi_calculated",
    "roi_cta_click"
  ];

  // ── Storage (sessionStorage mit In-Memory-Fallback) ───────────────────
  var memory = {};
  var storage = {
    get: function (key) {
      try { return window.sessionStorage.getItem(key); } catch (e) { return memory[key] || null; }
    },
    set: function (key, value) {
      try { window.sessionStorage.setItem(key, value); } catch (e) { memory[key] = value; }
    }
  };

  function readJson(key, fallback) {
    var raw = storage.get(key);
    if (!raw) return fallback;
    try { return JSON.parse(raw); } catch (e) { return fallback; }
  }

  function writeJson(key, value) {
    storage.set(key, JSON.stringify(value));
  }

  function makeSessionId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return "s-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12);
  }

  function getSession() {
    var session = readJson(SESSION_KEY, null);
    var now = Date.now();
    if (!session || !session.sid) {
      session = { sid: makeSessionId(), ts: now };
    }
    // UTM/Referrer nur beim ersten Seitenaufruf der Session erfassen (First-Touch)
    if (!session.landing) {
      var params = new URLSearchParams(window.location.search);
      session.utm_source = params.get("utm_source") || "";
      session.utm_medium = params.get("utm_medium") || "";
      session.utm_campaign = params.get("utm_campaign") || "";
      session.referrer = (document.referrer || "").slice(0, 512);
      session.landing = window.location.pathname;
      writeJson(SESSION_KEY, session);
    }
    return session;
  }

  // ── Senden ────────────────────────────────────────────────────────────
  function track(eventName, props) {
    if (EVENT_NAMES.indexOf(eventName) === -1) return false;

    var session = getSession();
    var payload = {
      event: eventName,
      page: window.location.pathname,
      session_id: session.sid,
      source: session.utm_source || "",
      medium: session.utm_medium || "",
      campaign: session.utm_campaign || "",
      referrer: session.referrer || "",
      props: props || {}
    };

    var body = JSON.stringify(payload);
    if (body.length > MAX_BODY) return false;

    if (navigator.sendBeacon) {
      try {
        return navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "application/json" }));
      } catch (e) { /* fallthrough to fetch */ }
    }
    if (window.fetch) {
      try {
        fetch(ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: body,
          keepalive: true
        }).catch(function () {});
        return true;
      } catch (e) { return false; }
    }
    return false;
  }

  // ── View-Dedupe (einmal pro Session pro Element) ──────────────────────
  function hasViewed(key) {
    var viewed = readJson(VIEWED_KEY, []);
    return viewed.indexOf(key) !== -1;
  }

  function markViewed(key) {
    var viewed = readJson(VIEWED_KEY, []);
    if (viewed.indexOf(key) === -1) viewed.push(key);
    writeJson(VIEWED_KEY, viewed);
  }

  // ── Auto-Wiring (nach DOMContentLoaded) ───────────────────────────────
  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function textOf(element, selector) {
    var node = element.querySelector(selector);
    return node ? node.textContent.replace(/\s+/g, " ").trim() : "";
  }

  function ctaLabel(element) {
    if (element.classList.contains("header-cta")) return "header";
    if (element.closest(".hero")) return "hero";
    return "section";
  }

  function wireClick(selector, eventName, labelFn) {
    document.querySelectorAll(selector).forEach(function (el) {
      el.addEventListener("click", function () {
        track(eventName, { label: labelFn ? labelFn(el) : "" });
      });
    });
  }

  function wireView(selector, eventName, labelFn) {
    var elements = document.querySelectorAll(selector);
    if (!elements.length || !("IntersectionObserver" in window)) return;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var label = labelFn ? labelFn(el) : "";
        var key = eventName + ":" + label;
        if (hasViewed(key)) return;
        markViewed(key);
        track(eventName, { label: label });
        observer.unobserve(el);
      });
    }, { threshold: 0.35 });

    elements.forEach(function (el) { observer.observe(el); });
  }

  // Generisches data-track-API für zukünftige Elemente:
  //   <button data-track="contact_clicked" data-track-label="footer">…
  function wireDataTrack() {
    document.querySelectorAll("[data-track]").forEach(function (el) {
      el.addEventListener("click", function () {
        track(el.getAttribute("data-track"), {
          label: el.getAttribute("data-track-label") || ""
        });
      });
    });
  }

  // Attribution als Hidden-Fields ins Formular legen (vor dem Submit),
  // damit der Server die Conversion-Events der Session zuordnen kann.
  function injectAttribution(form) {
    var session = getSession();
    var fields = {
      session_id: session.sid,
      utm_source: session.utm_source || "",
      utm_medium: session.utm_medium || "",
      utm_campaign: session.utm_campaign || ""
    };
    Object.keys(fields).forEach(function (name) {
      var input = form.querySelector('input[name="' + name + '"]');
      if (!input) {
        input = document.createElement("input");
        input.type = "hidden";
        input.name = name;
        form.appendChild(input);
      }
      input.value = fields[name];
    });
  }

  function wireForms() {
    ["#contact-form", "#booking-form"].forEach(function (selector) {
      var form = document.querySelector(selector);
      if (!form) return;
      var started = false;
      form.addEventListener("input", function () {
        if (started) return;
        started = true;
        track("form_start", { form: selector.slice(1) });
      });
      form.addEventListener("submit", function () {
        injectAttribution(form);
        track("form_submit", { form: selector.slice(1) });
      });
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────
  onReady(function () {
    track("page_view", {});

    wireClick(".header-cta, a[href='#termin']", "demo_started", ctaLabel);
    wireClick("a[href^='mailto:']", "contact_clicked", function () { return "mailto"; });
    wireClick("a[href='#contact']", "contact_clicked", function (el) {
      return el.closest(".service-card") ? textOf(el.closest(".service-card"), "h3") : "nav";
    });

    var bookingDay = document.getElementById("booking-day");
    if (bookingDay) {
      var calendarFired = false;
      ["focusin", "click"].forEach(function (type) {
        bookingDay.addEventListener(type, function () {
          if (calendarFired) return;
          calendarFired = true;
          track("calendar_opened", {});
        });
      });
    }

    wireView(".service-card", "service_viewed", function (el) { return textOf(el, "h3"); });
    wireView(".work-card", "case_study_viewed", function (el) { return textOf(el, "h3"); });

    wireDataTrack();
    wireForms();
  });

  // Öffentliche API für Widgets (z. B. ROI-Rechner):
  window.SkalantechAnalytics = { track: track, events: EVENT_NAMES.slice() };
})();
