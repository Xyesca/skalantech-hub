(function () {
  "use strict";

  document.documentElement.classList.add("has-js");

  const header = document.getElementById("site-header");
  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.getElementById("site-nav");

  function setHeaderState() {
    if (header) {
      header.classList.toggle("is-scrolled", window.scrollY > 12);
    }
  }

  // rAF-Throttling für den Scroll-Handler: ein Schreibzugriff pro Frame statt pro Event.
  let scrollTicking = false;
  function onScroll() {
    if (!scrollTicking) {
      scrollTicking = true;
      window.requestAnimationFrame(function () {
        setHeaderState();
        scrollTicking = false;
      });
    }
  }

  function closeMenu(returnFocus) {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Menü öffnen");
    navigation.classList.remove("is-open");
    document.body.classList.remove("menu-open");
    if (returnFocus) menuButton.focus();
  }

  if (menuButton && navigation) {
    menuButton.addEventListener("click", function () {
      const willOpen = menuButton.getAttribute("aria-expanded") !== "true";
      menuButton.setAttribute("aria-expanded", String(willOpen));
      menuButton.setAttribute("aria-label", willOpen ? "Menü schließen" : "Menü öffnen");
      navigation.classList.toggle("is-open", willOpen);
      document.body.classList.toggle("menu-open", willOpen);
    });

    navigation.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        closeMenu(false);
      });
    });

    let resizeTimer = null;
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860 && navigation.classList.contains("is-open")) {
        clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(function () {
          closeMenu(false);
        }, 120);
      }
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && navigation && navigation.classList.contains("is-open")) {
      closeMenu(true);
    }
  });

  setHeaderState();
  window.addEventListener("scroll", onScroll, { passive: true });

  const revealElements = Array.from(document.querySelectorAll("[data-reveal]"));
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!("IntersectionObserver" in window) || reducedMotion) {
    revealElements.forEach(function (element) {
      element.classList.add("is-visible");
    });
  } else {
    const revealObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    revealElements.forEach(function (element) {
      revealObserver.observe(element);
    });
  }

  const sectionLinks = Array.from(document.querySelectorAll(".site-nav a[href*='#']"));
  const sections = sectionLinks
    .map(function (link) {
      const hash = link.getAttribute("href").split("#")[1];
      return hash ? document.getElementById(hash) : null;
    })
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    let currentActiveId = null;

    const activeObserver = new IntersectionObserver(
      function (entries) {
        const visible = entries
          .filter(function (entry) { return entry.isIntersecting; })
          .sort(function (a, b) { return b.intersectionRatio - a.intersectionRatio; })[0];

        if (!visible) {
          if (currentActiveId !== null) {
            currentActiveId = null;
            sectionLinks.forEach(function (link) {
              link.removeAttribute("aria-current");
            });
          }
          return;
        }

        if (currentActiveId === visible.target.id) return;

        currentActiveId = visible.target.id;
        sectionLinks.forEach(function (link) {
          const isActive = link.getAttribute("href").endsWith("#" + visible.target.id);
          if (isActive) {
            link.setAttribute("aria-current", "true");
          } else {
            link.removeAttribute("aria-current");
          }
        });
      },
      { threshold: 0, rootMargin: "-20% 0px -55% 0px" }
    );

    sections.forEach(function (section) {
      activeObserver.observe(section);
    });
  }

  const serviceSelect = document.getElementById("service");
  document.querySelectorAll("[data-service-choice]").forEach(function (link) {
    link.addEventListener("click", function () {
      if (!serviceSelect) return;
      const choice = link.getAttribute("data-service-choice");
      const option = Array.from(serviceSelect.options).find(function (item) {
        return item.value === choice;
      });
      if (option) serviceSelect.value = choice;
      window.setTimeout(function () {
        serviceSelect.focus({ preventScroll: true });
      }, 500);
    });
  });

  const messageField = document.getElementById("message");
  const messageCount = document.getElementById("message-count");

  function updateMessageCount() {
    if (messageField && messageCount) {
      messageCount.textContent = String(messageField.value.length);
    }
  }

  if (messageField) {
    messageField.addEventListener("input", updateMessageCount);
    updateMessageCount();
  }

  const contactForm = document.getElementById("contact-form");
  const formStatus = document.getElementById("form-status");

  const bookingForm = document.getElementById("booking-form");
  const bookingStatus = document.getElementById("booking-status");

  // CustomValidity zurücksetzen, sobald der Nutzer einen neuen Tag wählt
  const bookingDay = document.getElementById("booking-day");
  if (bookingDay) {
    bookingDay.addEventListener("input", function () {
      bookingDay.setCustomValidity("");
    });
  }

  function wireAjaxForm(form, statusEl) {
    if (!form || !statusEl || !window.fetch) return;

    form.addEventListener("submit", async function (event) {
      event.preventDefault();

      if (!form.reportValidity()) return;

      // Wunschtag: Wochenende + Vergangenheit vor dem Absenden blocken
      if (form.id === "booking-form") {
        const dayField = document.getElementById("booking-day");
        if (dayField && dayField.value) {
          const d = new Date(dayField.value + "T12:00:00");
          const weekday = d.getUTCDay();
          const today = new Date();
          today.setHours(0, 0, 0, 0);
          if (weekday === 0 || weekday === 6) {
            dayField.setCustomValidity("Termine sind nur Montag bis Freitag buchbar.");
            dayField.reportValidity();
            return;
          }
          if (d < today) {
            dayField.setCustomValidity("Bitte wählen Sie einen Termin in der Zukunft.");
            dayField.reportValidity();
            return;
          }
          dayField.setCustomValidity("");
        }
      }

      const submitButton = form.querySelector('button[type="submit"]');
      const buttonLabel = submitButton ? submitButton.querySelector("span") : null;
      const originalLabel = buttonLabel ? buttonLabel.textContent : "";

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add("is-loading");
      }
      if (buttonLabel) buttonLabel.textContent = "Wird gesendet …";
      if (statusEl) {
        statusEl.textContent = "";
        statusEl.className = "form-status";
      }

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
          }
        });

        const payload = await response.json().catch(function () {
          return { success: false, message: "Die Antwort konnte nicht verarbeitet werden." };
        });

        if (!response.ok || !payload.success) {
          throw new Error(payload.message || "Die Anfrage konnte nicht gesendet werden.");
        }

        form.reset();
        if (statusEl) {
          statusEl.textContent = payload.message;
          statusEl.classList.add("is-success");
        }
      } catch (error) {
        if (statusEl) {
          statusEl.textContent = error.message || "Etwas ist schiefgelaufen. Bitte senden Sie eine E-Mail.";
          statusEl.classList.add("is-error");
        }
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.classList.remove("is-loading");
        }
        if (buttonLabel) buttonLabel.textContent = originalLabel;
      }
    });
  }

  wireAjaxForm(contactForm, formStatus);
  wireAjaxForm(bookingForm, bookingStatus);

  document.querySelectorAll(".flash").forEach(function (flash) {
    const closeButton = flash.querySelector("button");
    const remove = function () {
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-6px)";
      window.setTimeout(function () { flash.remove(); }, 180);
    };

    if (closeButton) closeButton.addEventListener("click", remove);
    window.setTimeout(remove, 8000);
  });

  document.querySelectorAll(".about-visual__frame img").forEach(function (image) {
    image.addEventListener("error", function () {
      image.hidden = true;
      image.parentElement.classList.add("has-fallback");
    });
  });

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", function () {
      const button = document.getElementById("login-btn");
      if (!button) return;
      const text = button.querySelector(".btn__text");
      const loader = button.querySelector(".btn__loader");
      if (text) text.hidden = true;
      if (loader) loader.hidden = false;
      button.disabled = true;
    });
  }
})();
