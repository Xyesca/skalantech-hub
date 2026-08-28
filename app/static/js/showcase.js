(() => {
  'use strict';

  const forms = document.querySelectorAll('[data-live-demo]');
  const pretty = (value) => {
    if (typeof value === 'string') return value;
    try { return JSON.stringify(value, null, 2); } catch (_) { return String(value); }
  };

  document.querySelectorAll('[data-demo-sample]').forEach((button) => {
    button.addEventListener('click', () => {
      const form = button.closest('[data-live-demo]');
      const textarea = form?.querySelector('textarea[name="input"]');
      if (!textarea) return;
      textarea.value = button.dataset.demoSample || '';
      textarea.focus();
    });
  });

  forms.forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const result = form.querySelector('[data-demo-result]');
      const original = button?.textContent || 'Demo starten';

      if (button) {
        button.disabled = true;
        button.textContent = 'Demo läuft …';
      }
      if (result) {
        result.hidden = false;
        result.textContent = 'Verarbeitung läuft …';
      }

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || !payload.success) {
          throw new Error(payload.message || 'Die Demo konnte nicht ausgeführt werden.');
        }
        if (result) result.textContent = pretty(payload.result);
      } catch (error) {
        if (result) result.textContent = `Hinweis: ${error.message}`;
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = original;
        }
      }
    });
  });

  // AI Consultant is mounted client-side so all public templates inherit it
  // without duplicating markup. Admin/auth routes are intentionally excluded.
  const publicPath = !window.location.pathname.startsWith('/admin') &&
    !window.location.pathname.startsWith('/login') &&
    !window.location.pathname.startsWith('/auth');

  if (publicPath && !document.getElementById('ai-consultant')) {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = '/static/css/ai-consultant.css?v=1';
    document.head.appendChild(stylesheet);

    const root = document.createElement('aside');
    root.id = 'ai-consultant';
    root.className = 'ai-consultant';
    root.setAttribute('aria-label', 'Skalantech AI Consultant');
    root.innerHTML = `
      <button class="ai-consultant__toggle" type="button" data-ai-toggle aria-expanded="false" aria-controls="ai-consultant-panel">
        <span class="ai-consultant__toggle-dot" aria-hidden="true"></span>
        <span class="ai-consultant__toggle-label">AI Consultant</span>
      </button>
      <section class="ai-consultant__panel" id="ai-consultant-panel" data-ai-panel hidden aria-label="Chat mit dem Skalantech AI Consultant">
        <div class="ai-consultant__inner">
          <header class="ai-consultant__head">
            <div><strong>Skalantech AI Consultant</strong><span>KI-Assistent · kein menschlicher Mitarbeiter</span></div>
            <button class="ai-consultant__close" type="button" data-ai-close aria-label="Chat schließen">×</button>
          </header>
          <div class="ai-consultant__notice">Beschreiben Sie einen manuellen Geschäftsprozess. Bitte keine Passwörter, vertraulichen Kundendaten oder sensiblen Informationen eingeben.</div>
          <div class="ai-consultant__messages" data-ai-messages aria-live="polite">
            <div class="ai-consultant__message ai-consultant__message--assistant"><div class="ai-consultant__bubble">Hallo. Ich bin der Skalantech AI Consultant. Welcher Geschäftsprozess kostet heute unnötig Zeit?</div></div>
          </div>
          <div class="ai-consultant__suggestions" data-ai-suggestions>
            <button type="button" class="ai-consultant__suggestion">Rechnungen automatisch verarbeiten</button>
            <button type="button" class="ai-consultant__suggestion">E-Mails ins CRM übertragen</button>
            <button type="button" class="ai-consultant__suggestion">Angebote vorbereiten</button>
          </div>
          <form class="ai-consultant__form" data-ai-form>
            <div class="ai-consultant__composer">
              <textarea class="ai-consultant__input" data-ai-input rows="2" maxlength="1500" placeholder="z. B. Kundenanfragen kommen per E-Mail und werden manuell ins CRM übertragen …" aria-label="Nachricht an den AI Consultant"></textarea>
              <button class="ai-consultant__send" data-ai-send type="submit" aria-label="Nachricht senden">→</button>
            </div>
            <div class="ai-consultant__status" data-ai-status aria-live="polite"></div>
          </form>
        </div>
      </section>`;
    document.body.appendChild(root);

    const script = document.createElement('script');
    script.src = '/static/js/ai-consultant.js?v=1';
    script.defer = true;
    document.body.appendChild(script);
  }
})();
