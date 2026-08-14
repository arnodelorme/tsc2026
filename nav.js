/* Shared navigation — include via <script src="nav.js"></script> after the
   <nav class="topnav"> element.  The script replaces the <ul> inside .topnav
   so every page gets the same links in the same order.
   Supports dropdown submenus via the "children" property. */
(function () {
  var isIndex = /index\.html$/.test(location.pathname) || /\/$/.test(location.pathname);

  /* Detect if we are in a subdirectory (e.g. past/) by checking the
     script's own src attribute — it is always loaded from the root. */
  var scripts = document.querySelectorAll('script[src*="nav.js"]');
  var base = '';
  if (scripts.length) {
    var src = scripts[scripts.length - 1].getAttribute('src');
    var m = src.match(/^((?:\.\.\/)+)/);
    if (m) base = m[1];
  }

  var tabs = [
    { href: base + 'program.html', label: 'Program', children: [
      { href: base + 'program.html#speakers', label: 'Speakers' },
      { href: base + 'program.html#at-a-glance', label: 'Program at a Glance' },
      { href: base + 'program_details.html', label: 'Program (Detailed)' },
      { href: base + 'workshops.html', label: 'Workshops' },
      { href: base + 'concurrent.html', label: 'Concurrent Presentations' },
      { href: base + 'posters.html', label: 'Posters' }
    ]},
    { href: base + 'about.html',   label: 'About', children: [
      { href: base + 'about.html',     label: 'History' },
      { href: base + 'committee.html', label: 'Committee' },
      { href: base + 'conduct.html',   label: 'Conduct' },
      { href: base + 'vetting.html',   label: 'Vetting' },
      { href: base + 'faq.html',       label: 'FAQ' }
    ]},
    { href: base + 'community.html', label: 'Community', children: [
      { href: base + 'festival.html',  label: 'Hangout' },
      { href: base + 'experientials.html', label: 'Experiential' },
      { href: base + 'hackathon.html', label: 'Hackathon' }
    ]},
    { href: base + 'register.html', label: 'Register' }
  ];

  /* IONS members: the hidden IONS page (ions.html) sets the `tsc_ions` cookie
     when first visited. Once set, surface the IONS tab right after Home on
     every page. Without the cookie the tab stays hidden. */
  if (/(?:^|;\s*)tsc_ions=1(?:\s*;|\s*$)/.test(document.cookie)) {
    tabs.unshift({ href: base + 'ions.html', label: 'IONS' });
  }

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
      /* inline search: magnifier expands an edit box at the right of the menu */
      '.topnav .nav-search { display: flex; align-items: center; gap: .4rem; }' +
      '.topnav .nav-search svg { width: 17px; height: 17px; stroke: #c8ddf0;' +
      '  cursor: pointer; vertical-align: middle; transition: stroke .2s; }' +
      '.topnav .nav-search svg:hover { stroke: #fff; }' +
      '.topnav .nav-search input { width: 0; padding: 0; border: 0; opacity: 0;' +
      '  background: rgba(255,255,255,.12); color: #fff; border-radius: 6px;' +
      '  font-size: .85rem; font-family: inherit; outline: none;' +
      '  transition: width .25s, padding .25s, opacity .2s; }' +
      '.topnav .nav-search input::placeholder { color: #9fc3d8; }' +
      '.topnav .nav-search.open input { width: 150px; padding: .3rem .6rem; opacity: 1; }' +
      /* mobile: show dropdown items inline when menu is open */
      '@media (max-width: 768px) {' +
      '  .topnav .dropdown-menu { position: static; display: none; box-shadow: none;' +
      '    padding: 0 0 0 1rem; min-width: 0; background: transparent; }' +
      '  .topnav .dropdown.open .dropdown-menu { display: block; }' +
      '  .topnav .dropdown-menu a { padding: .3rem 0; }' +
      '  .topnav .nav-search.open input { width: 100%; }' +
      '}';
    document.head.appendChild(style);
  }

  /* Normalize brand text to "TSC 2026" on every page */
  var brand = document.querySelector('.topnav .nav-brand');
  if (brand) {
    var brandSpan = brand.querySelector('span');
    if (brandSpan) brandSpan.textContent = 'TSC 2026';
    var brandImg = brand.querySelector('img');
    if (brandImg) brandImg.alt = 'TSC Logo';
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

  /* Search: magnifier icon that expands an edit box, submits to search.html */
  var searchLi = document.createElement('li');
  searchLi.className = 'nav-search';
  searchLi.innerHTML =
    '<input type="search" placeholder="Search…" aria-label="Search the site">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="2.4" stroke-linecap="round" ' +
    'role="button" aria-label="Search"><circle cx="10.5" cy="10.5" r="6.5"/>' +
    '<line x1="15.5" y1="15.5" x2="21" y2="21"/></svg>';
  var searchInput = searchLi.querySelector('input');
  var searchIcon = searchLi.querySelector('svg');
  function submitSearch() {
    var q = searchInput.value.trim();
    location.href = base + 'search.html' + (q ? '?q=' + encodeURIComponent(q) : '');
  }
  searchIcon.addEventListener('click', function () {
    if (!searchLi.classList.contains('open')) {
      searchLi.classList.add('open');
      searchInput.focus();
    } else if (searchInput.value.trim()) {
      submitSearch();
    } else {
      searchLi.classList.remove('open');
    }
  });
  searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') submitSearch();
    if (e.key === 'Escape') { searchInput.value = ''; searchLi.classList.remove('open'); }
  });
  ul.appendChild(searchLi);

  /* Mark the link matching the current page as active */
  var currentFile = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  ul.querySelectorAll('a').forEach(function (a) {
    var href = (a.getAttribute('href') || '').split('/').pop().toLowerCase();
    if (href && href === currentFile) a.classList.add('active');
  });

  tabs.forEach(function (t) {
    if (!t.children) return;
    var parentLink = ul.querySelector('.dropdown > a[href="' + t.href + '"]');
    if (!parentLink) return;
    var active = ((t.href.split('/').pop() || '').split('#')[0].toLowerCase() === currentFile);
    if (!active) {
      t.children.some(function (c) {
        if (!c.href) return false;
        var childFile = ((c.href.split('/').pop() || '').split('#')[0]).toLowerCase();
        if (childFile && childFile === currentFile) {
          active = true;
          return true;
        }
        return false;
      });
    }
    if (active) parentLink.classList.add('active');
  });

  /* hamburger close on click (but not parent dropdown links on mobile) */
  ul.querySelectorAll('.dropdown-menu a, li:not(.dropdown) > a').forEach(function (a) {
    a.addEventListener('click', function () {
      ul.classList.remove('open');
    });
  });
})();
