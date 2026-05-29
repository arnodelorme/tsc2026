/* Shared footer — include via <script src="footer.js"></script> after the
   <footer> element.  The script replaces the footer's innerHTML so every
   page gets the same content. */
(function () {
  var footer = document.querySelector('footer');
  if (!footer) return;
  footer.innerHTML =
    '<div class="foot-brand">The Science of Consciousness 2026</div>' +
    '<p>&copy; 2026 CS Conference. All rights reserved.</p>' +
    '<p style="margin-top:.3rem;">' +
    'Contact: <a href="mailto:info@cs2026.org">info@cs2026.org</a>' +
    '</p>';
})();
