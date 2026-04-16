/* Shared navigation — include via <script src="nav.js"></script> after the
   <nav class="topnav"> element.  The script replaces the <ul> inside .topnav
   so every page gets the same links in the same order. */
(function () {
  var isIndex = /index\.html$/.test(location.pathname) || /\/$/.test(location.pathname);
  var prefix = isIndex ? '' : 'index.html';

  var tabs = [
    [prefix || '#about',        'About',    'about.html'],
    [prefix + '#speakers',      'Speakers', null],
    ['program.html',            'Program',  null],
    [prefix + '#venue',         'Venue',    null],
    ['conduct.html',            'Conduct',  null],
    ['vetting.html',            'Vetting',  null],
    ['pledges.html',            'Sponsors', null],
    ['festival.html',           'Hangout',  null]
  ];

  /* On index.html the About link points to about.html (not #about) */
  if (isIndex) { tabs[0][0] = 'about.html'; }

  var ul = document.querySelector('.topnav ul');
  if (!ul) return;
  ul.innerHTML = '';

  /* Home link — only on non-index pages */
  if (!isIndex) {
    var li = document.createElement('li');
    li.innerHTML = '<a href="index.html">Home</a>';
    ul.appendChild(li);
  }

  tabs.forEach(function (t) {
    var li = document.createElement('li');
    li.innerHTML = '<a href="' + t[0] + '">' + t[1] + '</a>';
    ul.appendChild(li);
  });

  /* hamburger close on click */
  ul.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      ul.classList.remove('open');
    });
  });
})();
