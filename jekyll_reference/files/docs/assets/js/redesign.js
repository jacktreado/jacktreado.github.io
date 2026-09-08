/* redesign.js — off-canvas nav, shrink-on-scroll, hover-to-play thumbnails.
   No dependencies. Safe to load with `defer`. */
(function () {
  "use strict";

  /* ---------------- off-canvas nav ---------------- */
  var drawer = document.querySelector("[data-nav-drawer]");
  var scrim = document.querySelector("[data-nav-scrim]");
  var toggle = document.querySelector("[data-nav-toggle]");
  var closeBtn = document.querySelector("[data-nav-close]");
  var lastFocus = null;

  function setNav(open) {
    if (!drawer) return;
    drawer.setAttribute("data-open", open ? "true" : "false");
    drawer.setAttribute("aria-hidden", open ? "false" : "true");
    if (scrim) scrim.setAttribute("data-open", open ? "true" : "false");
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("jt-nav-open", open);
    if (open) {
      lastFocus = document.activeElement;
      var first = drawer.querySelector("a, button");
      if (first) first.focus();
    } else if (lastFocus) {
      lastFocus.focus();
    }
  }

  if (toggle) toggle.addEventListener("click", function () { setNav(true); });
  if (closeBtn) closeBtn.addEventListener("click", function () { setNav(false); });
  if (scrim) scrim.addEventListener("click", function () { setNav(false); });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && drawer && drawer.getAttribute("data-open") === "true") setNav(false);
  });

  // keep focus inside the open drawer
  document.addEventListener("focusin", function (e) {
    if (!drawer || drawer.getAttribute("data-open") !== "true") return;
    if (!drawer.contains(e.target)) {
      var first = drawer.querySelector("a, button");
      if (first) first.focus();
    }
  });

  // close after an in-page jump
  if (drawer) {
    drawer.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
  }

  // preview convenience: #nav-open opens the drawer on load
  if (location.hash === "#nav-open") setNav(true);

  /* ---------------- shrink on scroll ---------------- */
  var nav = document.querySelector("[data-nav]");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("is-shrunk", window.scrollY > 40);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------------- hover / focus to play thumbnails ---------------- */
  var canHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!canHover || reduced) return;

  document.querySelectorAll("[data-thumb]").forEach(function (card) {
    var video = card.querySelector("video");
    if (!video) return;

    var play = function () {
      if (video.preload === "none") video.preload = "auto";
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    };
    var stop = function () {
      video.pause();
      try { video.currentTime = 0; } catch (err) {}
    };

    card.addEventListener("pointerenter", play);
    card.addEventListener("pointerleave", stop);
    card.addEventListener("focus", play);
    card.addEventListener("blur", stop);
  });
})();
