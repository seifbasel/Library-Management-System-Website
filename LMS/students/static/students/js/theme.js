/*
 * Theme toggle (light / dark / system). The initial theme is already
 * applied synchronously by an inline script in <head> (see base.html) to
 * avoid a flash of the wrong theme; this file only wires up the visible
 * toggle control once the DOM is ready.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "lms-theme";

  function getStored() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function setStored(value) {
    try {
      if (value === "system") {
        localStorage.removeItem(STORAGE_KEY);
      } else {
        localStorage.setItem(STORAGE_KEY, value);
      }
    } catch (e) {
      /* localStorage unavailable (private mode, etc.) - theme just won't persist */
    }
  }

  function apply(theme) {
    if (theme === "light" || theme === "dark") {
      document.documentElement.setAttribute("data-theme", theme);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }

  function currentChoice() {
    return getStored() || "system";
  }

  function updateToggleUI(root, choice) {
    var buttons = root.querySelectorAll("[data-theme-choice]");
    buttons.forEach(function (btn) {
      var isActive = btn.getAttribute("data-theme-choice") === choice;
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggles = document.querySelectorAll("[data-theme-toggle]");
    if (!toggles.length) return;

    toggles.forEach(function (root) {
      updateToggleUI(root, currentChoice());
      root.addEventListener("click", function (event) {
        var btn = event.target.closest("[data-theme-choice]");
        if (!btn) return;
        var choice = btn.getAttribute("data-theme-choice");
        setStored(choice);
        apply(choice);
        toggles.forEach(function (r) {
          updateToggleUI(r, choice);
        });
      });
    });
  });
})();
