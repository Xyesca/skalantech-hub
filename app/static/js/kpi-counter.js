/**
 * KPI Counter — animierte Zahleneffekte.
 * Zählt von 0 zum Zielwert, sobald sichtbar.
 */
(function() {
  'use strict';

  function animateCounters() {
    const counters = document.querySelectorAll('.kpi-counter');
    if (!counters.length) return;

    counters.forEach(el => {
      const target = parseInt(el.getAttribute('data-target'), 10);
      const suffix = el.getAttribute('data-suffix') || '';
      let animated = false;

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !animated) {
            animated = true;
            const duration = Math.min(1600, Math.max(600, target * 10));
            const start = performance.now();

            function tick(now) {
              const progress = Math.min(1, (now - start) / duration);
              const eased = 1 - Math.pow(1 - progress, 3);
              const current = Math.round(target * eased);
              el.textContent = current + suffix;
              if (progress < 1) {
                requestAnimationFrame(tick);
              } else {
                el.textContent = target + suffix;
              }
            }
            requestAnimationFrame(tick);
            observer.unobserve(el);
          }
        });
      }, { threshold: 0.3 });

      observer.observe(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', animateCounters);
  } else {
    animateCounters();
  }
})();
