/* Shared navigation — include via <script src="nav.js"></script> after the
   <nav class="topnav"> element.  The script replaces the <ul> inside .topnav
   so every page gets the same links in the same order.
   Supports dropdown submenus via the "children" property. */
(function () {
  var isIndex = /index\.html$/.test(location.pathname) || /\/$/.test(location.pathname);
  var prefix = isIndex ? '' : 'index.html';

  var tabs = [
    { href: 'program.html', label: 'Program' },
    { href: 'about.html',   label: 'About', children: [
      { href: 'committee.html', label: 'Committee' },
      { href: 'conduct.html',   label: 'Conduct' },
      { href: 'vetting.html',   label: 'Vetting' },
      { href: 'pledges.html',   label: 'Sponsors' }
    ]},
    { href: 'community.html', label: 'Community', children: [
      { href: 'festival.html',  label: 'Hangout' },
      { href: 'hackathon.html', label: 'Hackathon' }
    ]},
    { href: 'register.html', label: 'Register' }
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
