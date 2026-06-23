/**
 * Skalantech Scroll Effects v2 — Modern Scroll-Animations
 * Parallax, Reading Progress, Multi-Direction Reveal, Glow, Stagger
 */
(function() {
  'use strict';

  // ================================================================
  // 1. READING PROGRESS BAR
  // ================================================================
  (function() {
    const bar = document.createElement('div');
    bar.className = 'progress-bar';
    bar.setAttribute('aria-hidden', 'true');
    document.body.prepend(bar);

    window.addEventListener('scroll', function() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.transform = 'scaleX(' + (progress / 100) + ')';
    }, { passive: true });
  })();

  // ================================================================
  // 2. HERO PARALLAX — Background + Shapes
  // ================================================================
  (function() {
    const hero = document.getElementById('hero');
    if (!hero) return;

    const bgImg = hero.querySelector('.hero__bg-img');
    const shapes = hero.querySelectorAll('.hero__geom');
    const glowOrbs = hero.querySelectorAll('.hero__glow:not(.hero__glow--cursor)');

    window.addEventListener('scroll', function() {
      const rect = hero.getBoundingClientRect();
      const heroHeight = hero.offsetHeight;
      const scrollProgress = Math.max(0, Math.min(1, -rect.top / heroHeight));

      // Background image parallax — moves at 40% speed
      if (bgImg) {
        const y = scrollProgress * 40;
        bgImg.style.transform = 'translateY(' + y + 'px) scale(1.08)';
        bgImg.style.opacity = Math.max(0.4, 0.85 - scrollProgress * 0.45);
      }

      // Floating shapes parallax — each at different speed
      shapes.forEach(function(shape, i) {
        const speed = 0.3 + (i * 0.15);
        const y = scrollProgress * 80 * speed;
        const rotate = scrollProgress * 30 * (i % 2 === 0 ? 1 : -1);
        shape.style.transform = 'translateY(' + y + 'px) rotate(' + rotate + 'deg)';
        shape.style.opacity = Math.max(0.1, 0.6 - scrollProgress * 0.5);
      });

      // Glow orbs parallax — drift away
      glowOrbs.forEach(function(orb, i) {
        const speed = 0.2 + (i * 0.1);
        const y = scrollProgress * 60 * speed;
        orb.style.transform = 'translateY(' + y + 'px)';
      });
    }, { passive: true });
  })();

  // ================================================================
  // 3. ENHANCED SCROLL REVEAL — Multi-Direction
  // ================================================================
  (function() {
    const revealObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const delay = parseFloat(el.getAttribute('data-delay')) || 0;
        const direction = el.getAttribute('data-reveal') || 'up';

        setTimeout(function() {
          el.classList.add('is-visible');
        }, delay);

        revealObserver.unobserve(el);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('[data-reveal]').forEach(function(el) {
      // Don't re-observe if already visible
      if (el.classList.contains('is-visible')) return;

      const direction = el.getAttribute('data-reveal') || 'up';

      // Set initial transform based on direction (CSS handles the rest)
      if (direction === 'left') {
        el.style.transform = 'translateX(-40px)';
        el.style.opacity = '0';
      } else if (direction === 'right') {
        el.style.transform = 'translateX(40px)';
        el.style.opacity = '0';
      } else if (direction === 'scale') {
        el.style.transform = 'scale(0.92)';
        el.style.opacity = '0';
      } else if (direction === 'up') {
        el.style.transform = 'translateY(30px)';
        el.style.opacity = '0';
      }

      el.style.transition = 'opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1)';

      revealObserver.observe(el);
    });

    // When visible, reset transform
    document.addEventListener('transitionend', function(e) {
      if (e.target.hasAttribute('data-reveal') && e.propertyName === 'opacity') {
        e.target.style.transform = '';
        e.target.style.opacity = '';
      }
    }, true);
  })();

  // ================================================================
  // 4. STAGGERED GRID — Cards appear with delay
  // ================================================================
  (function() {
    const staggerObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (!entry.isIntersecting) return;
        const grid = entry.target;
        const items = grid.querySelectorAll('[data-stagger]');
        const baseDelay = parseFloat(grid.getAttribute('data-stagger-delay')) || 80;

        items.forEach(function(item, i) {
          const delay = i * baseDelay;
          setTimeout(function() {
            item.classList.add('is-visible');
          }, delay);
        });

        staggerObserver.unobserve(grid);
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('[data-stagger-grid]').forEach(function(grid) {
      staggerObserver.observe(grid);
    });
  })();

  // ================================================================
  // 5. SECTION BACKGROUND PARALLAX
  // ================================================================
  (function() {
    const sections = document.querySelectorAll('.section--dark');

    window.addEventListener('scroll', function() {
      sections.forEach(function(section) {
        const rect = section.getBoundingClientRect();
        const vh = window.innerHeight;
        const center = rect.top + rect.height / 2;
        const distance = center / vh - 0.5; // -0.5 to 0.5

        // Subtle radial gradient shift
        const x = 50 + distance * 10;
        section.style.backgroundPosition = x + '% 0%';
      });
    }, { passive: true });
  })();

  // ================================================================
  // 6. SCROLL-TRIGGERED GLOW on project cards
  // ================================================================
  (function() {
    const cards = document.querySelectorAll('.project-card-v2');

    const cardObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('card-glow-visible');
        } else {
          entry.target.classList.remove('card-glow-visible');
        }
      });
    }, { threshold: [0, 0.3, 0.7] });

    cards.forEach(function(card) {
      cardObserver.observe(card);
    });
  })();

  // ================================================================
  // 7. ACTIVE NAV SECTION HIGHLIGHT
  // ================================================================
  (function() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav__links a[href^="#"]');

    if (!sections.length || !navLinks.length) return;

    const navObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (!entry.isIntersecting) return;
        const id = entry.target.getAttribute('id');

        navLinks.forEach(function(link) {
          link.classList.remove('nav--active');
          if (link.getAttribute('href') === '#' + id) {
            link.classList.add('nav--active');
          }
        });
      });
    }, { threshold: 0.25, rootMargin: '-80px 0px 0px 0px' });

    sections.forEach(function(section) {
      navObserver.observe(section);
    });
  })();

})();
