(function () {
  "use strict";

  function on(el, event, handler) {
    if (el) el.addEventListener(event, handler);
  }

  // Mobile navigation
  var navToggle = document.getElementById("navToggle");
  var siteNav = document.getElementById("siteNav");
  on(navToggle, "click", function () {
    var open = siteNav.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
  });

  // User dropdown
  var userMenuBtn = document.getElementById("userMenuBtn");
  var userMenu = document.getElementById("userMenu");
  on(userMenuBtn, "click", function (event) {
    event.stopPropagation();
    var open = userMenu.classList.toggle("open");
    userMenuBtn.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("click", function (event) {
    if (userMenu && !userMenu.contains(event.target)) userMenu.classList.remove("open");
  });

  // Dashboard sidebar toggle
  var dashToggle = document.getElementById("dashToggle");
  on(dashToggle, "click", function () {
    var side = document.getElementById("dashSide");
    if (side) side.classList.toggle("open");
  });

  // Dismissible alerts
  document.querySelectorAll(".alert-close").forEach(function (btn) {
    btn.addEventListener("click", function () {
      btn.closest(".alert").remove();
    });
  });
  window.setTimeout(function () {
    document.querySelectorAll("#messages .alert").forEach(function (alert) {
      alert.style.transition = "opacity .4s";
      alert.style.opacity = "0";
      window.setTimeout(function () { alert.remove(); }, 400);
    });
  }, 6000);

  // Confirm destructive actions
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  // Live image preview for file inputs
  document.querySelectorAll("input[type=file][data-preview]").forEach(function (input) {
    input.addEventListener("change", function () {
      var target = document.querySelector(input.dataset.preview);
      if (!target || !input.files || !input.files[0]) return;
      var reader = new FileReader();
      reader.onload = function (e) {
        target.src = e.target.result;
        target.style.display = "block";
      };
      reader.readAsDataURL(input.files[0]);
    });
  });

  // Quantity steppers on product pages
  document.querySelectorAll("[data-qty-step]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = document.querySelector(btn.dataset.qtyTarget);
      if (!input) return;
      var next = parseInt(input.value || "1", 10) + parseInt(btn.dataset.qtyStep, 10);
      var max = parseInt(input.max || "999", 10);
      input.value = Math.min(Math.max(next, 1), max);
    });
  });
})();
