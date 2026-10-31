(function () {
  var doc = document.documentElement;
  var body = document.body;
  doc.classList.add('js');

  // Header: solid on scroll, hide on scroll down
  var header = document.querySelector('.site-header');
  var toTop = document.querySelector('.to-top');
  var lastY = 0;
  function onScroll() {
    if (body.classList.contains('menu-open')) return;
    var y = window.scrollY;
    header.classList.toggle('scrolled', y > 40);
    if (!body.classList.contains('menu-open')) {
      if (y > 600 && y > lastY + 4) header.classList.add('hidden');
      if (y < lastY - 4 || y <= 600) header.classList.remove('hidden');
      body.classList.toggle('hdr-hidden', header.classList.contains('hidden'));
    }
    if (toTop) toTop.classList.toggle('show', y > 1200);
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // Mobile menu
  var burger = document.querySelector('.burger');
  var lockedY = 0;
  function openMenu() {
    lockedY = window.scrollY;
    header.classList.remove('hidden');
    body.classList.add('menu-open');
    body.style.position = 'fixed';
    body.style.top = -lockedY + 'px';
    body.style.left = body.style.right = '0';
    burger.setAttribute('aria-expanded', 'true');
  }
  function closeMenu() {
    if (!body.classList.contains('menu-open')) return;
    body.classList.remove('menu-open');
    body.style.position = body.style.top = body.style.left = body.style.right = '';
    window.scrollTo(0, lockedY);
    if (burger) burger.setAttribute('aria-expanded', 'false');
  }
  if (burger) {
    burger.addEventListener('click', function () {
      if (body.classList.contains('menu-open')) closeMenu(); else openMenu();
    });
    document.querySelectorAll('.nav a').forEach(function (a) { a.addEventListener('click', closeMenu); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
    window.addEventListener('resize', function () { if (window.innerWidth > 1020) closeMenu(); });
  }

  // Scroll reveal
  var targets = document.querySelectorAll('.rv, .ascent');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -5% 0px', threshold: 0.05 });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add('in'); });
  }

  // Capability navigation (What we do): desktop side nav + mobile chips
  var subLinks = document.querySelectorAll('.svc-nav a, .svc-chips a');
  if (subLinks.length && 'IntersectionObserver' in window) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        subLinks.forEach(function (a) {
          var on = a.getAttribute('href') === '#' + e.target.id;
          a.classList.toggle('active', on);
          if (on && a.parentNode.classList.contains('svc-chips')) {
            a.parentNode.scrollTo({ left: a.offsetLeft - 20, behavior: 'smooth' });
          }
        });
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    document.querySelectorAll('.svc').forEach(function (s) { so.observe(s); });
  }

  // Contact form
  var form = document.querySelector('#enquiry');
  if (!form) return;

  var AREAS = {
    'immunology': 'Immunology, Plasma & Rare Diseases',
    'womens-health': 'Women’s Health, Fertility & Reproductive Medicine',
    'ophthalmology': 'Ophthalmology & Vision Care',
    'oncology': 'Oncology & Supportive Care',
    'neurology': 'Neurology & Specialty Therapies',
    'hospital': 'Anaesthesia, Critical Care & Hospital Solutions',
    'cardiology': 'Interventional Cardiology & Cardiovascular Solutions',
    'consumer-health': 'Consumer Health, Nutrition & Wellness'
  };
  var params = new URLSearchParams(location.search);
  function preselect(select, value) {
    if (!select || !value) return;
    for (var i = 0; i < select.options.length; i++) {
      if (select.options[i].text === value) { select.selectedIndex = i; return; }
    }
  }
  preselect(form.elements.area, AREAS[params.get('area')]);
  var m = params.get('market');
  if (m) preselect(form.elements.market, m.charAt(0).toUpperCase() + m.slice(1));

  var MESSAGES = {
    valueMissing: 'This field is required.',
    typeMismatch: 'Please enter a valid email address.'
  };
  function errorFor(el) {
    var id = el.id + '-err';
    var p = document.getElementById(id);
    if (!p) {
      p = document.createElement('p');
      p.className = 'field-error';
      p.id = id;
      (el.closest('.field') || el.closest('.consent')).appendChild(p);
      el.setAttribute('aria-describedby', id);
    }
    return p;
  }
  function check(el) {
    if (!el.willValidate || el.type === 'checkbox') return el.checkValidity();
    var ok = el.checkValidity();
    var msg = ok ? '' : (el.validity.valueMissing ? MESSAGES.valueMissing : MESSAGES.typeMismatch);
    el.setAttribute('aria-invalid', ok ? 'false' : 'true');
    errorFor(el).textContent = msg;
    return ok;
  }
  form.querySelectorAll('input[required], select[required], textarea[required]').forEach(function (el) {
    el.addEventListener('blur', function () { if (el.value) check(el); });
    el.addEventListener('input', function () { if (el.getAttribute('aria-invalid') === 'true') check(el); });
  });

  var status = form.querySelector('.form-status');

  function summary() {
    var f = form.elements;
    return [
      'Company: ' + f.company.value,
      'Name: ' + f.name.value,
      'Position: ' + f.position.value,
      'Email: ' + f.email.value,
      'Market: ' + f.market.value,
      'Therapeutic area: ' + f.area.value,
      'Portfolio / opportunity: ' + f.portfolio.value,
      '',
      f.message.value
    ].join('\n');
  }
  function mailtoHref() {
    return 'mailto:info@alpen-health.com?subject=' +
      encodeURIComponent('Partnership enquiry: ' + form.elements.company.value) +
      '&body=' + encodeURIComponent(summary());
  }
  function done(sent) {
    var first = form.elements.name.value.split(' ')[0];
    var box = document.createElement('div');
    box.className = 'form-done';
    box.setAttribute('tabindex', '-1');
    box.innerHTML = sent
      ? '<div class="form-done__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>' +
        '<h3>Thank you' + (first ? ', ' + first.replace(/[<>&"]/g, '') : '') + '.</h3>' +
        '<p>Your enquiry has been received. A member of our team will reply from info@alpen-health.com to arrange a first conversation.</p>' +
        '<div class="btns"><a class="btn btn--ghost" href="index.html">Back to Home</a></div>'
      : '<div class="form-done__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18v12H3z"/><path d="M3 7l9 6 9-6"/></svg></div>' +
        '<h3>One last step.</h3>' +
        '<p>Our online form could not send your message from here. Your enquiry is ready: open it in your email application and press send.</p>' +
        '<div class="btns"><a class="btn" href="' + mailtoHref() + '">Send by email</a><button class="btn btn--ghost" type="button">Edit enquiry</button></div>';
    form.hidden = true;
    form.parentNode.insertBefore(box, form.nextSibling);
    box.focus();
    var edit = box.querySelector('button');
    if (edit) edit.addEventListener('click', function () { box.remove(); form.hidden = false; });
  }

  if (params.get('sent') === '1') done(true);

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    var firstBad = null;
    fields.forEach(function (el) { if (!check(el) && !firstBad) firstBad = el; });
    var consent = form.elements.consent;
    if (!consent.checked) {
      errorFor(consent).textContent = 'Please confirm you agree to the privacy notice.';
      if (!firstBad) firstBad = consent;
    } else if (document.getElementById(consent.id + '-err')) {
      errorFor(consent).textContent = '';
    }
    if (firstBad) { firstBad.focus(); status.textContent = 'Please check the highlighted fields.'; status.className = 'form-status err'; return; }

    if (!window.fetch) { form.submit(); return; }
    var btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    status.textContent = 'Sending…';
    status.className = 'form-status';
    fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
      .then(function (r) {
        var ct = r.headers.get('content-type') || '';
        if (ct.indexOf('application/json') === -1) throw new Error('unavailable');
        return r.json().then(function (j) { return { ok: r.ok && j.ok, j: j }; });
      })
      .then(function (res) {
        if (res.ok) { done(true); return; }
        status.textContent = res.j.error || 'Something went wrong. Please try again.';
        status.className = 'form-status err';
      })
      .catch(function () { status.textContent = ''; done(false); })
      .then(function () { btn.disabled = false; });
  });
})();

// Mobile swipe rows: progress bar + counter under each .snap row
(function () {
  document.querySelectorAll('.snap').forEach(function (row) {
    var items = Array.prototype.filter.call(row.children, function (c) { return !c.classList.contains('eq-op'); });
    var bar = document.createElement('div');
    bar.className = 'snap-bar';
    bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML = '<i></i>';
    var hint = document.createElement('div');
    hint.className = 'snap-hint';
    hint.setAttribute('aria-hidden', 'true');
    hint.innerHTML = '<span class="snap-count"></span><span>Swipe &rarr;</span>';
    row.parentNode.insertBefore(hint, row.nextSibling);
    row.parentNode.insertBefore(bar, row.nextSibling);
    var thumb = bar.firstChild, count = hint.firstChild;
    function update() {
      if (getComputedStyle(row).overflowX !== 'auto') { bar.style.display = hint.style.display = 'none'; return; }
      bar.style.display = hint.style.display = '';
      var max = row.scrollWidth - row.clientWidth;
      var ratio = row.clientWidth / row.scrollWidth;
      var p = max > 0 ? row.scrollLeft / max : 0;
      thumb.style.width = (ratio * 100) + '%';
      thumb.style.transform = 'translateX(' + (p * (1 / ratio - 1) * 100) + '%)';
      var idx = Math.min(items.length, Math.round(p * (items.length - 1)) + 1);
      count.textContent = String(idx).padStart(2, '0') + ' / ' + String(items.length).padStart(2, '0');
    }
    row.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });
})();

// Coral cursor over the maps and the footer logo (mouse only)
(function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var zones = document.querySelectorAll('.mcard, .mdetail__img, .phero:has(.map), .site-footer .logo');
  if (!zones.length) return;
  var c = document.createElement('div');
  c.className = 'cursor';
  c.setAttribute('aria-hidden', 'true');
  document.body.appendChild(c);
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var x = 0, y = 0, cx = 0, cy = 0, raf = 0;
  function loop() {
    cx += (x - cx) * (still ? 1 : 0.22);
    cy += (y - cy) * (still ? 1 : 0.22);
    c.style.transform = 'translate(' + cx + 'px,' + cy + 'px)';
    raf = Math.abs(x - cx) + Math.abs(y - cy) > 0.3 ? requestAnimationFrame(loop) : 0;
  }
  document.addEventListener('mousemove', function (e) {
    x = e.clientX; y = e.clientY;
    if (!raf) raf = requestAnimationFrame(loop);
  }, { passive: true });
  zones.forEach(function (z) {
    z.addEventListener('mouseenter', function (e) { cx = x = e.clientX; cy = y = e.clientY; loop(); c.classList.add('on'); });
    z.addEventListener('mouseleave', function () { c.classList.remove('on'); });
  });
  document.addEventListener('mousedown', function () { c.classList.add('down'); });
  document.addEventListener('mouseup', function () { c.classList.remove('down'); });
})();
