/**
 * Terminal typewriter effect for the hero section.
 * Types out script lines character by character with delays.
 */
(function() {
  'use strict';

  const terminalBody = document.getElementById('terminal-body');
  if (!terminalBody) return;

  const scriptLines = [
    { text: 'Initializing system...', status: 'ok', delay: 50 },
    { text: '[OK] M365 tenant connected', status: 'ok', delay: 40 },
    { text: '[OK] Tailscale mesh secure', status: 'ok', delay: 40 },
    { text: '[OK] Docker 14 containers up', status: 'ok', delay: 40 },
    { text: '[OK] Hermes Agent connected', status: 'ok', delay: 40 },
    { text: '[OK] n8n — 50 workflows live', status: 'ok', delay: 40 },
    { text: '[ACTIVE] AI Agent fleet ready', status: 'active', delay: 50 },
    { text: '', status: 'info', delay: 30 },
    { text: 'All systems operational.', status: 'ok', delay: 60 },
    { text: 'Ready for deployment >', status: 'active', delay: 100 },
  ];

  let currentLine = 0;
  let currentChar = 0;

  function createLineElement(status) {
    const div = document.createElement('div');
    div.className = 'line-' + status;
    return div;
  }

  function scrollToBottom() {
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }

  function typeNextChar() {
    if (currentLine >= scriptLines.length) {
      return;
    }

    const line = scriptLines[currentLine];

    if (currentChar === 0) {
      const el = createLineElement(line.status);
      el.setAttribute('data-line-index', currentLine);
      terminalBody.appendChild(el);
      const oldCursor = terminalBody.querySelector('.terminal-window__cursor');
      if (oldCursor) oldCursor.remove();
    }

    const lineEl = terminalBody.querySelector(`[data-line-index="${currentLine}"]`);
    if (!lineEl) return;

    if (currentChar < line.text.length) {
      lineEl.textContent += line.text[currentChar];
      currentChar++;

      const oldCursor = terminalBody.querySelector('.terminal-window__cursor');
      if (oldCursor) oldCursor.remove();

      const cursor = document.createElement('span');
      cursor.className = 'terminal-window__cursor';
      lineEl.appendChild(cursor);

      scrollToBottom();
      const charDelay = line.delay + (Math.random() * 20 - 10);
      setTimeout(typeNextChar, charDelay);
    } else {
      currentLine++;
      currentChar = 0;

      if (currentLine >= scriptLines.length) {
        const oldCursor = terminalBody.querySelector('.terminal-window__cursor');
        if (oldCursor) oldCursor.remove();
        const cursor = document.createElement('span');
        cursor.className = 'terminal-window__cursor';
        const lastLine = terminalBody.lastElementChild;
        if (lastLine) lastLine.appendChild(cursor);
        scrollToBottom();
        return;
      }

      const lineEndDelay = line.text.length === 0 ? 120 : 250 + Math.random() * 150;
      setTimeout(typeNextChar, lineEndDelay);
    }
  }

  terminalBody.innerHTML = '';
  setTimeout(typeNextChar, 500);
})();

/**
 * Contact Form AJAX — Terminal-Style Feedback.
 */
(function() {
  'use strict';

  const form = document.querySelector('.contact-terminal__form');
  const prompt = document.querySelector('.contact-terminal__prompt');
  if (!form || !prompt) return;

  const lines = [
    '[CONNECT] Establishing secure channel...',
    '[AUTH]   Verifying session token...',
    '[SEND]   Transmitting payload...',
    '[OK]     Message securely delivered ✓',
  ];

  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const btn = form.querySelector('.btn--primary');
    const origText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = 'Senden...';
    prompt.textContent = '';

    let lineIdx = 0;
    function typePrompt() {
      if (lineIdx >= lines.length) {
        // Final — actually submit
        const fd = new FormData(form);
        fetch(form.action, {
          method: 'POST',
          body: fd,
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
        .then(r => r.json().catch(() => ({ ok: r.ok })))
        .then(data => {
          if (data.ok || data.success) {
            prompt.textContent = '[DONE] ✓ ' + (data.message || 'Nachricht erfolgreich gesendet!');
            form.querySelectorAll('input, textarea').forEach(el => el.value = '');
          } else {
            prompt.textContent = '[FAIL] ✗ ' + (data.message || 'Fehler beim Senden');
          }
        })
        .catch(() => {
          prompt.textContent = '[FAIL] ✗ Verbindung fehlgeschlagen';
        })
        .finally(() => {
          btn.disabled = false;
          btn.innerHTML = origText;
        });
        return;
      }
      prompt.textContent = lines[lineIdx];
      lineIdx++;
      setTimeout(typePrompt, 350 + Math.random() * 200);
    }
    typePrompt();
  });
})();
