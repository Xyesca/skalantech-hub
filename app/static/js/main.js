/* ═══════════════════════════════════════════════════════════════════════
   Skalantech Hub — Client-side Interactions
   Particles · Scroll Reveal · Sidebar · Modals · Toasts
   ═══════════════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  /* ── Particle Field ─────────────────────────────────────────────────── */
  class ParticleField {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.particles = [];
      this.raf = null;

      this._resize = this._resize.bind(this);
      window.addEventListener("resize", this._resize);
      this._resize();
      this._seed();
      this._loop();
    }

    _resize() {
      const p = this.canvas.parentElement;
      this.canvas.width = p.clientWidth;
      this.canvas.height = p.clientHeight;
    }

    _seed() {
      const area = this.canvas.width * this.canvas.height;
      const n = Math.min(Math.floor(area / 18000), 70);
      this.particles = [];
      const colors = ["6,182,212", "139,92,246", "59,130,246"];

      for (let i = 0; i < n; i++) {
        this.particles.push({
          x: Math.random() * this.canvas.width,
          y: Math.random() * this.canvas.height,
          vx: (Math.random() - 0.5) * 0.35,
          vy: (Math.random() - 0.5) * 0.35,
          r: Math.random() * 1.5 + 0.5,
          a: Math.random() * 0.4 + 0.1,
          c: colors[Math.floor(Math.random() * colors.length)],
        });
      }
    }

    _loop() {
      const { ctx, canvas, particles } = this;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.c},${p.a})`;
        ctx.fill();
      }

      /* Connections */
      const maxD = 130;
      const maxD2 = maxD * maxD;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d2 = dx * dx + dy * dy;
          if (d2 < maxD2) {
            const alpha = 0.07 * (1 - Math.sqrt(d2) / maxD);
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(6,182,212,${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      this.raf = requestAnimationFrame(() => this._loop());
    }

    destroy() {
      window.removeEventListener("resize", this._resize);
      cancelAnimationFrame(this.raf);
    }
  }

  /* Init particles */
  const heroCanvas = document.getElementById("hero-particles");
  if (heroCanvas) {
    /* Respect prefers-reduced-motion */
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (!mq.matches) {
      new ParticleField(heroCanvas);
    }
  }


  /* ── Scroll Reveal ──────────────────────────────────────────────────── */
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          revealObserver.unobserve(e.target);
        }
      });
    },
    { threshold: 0.08 }
  );
  document.querySelectorAll("[data-reveal]").forEach((el) =>
    revealObserver.observe(el)
  );


  /* ── Sidebar toggle (Admin) ─────────────────────────────────────────── */
  const sidebar = document.getElementById("admin-sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  const toggleBtn = document.getElementById("sidebar-toggle");
  const closeBtn = document.getElementById("sidebar-close");

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add("is-open");
    if (overlay) overlay.classList.add("is-visible");
    document.body.style.overflow = "hidden";
  }
  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove("is-open");
    if (overlay) overlay.classList.remove("is-visible");
    document.body.style.overflow = "";
  }

  if (toggleBtn) toggleBtn.addEventListener("click", openSidebar);
  if (closeBtn) closeBtn.addEventListener("click", closeSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);


  /* ── Modals ─────────────────────────────────────────────────────────── */
  window.openModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("is-open");
      document.body.style.overflow = "hidden";
    }
  };
  window.closeModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove("is-open");
      document.body.style.overflow = "";
    }
  };

  /* Close modal on backdrop click */
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove("is-open");
        document.body.style.overflow = "";
      }
    });
  });

  /* Close modal on Escape */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop.is-open").forEach((el) => {
        el.classList.remove("is-open");
      });
      document.body.style.overflow = "";
    }
  });


  /* ── Toast auto-dismiss ─────────────────────────────────────────────── */
  const toastStack = document.getElementById("toast-stack");
  if (toastStack) {
    setTimeout(() => {
      toastStack.style.transition = "opacity 0.4s ease";
      toastStack.style.opacity = "0";
      setTimeout(() => toastStack.remove(), 400);
    }, 5000);
  }


  /* ── Login form spinner ─────────────────────────────────────────────── */
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", () => {
      const btn = document.getElementById("login-btn");
      if (btn) {
        const text = btn.querySelector(".btn__text");
        const loader = btn.querySelector(".btn__loader");
        if (text) text.hidden = true;
        if (loader) loader.hidden = false;
        btn.disabled = true;
        btn.style.opacity = "0.7";
      }
    });
  }
})();
