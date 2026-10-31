(function () {
  var doc = document.documentElement;
  doc.classList.add('js');

  // Header: solid on scroll, hide on scroll down
  var header = document.querySelector('.site-header');
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY;
    header.classList.toggle('scrolled', y > 40);
    if (!document.body.classList.contains('menu-open')) {
      header.classList.toggle('hidden', y > 400 && y > lastY + 4);
      if (y < lastY - 4) header.classList.remove('hidden');
    }
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var burger = document.querySelector('.burger');
  if (burger) {
    burger.addEventListener('click', function () {
      var open = document.body.classList.toggle('menu-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    document.querySelectorAll('.nav a').forEach(function (a) {
      a.addEventListener('click', function () {
        document.body.classList.remove('menu-open');
        document.body.style.overflow = '';
      });
    });
  }

  // Scroll reveal
  var targets = document.querySelectorAll('.rv, .ascent');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add('in'); });
  }

  // Sticky sub-navigation (What we do)
  var subLinks = document.querySelectorAll('.svc-nav a');
  if (subLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    subLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          subLinks.forEach(function (a) { a.classList.remove('active'); });
          if (map[e.target.id]) map[e.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    document.querySelectorAll('.svc').forEach(function (s) { so.observe(s); });
  }

  // Contact form
  var form = document.querySelector('#enquiry');
  if (form) {
    var status = form.querySelector('.form-status');
    var params = new URLSearchParams(location.search);
    if (params.get('sent') === '1') { status.textContent = 'Thank you. Your enquiry has been received and we will be in touch shortly.'; status.className = 'form-status ok'; }
    if (params.get('sent') === '0') { status.textContent = 'Something went wrong. Please try again or write to info@alpen-health.com.'; status.className = 'form-status err'; }

    form.addEventListener('submit', function (ev) {
      if (!window.fetch || !window.FormData) return;
      ev.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      status.textContent = 'Sending…';
      status.className = 'form-status';
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && res.j.ok) {
            form.reset();
            status.textContent = 'Thank you. Your enquiry has been received and we will be in touch shortly.';
            status.className = 'form-status ok';
          } else {
            throw new Error(res.j && res.j.error);
          }
        })
        .catch(function (err) {
          status.textContent = (err && err.message) ? err.message : 'Something went wrong. Please try again or write to info@alpen-health.com.';
          status.className = 'form-status err';
        })
        .then(function () { btn.disabled = false; });
    });
  }
})();
