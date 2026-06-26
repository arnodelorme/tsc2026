/* Shared footer — include via <script src="footer.js"></script> after the
   <footer> element.  The script replaces the footer's innerHTML so every
   page gets the same content.  Asset paths are resolved relative to this
   script so pages in subdirectories (e.g. abstracts_html/) work too. */
(function () {
  var footer = document.querySelector('footer');
  if (!footer) return;

  /* Derive base path from this script's own src (mirrors nav.js). */
  var base = '';
  var scripts = document.querySelectorAll('script[src$="footer.js"]');
  if (scripts.length) {
    var src = scripts[scripts.length - 1].getAttribute('src') || '';
    var m = src.match(/(.*\/)footer\.js/);
    if (m) base = m[1];
  }

  /* Inject shared footer styling once so every page renders the same
     deep-blue footer, overriding per-page CSS and theme.css !important rules. */
  if (!document.getElementById('shared-footer-style')) {
    var st = document.createElement('style');
    st.id = 'shared-footer-style';
    st.textContent =
      'footer{background:#0C234B!important;color:rgba(255,255,255,.7)!important;' +
      'padding:2.5rem 2rem!important;text-align:center!important;font-size:.85rem!important;}' +
      'footer a{color:#8fb7d4!important;}' +
      'footer a:hover{color:#fff!important;}' +
      'footer .foot-brand{color:#fff!important;font-weight:700!important;margin-bottom:.35rem!important;}' +
      'footer .foot-org span{color:rgba(255,255,255,.6)!important;}';
    document.head.appendChild(st);
  }

  footer.innerHTML =
    '<div class="foot-brand">The Science of Consciousness 2026</div>' +
    '<div class="foot-org" style="display:flex;flex-direction:column;align-items:center;gap:.4rem;margin:.6rem 0 .8rem;">' +
    '<span style="font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;opacity:.7;">Organized by</span>' +
    '<a href="https://ucsd.edu/" target="_blank" rel="noopener" style="display:inline-block;">' +
    '<img src="' + base + 'sponsors/ucsd-logo-white.png" alt="UC San Diego" style="height:34px;width:auto;opacity:.9;">' +
    '</a>' +
    '</div>' +
    '<p>&copy; 2026 TSC Conference. All rights reserved.</p>' +
    '<p style="margin-top:.3rem;">' +
    'Contact: <a href="mailto:info@tsc2026.org">info@tsc2026.org</a>' +
    '</p>';
})();
