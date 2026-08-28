/* Skalantech AI Consultant — first-party chat widget.
 * No third-party chat script. Conversation state lives only in sessionStorage.
 */
(function () {
  "use strict";

  var API = "/api/ai-consultant/message";
  var ANALYTICS_API = "/analytics/event";
  var SESSION_KEY = "skalantech:ai-consultant-id";
  var MAX_MESSAGE = 1500;

  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  function conversationId() {
    try {
      var existing = sessionStorage.getItem(SESSION_KEY);
      if (existing) return existing;
    } catch (e) {}
    var value = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() :
      "chat-" + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
    try { sessionStorage.setItem(SESSION_KEY, value); } catch (e) {}
    return value;
  }

  function track(name, props) {
    var handled = false;
    if (window.SkalantechAnalytics && typeof window.SkalantechAnalytics.track === "function") {
      handled = window.SkalantechAnalytics.track(name, props || {}) === true;
    }
    if (handled) return;

    // The main analytics bundle may predate chat events. Send only anonymous
    // funnel metadata directly; chat message content is never included.
    try {
      fetch(ANALYTICS_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        keepalive: true,
        body: JSON.stringify({
          event: name,
          page: window.location.pathname,
          session_id: conversationId(),
          props: props || {}
        })
      }).catch(function () {});
    } catch (e) {}
  }

  ready(function () {
    var root = document.getElementById("ai-consultant");
    if (!root) return;

    var toggle = root.querySelector("[data-ai-toggle]");
    var panel = root.querySelector("[data-ai-panel]");
    var close = root.querySelector("[data-ai-close]");
    var form = root.querySelector("[data-ai-form]");
    var input = root.querySelector("[data-ai-input]");
    var messages = root.querySelector("[data-ai-messages]");
    var suggestions = root.querySelector("[data-ai-suggestions]");
    var status = root.querySelector("[data-ai-status]");
    var send = root.querySelector("[data-ai-send]");
    var cid = conversationId();
    var openedOnce = false;

    function setOpen(open) {
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        if (!openedOnce) {
          openedOnce = true;
          track("chat_opened", {});
        }
        window.setTimeout(function () { input.focus(); }, 30);
      }
    }

    function append(role, text) {
      var item = document.createElement("div");
      item.className = "ai-consultant__message ai-consultant__message--" + role;
      var bubble = document.createElement("div");
      bubble.className = "ai-consultant__bubble";
      bubble.textContent = text;
      item.appendChild(bubble);
      messages.appendChild(item);
      messages.scrollTop = messages.scrollHeight;
    }

    function setSuggestions(items, action) {
      suggestions.replaceChildren();
      (items || []).slice(0, 3).forEach(function (label) {
        var button = document.createElement("button");
        button.type = "button";
        button.className = "ai-consultant__suggestion";
        button.textContent = label;
        button.addEventListener("click", function () {
          input.value = label;
          form.requestSubmit();
        });
        suggestions.appendChild(button);
      });
      if (action && action.label && action.url) {
        var link = document.createElement("a");
        link.className = "ai-consultant__action";
        link.href = action.url;
        link.textContent = action.label + " →";
        link.addEventListener("click", function () {
          track("chat_action_clicked", { label: action.label });
        });
        suggestions.appendChild(link);
      }
    }

    function busy(state) {
      input.disabled = state;
      send.disabled = state;
      status.textContent = state ? "Skalantech AI analysiert …" : "";
    }

    async function submitMessage(text) {
      append("user", text);
      setSuggestions([], null);
      busy(true);
      track("chat_message_sent", { length_bucket: text.length > 400 ? "long" : text.length > 120 ? "medium" : "short" });
      try {
        var response = await fetch(API, {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify({
            message: text,
            conversation_id: cid,
            page: window.location.pathname
          })
        });
        var data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "unavailable");
        cid = data.conversation_id || cid;
        try { sessionStorage.setItem(SESSION_KEY, cid); } catch (e) {}
        append("assistant", data.reply);
        setSuggestions(data.suggestions, data.action);
        track("chat_reply_received", { source: data.source || "unknown" });
      } catch (error) {
        append("assistant", "Der Assistent ist gerade nicht erreichbar. Sie können weiterhin die Live-Demos testen oder eine Business-Analyse anfragen.");
        setSuggestions([], { label: "Live-Demos ansehen", url: "/demos" });
        track("chat_error", {});
      } finally {
        busy(false);
      }
    }

    toggle.addEventListener("click", function () { setOpen(panel.hidden); });
    close.addEventListener("click", function () { setOpen(false); toggle.focus(); });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) setOpen(false);
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var text = input.value.replace(/\s+/g, " ").trim();
      if (text.length < 2) return;
      if (text.length > MAX_MESSAGE) text = text.slice(0, MAX_MESSAGE);
      input.value = "";
      submitMessage(text);
    });

    setSuggestions([
      "Rechnungen automatisch verarbeiten",
      "E-Mails ins CRM übertragen",
      "Angebote vorbereiten"
    ], null);
  });
})();
