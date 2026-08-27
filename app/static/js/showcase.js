(() => {
  'use strict';

  const forms = document.querySelectorAll('[data-live-demo]');
  if (!forms.length) return;

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
})();
