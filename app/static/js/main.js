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

    window.addEventListener("resize", function () {
      if (window.innerWidth > 860) closeMenu(false);
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && navigation && navigation.classList.contains("is-open")) {
      closeMenu(true);
    }
  });

  setHeaderState();
  window.addEventListener("scroll", setHeaderState, { passive: true });

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
    const activeObserver = new IntersectionObserver(
      function (entries) {
        const visible = entries
          .filter(function (entry) { return entry.isIntersecting; })
          .sort(function (a, b) { return b.intersectionRatio - a.intersectionRatio; })[0];

        if (!visible) {
          // Beim Verlassen der beobachteten Abschnitte alle veralteten Marker entfernen
          sectionLinks.forEach(function (link) {
            link.removeAttribute("aria-current");
          });
          return;
        }

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

  if (contactForm && window.fetch) {
    contactForm.addEventListener("submit", async function (event) {
      event.preventDefault();

      if (!contactForm.reportValidity()) return;

      const submitButton = contactForm.querySelector('button[type="submit"]');
      const buttonLabel = submitButton ? submitButton.querySelector("span") : null;
      const originalLabel = buttonLabel ? buttonLabel.textContent : "";

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add("is-loading");
      }
      if (buttonLabel) buttonLabel.textContent = "Wird gesendet …";
      if (formStatus) {
        formStatus.textContent = "";
        formStatus.className = "form-status";
      }

      try {
        const response = await fetch(contactForm.action, {
          method: "POST",
          body: new FormData(contactForm),
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

        contactForm.reset();
        updateMessageCount();
        if (formStatus) {
          formStatus.textContent = payload.message;
          formStatus.classList.add("is-success");
        }
      } catch (error) {
        if (formStatus) {
          formStatus.textContent = error.message || "Etwas ist schiefgelaufen. Bitte senden Sie eine E-Mail.";
          formStatus.classList.add("is-error");
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
