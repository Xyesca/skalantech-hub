(() => {
  'use strict';

  const forms = document.querySelectorAll('[data-live-demo]');
  if (!forms.length) return;

  const LABELS = {
    anfrage_typ: 'Anfragetyp',
    angebotsentwurf: 'Angebotsentwurf',
    angefragte_leistungen: 'Angefragte Leistungen',
    anmerkungen: 'Anmerkungen',
    angebot: 'Angebot',
    angebotsnummer: 'Angebotsnummer',
    ansprechpartner: 'Ansprechpartner',
    antwort_vorschlag: 'Antwortvorschlag',
    bekannte_angaben: 'Bekannte Angaben',
    bic: 'BIC',
    brutto: 'Bruttobetrag',
    data: 'Ergebnisdaten',
    datum: 'Datum',
    dringend: 'Dringend',
    dringlichkeit: 'Dringlichkeit',
    email: 'E-Mail',
    einzelpreis: 'Einzelpreis',
    empfaenger: 'Empfänger',
    empfohlene_bearbeitung: 'Empfohlene Bearbeitung',
    eskalation: 'Eskalation',
    faelligkeitsdatum: 'Fälligkeitsdatum',
    firma: 'Firma',
    gesamt: 'Gesamtbetrag',
    gueltigkeit_tage: 'Gültigkeit',
    human_review_required: 'Menschliche Prüfung erforderlich',
    iban: 'IBAN',
    kategorie: 'Kategorie',
    klassifikation: 'Klassifikation',
    kunde: 'Kunde',
    kunde_kontext: 'Kundenkontext',
    kurzfassung: 'Kurzfassung',
    leistungen: 'Leistungen',
    lieferant: 'Lieferant',
    medizinischer_inhalt: 'Medizinischer Inhalt',
    muss_kalkuliert_werden: 'Kalkulation erforderlich',
    mwst: 'Umsatzsteuer',
    mwst_betrag: 'Umsatzsteuer',
    mwst_satz: 'Umsatzsteuersatz',
    name: 'Name',
    naechster_schritt: 'Nächster Schritt',
    netto: 'Nettobetrag',
    offene_fragen: 'Offene Fragen',
    offene_informationen: 'Offene Informationen',
    ort: 'Ort',
    positionen: 'Positionen',
    plz: 'PLZ',
    pruefhinweis: 'Prüfhinweis',
    rechnungsdatum: 'Rechnungsdatum',
    rechnungsnummer: 'Rechnungsnummer',
    referenz: 'Referenz',
    strasse: 'Straße',
    umsatzsteuer: 'Umsatzsteuer',
    ust_id: 'USt-IdNr.',
    waehrung: 'Währung',
    zahlungsziel: 'Zahlungsziel',
    zahlungsziel_tage: 'Zahlungsziel',
  };

  // Spec E7: Konfidenz nur anzeigen, wenn fachlich sinnvoll kalibriert.
  // Die Demo-Workflows liefern keine belastbare Selbstbewertung → weglassen.
  const SKIP_KEYS = new Set(['konfidenz', 'vertrauen']);

  const CURRENCY_KEYS = new Set(['brutto', 'einzelpreis', 'gesamt', 'netto', 'preis', 'summe', 'umsatzsteuer', 'mwst']);

  const humanize = (key) => {
    if (LABELS[key]) return LABELS[key];
    return String(key)
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  const formatValue = (value, key = '') => {
    if (value === null || value === undefined || value === '') return 'Nicht angegeben';
    if (typeof value === 'boolean') return value ? 'Ja' : 'Nein';
    if (typeof value === 'number') {
      if (key === 'vertrauen' && value >= 0 && value <= 1) {
        return new Intl.NumberFormat('de-DE', { style: 'percent', maximumFractionDigits: 0 }).format(value);
      }
      if (key === 'gueltigkeit_tage') return `${value} Tage`;
      if (key === 'zahlungsziel_tage') return `${value} Tage`;
      if (CURRENCY_KEYS.has(key)) {
        return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value);
      }
      return new Intl.NumberFormat('de-DE', { maximumFractionDigits: 2 }).format(value);
    }
    return String(value);
  };

  const isRecord = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);

  const makeElement = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };

  const renderFields = (entries) => {
    const grid = makeElement('div', 'demo-result__fields');
    entries.forEach(([key, value]) => {
      if (SKIP_KEYS.has(key)) return;
      const formatted = formatValue(value, key);
      const isWide = formatted.length > 70 || formatted.includes('\n');
      const field = makeElement('div', `demo-result__field${isWide ? ' demo-result__field--wide' : ''}`);
      field.append(makeElement('span', 'demo-result__label', humanize(key)));
      const valueClass = `demo-result__value${formatted === 'Nicht angegeben' ? ' demo-result__value--empty' : ''}`;
      field.append(makeElement('span', valueClass, formatted));
      grid.append(field);
    });
    return grid;
  };

  const renderSection = (key, value) => {
    const section = makeElement('section', 'demo-result__section');
    if (key) section.append(makeElement('h3', 'demo-result__section-title', humanize(key)));

    if (Array.isArray(value)) {
      if (!value.length) {
        section.append(makeElement('p', 'demo-result__notice', 'Keine Einträge vorhanden.'));
        return section;
      }
      if (value.every((item) => !isRecord(item) && !Array.isArray(item))) {
        const list = makeElement('ul', 'demo-result__list');
        value.forEach((item) => list.append(makeElement('li', '', formatValue(item, key))));
        section.append(list);
        return section;
      }
      const items = makeElement('div', 'demo-result__items');
      value.forEach((item, index) => {
        const card = makeElement('div', 'demo-result__item');
        card.append(makeElement('span', 'demo-result__item-index', `Position ${index + 1}`));
        if (isRecord(item)) card.append(renderObject(item));
        else card.append(makeElement('span', 'demo-result__value', formatValue(item, key)));
        items.append(card);
      });
      section.append(items);
      return section;
    }

    if (isRecord(value)) section.append(renderObject(value));
    else section.append(renderFields([[key || 'ergebnis', value]]));
    return section;
  };

  const renderObject = (value) => {
    const fragment = document.createDocumentFragment();
    const entries = Object.entries(value);
    const simple = entries.filter(([, item]) => !isRecord(item) && !Array.isArray(item));
    const complex = entries.filter(([, item]) => isRecord(item) || Array.isArray(item));
    if (simple.length) fragment.append(renderFields(simple));
    complex.forEach(([key, item]) => fragment.append(renderSection(key, item)));
    return fragment;
  };

  const renderResult = (target, value) => {
    target.replaceChildren();
    let normalized = value;
    if (Array.isArray(normalized) && normalized.length === 1) normalized = normalized[0];
    if (isRecord(normalized) && isRecord(normalized.data)) normalized = normalized.data;
    if (isRecord(normalized)) target.append(renderObject(normalized));
    else if (Array.isArray(normalized)) target.append(renderSection('', normalized));
    else target.append(renderFields([['ergebnis', normalized]]));
    target.scrollTop = 0;
  };

  const renderNotice = (target, message, isError = false) => {
    target.replaceChildren(makeElement('p', `demo-result__notice${isError ? ' demo-result__notice--error' : ''}`, message));
    target.scrollTop = 0;
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
      const resultOutput = form.querySelector('[data-demo-result-output]');
      const original = button?.textContent || 'Demo starten';

      if (button) {
        button.disabled = true;
        button.textContent = 'Demo läuft …';
      }
      if (result) {
        result.hidden = false;
      }
      if (resultOutput) {
        renderNotice(resultOutput, 'Die Eingabe wird verarbeitet …');
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
        if (resultOutput) renderResult(resultOutput, payload.result);
      } catch (error) {
        if (resultOutput) renderNotice(resultOutput, error.message || 'Die Demo konnte nicht ausgeführt werden.', true);
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = original;
        }
      }
    });
  });
})();
