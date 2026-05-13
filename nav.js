/* Shared navigation — include via <script src="nav.js"></script> after the
   <nav class="topnav"> element.  The script replaces the <ul> inside .topnav
   so every page gets the same links in the same order.
   Supports dropdown submenus via the "children" property. */
(function () {
  var isIndex = /index\.html$/.test(location.pathname) || /\/$/.test(location.pathname);

  /* Detect if we are in a subdirectory (e.g. past/) by checking the
     script's own src attribute — it is always loaded from the root. */
  var scripts = document.querySelectorAll('script[src$="nav.js"]');
  var base = '';
  if (scripts.length) {
    var src = scripts[scripts.length - 1].getAttribute('src');
    var m = src.match(/^((?:\.\.\/)+)/);
    if (m) base = m[1];
  }

  var tabs = [
    { href: base + 'program.html', label: 'Program' },
    { href: base + 'about.html',   label: 'About', children: [
      { href: base + 'about.html',     label: 'History' },
      { href: base + 'committee.html', label: 'Committee' },
      { href: base + 'conduct.html',   label: 'Conduct' },
      { href: base + 'vetting.html',   label: 'Vetting' },
      { href: base + 'conferences.html', label: 'Gatherings' },
      { href: base + 'faq.html',       label: 'FAQ' }
    ]},
    { href: base + 'community.html', label: 'Community', children: [
      { href: base + 'festival.html',  label: 'Hangout' },
      { href: base + 'hackathon.html', label: 'Hackathon' }
    ]},
    { href: base + 'register.html', label: 'Register' }
  ];

  /* Inject dropdown CSS once */
  if (!document.getElementById('nav-dropdown-css')) {
    var style = document.createElement('style');
    style.id = 'nav-dropdown-css';
    style.textContent =
      '.topnav .dropdown { position: relative; }' +
      '.topnav .dropdown-menu { display: none; position: absolute; top: 100%; left: 0;' +
      '  background: rgba(10,36,64,.98); min-width: 160px; padding: .5rem 0;' +
      '  box-shadow: 0 4px 12px rgba(0,0,0,.3); border-radius: 0 0 6px 6px; z-index: 101; }' +
      '.topnav .dropdown:hover .dropdown-menu { display: block; }' +
      '.topnav .dropdown-menu a { display: block; padding: .45rem 1.2rem; color: #c8ddf0;' +
      '  font-size: .85rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em;' +
      '  white-space: nowrap; transition: background .2s, color .2s; }' +
      '.topnav .dropdown-menu a:hover { background: rgba(255,255,255,.08); color: #fff; text-decoration: none; }' +
      /* mobile: show dropdown items inline when menu is open */
      '@media (max-width: 768px) {' +
      '  .topnav .dropdown-menu { position: static; display: none; box-shadow: none;' +
      '    padding: 0 0 0 1rem; min-width: 0; background: transparent; }' +
      '  .topnav .dropdown.open .dropdown-menu { display: block; }' +
      '  .topnav .dropdown-menu a { padding: .3rem 0; }' +
      '}';
    document.head.appendChild(style);
  }

  /* Normalize brand text to "CS 2026" on every page */
  var brand = document.querySelector('.topnav .nav-brand');
  if (brand) {
    var brandSpan = brand.querySelector('span');
    if (brandSpan) brandSpan.textContent = 'CS 2026';
    var brandImg = brand.querySelector('img');
    if (brandImg) brandImg.alt = 'CS Logo';
  }

  var ul = document.querySelector('.topnav ul');
  if (!ul) return;
  ul.innerHTML = '';

  /* Home link — on all pages for consistent navigation */
  var li = document.createElement('li');
  li.innerHTML = '<a href="' + base + 'index.html">Home</a>';
  ul.appendChild(li);

  tabs.forEach(function (t) {
    var li = document.createElement('li');
    if (t.children) {
      li.className = 'dropdown';
      var link = '<a href="' + t.href + '">' + t.label + '</a>';
      var sub = '<div class="dropdown-menu">';
      t.children.forEach(function (c) {
        sub += '<a href="' + c.href + '">' + c.label + '</a>';
      });
      sub += '</div>';
      li.innerHTML = link + sub;
      /* mobile: tap parent toggles submenu */
      li.querySelector('a').addEventListener('click', function (e) {
        if (window.innerWidth <= 768) {
          e.preventDefault();
          li.classList.toggle('open');
        }
      });
    } else {
      li.innerHTML = '<a href="' + t.href + '">' + t.label + '</a>';
    }
    ul.appendChild(li);
  });

  /* hamburger close on click (but not parent dropdown links on mobile) */
  ul.querySelectorAll('.dropdown-menu a, li:not(.dropdown) > a').forEach(function (a) {
    a.addEventListener('click', function () {
      ul.classList.remove('open');
    });
  });
})();
