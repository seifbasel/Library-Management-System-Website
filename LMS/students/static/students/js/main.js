/*
 * Small, dependency-free UI interactions: mobile nav drawer and a
 * reusable confirmation modal for destructive/important form submissions.
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    setupMobileNav();
    setupHeaderSearchShortcut();
    setupConfirmModal();
    setupSubmitLoadingState();
  });

  function setupHeaderSearchShortcut() {
    var searchInput = document.getElementById("header-search-input");
    if (!searchInput) return;

    document.addEventListener("keydown", function (event) {
      var target = event.target;
      var isTyping = target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
      if (event.key === "/" && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();
        searchInput.focus();
      }
    });
  }

  /*
   * Shows a spinner on a form's submit button while a normal (full page
   * reload) submission is in flight, to prevent double-submits and give
   * immediate feedback. Skipped for forms gated by the confirm modal -
   * those only submit once the user has already confirmed.
   */
  function setupSubmitLoadingState() {
    document.querySelectorAll("form:not([data-confirm])").forEach(function (form) {
      form.addEventListener("submit", function () {
        var submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.classList.add("is-loading");
          submitBtn.disabled = true;
        }
      });
    });
  }

  function setupMobileNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-nav]");
    var backdrop = document.querySelector("[data-nav-backdrop]");
    if (!toggle || !nav || !backdrop) return;

    function close() {
      nav.classList.remove("is-open");
      backdrop.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }

    function open() {
      nav.classList.add("is-open");
      backdrop.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
    }

    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.contains("is-open");
      isOpen ? close() : open();
    });
    backdrop.addEventListener("click", close);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
  }

  /*
   * Any <form> with data-confirm="..." pops a confirmation modal before
   * actually submitting. The modal markup itself lives once in base.html
   * (#confirm-modal) and is reused for every such form.
   */
  function setupConfirmModal() {
    var modal = document.getElementById("confirm-modal");
    if (!modal) return;

    var titleEl = modal.querySelector("[data-confirm-title]");
    var bodyEl = modal.querySelector("[data-confirm-body]");
    var confirmBtn = modal.querySelector("[data-confirm-accept]");
    var cancelBtns = modal.querySelectorAll("[data-confirm-cancel]");
    var pendingForm = null;

    function openModal(form) {
      pendingForm = form;
      titleEl.textContent = form.getAttribute("data-confirm-title") || "Are you sure?";
      bodyEl.textContent = form.getAttribute("data-confirm") || "This action cannot be undone.";
      confirmBtn.textContent = form.getAttribute("data-confirm-label") || "Confirm";
      modal.classList.add("is-open");
      confirmBtn.focus();
    }

    function closeModal() {
      modal.classList.remove("is-open");
      pendingForm = null;
    }

    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        if (form.dataset.confirmed === "true") return;
        event.preventDefault();
        openModal(form);
      });
    });

    confirmBtn.addEventListener("click", function () {
      if (!pendingForm) return;
      pendingForm.dataset.confirmed = "true";
      pendingForm.requestSubmit ? pendingForm.requestSubmit() : pendingForm.submit();
      closeModal();
    });

    cancelBtns.forEach(function (btn) {
      btn.addEventListener("click", closeModal);
    });
    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeModal();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && modal.classList.contains("is-open")) closeModal();
    });
  }
})();
