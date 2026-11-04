/* Shamikh Al-Aofiry portfolio: navigation state, mobile menu and scroll reveal.
   English-only site. Every feature degrades to plain, visible HTML without JavaScript. */
(() => {
  'use strict';

  // Must match the phone media query in style.css.
  const MOBILE_QUERY = '(max-width: 47.99rem)';
  const reducedMotion = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : null;

  function onMediaChange(query, handler) {
    if (!query) return;
    if (typeof query.addEventListener === 'function') query.addEventListener('change', handler);
    else if (typeof query.addListener === 'function') query.addListener(handler);
  }

  // Keep regular fragment links intact so native history, focus and URLs work.
  function initializeNavigation() {
    const navigation = document.querySelector('.site-nav');
    const header = document.querySelector('[data-site-header]');
    if (!navigation) return;
    const links = Array.from(navigation.querySelectorAll('a[href^="#"]'));
    const targets = links.map((link) => {
      const id = link.getAttribute('href').slice(1);
      const section = id ? document.getElementById(id) : null;
      return section ? { link, section } : null;
    }).filter(Boolean);

    let scheduled = false;
    function update() {
      scheduled = false;
      if (header) header.toggleAttribute('data-scrolled', window.scrollY > 8);
      if (!targets.length) return;
      // The last section to cross the reading line is current; none while in the hero.
      const readingLine = Math.min(window.innerHeight * 0.35, 240);
      let current = null;
      targets.forEach((item) => {
        if (item.section.getBoundingClientRect().top <= readingLine) current = item.link;
      });
      // At the very bottom, the final section is current even if it is short.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
        current = targets[targets.length - 1].link;
      }
      links.forEach((link) => {
        if (link === current) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }
    function schedule() {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(update);
    }
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
    window.addEventListener('hashchange', schedule);
    update();
  }

  // A plain, visible navigation remains available if JavaScript does not run.
  function initializeMobileMenu() {
    const button = document.querySelector('[data-menu-toggle]');
    const navigation = document.getElementById('main-navigation');
    if (!button || !navigation || typeof window.matchMedia !== 'function') return;
    const label = button.querySelector('[data-menu-label]');
    const header = navigation.closest('.site-header');
    const mobile = window.matchMedia(MOBILE_QUERY);
    // Dropdown styling applies only once JavaScript controls the menu.
    if (header) header.setAttribute('data-menu-ready', '');
    let expanded = false;

    function render() {
      const isOpen = mobile.matches && expanded;
      button.hidden = !mobile.matches;
      button.setAttribute('aria-expanded', String(isOpen));
      if (label) label.textContent = isOpen ? 'Close' : 'Menu';
      navigation.toggleAttribute('inert', mobile.matches && !isOpen);
      if (header) header.toggleAttribute('data-menu-open', isOpen);
      if (mobile.matches && !isOpen) navigation.setAttribute('data-menu-collapsed', 'true');
      else navigation.removeAttribute('data-menu-collapsed');
    }
    function close() { expanded = false; render(); }
    button.addEventListener('click', () => { expanded = !expanded; render(); });
    navigation.addEventListener('click', (event) => {
      if (mobile.matches && event.target.closest('a[href]')) close();
    });
    // Tapping outside the open menu closes it.
    document.addEventListener('click', (event) => {
      if (!mobile.matches || !expanded) return;
      if (!navigation.contains(event.target) && !button.contains(event.target)) close();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && mobile.matches && expanded) { close(); button.focus(); }
    });
    onMediaChange(mobile, close);
    render();
  }

  // Native anchor scrolling retains browser history and fragment navigation.
  function initializeScrollPreference() {
    function update() {
      document.documentElement.style.scrollBehavior = reducedMotion && reducedMotion.matches ? 'auto' : 'smooth';
    }
    update();
    onMediaChange(reducedMotion, update);
  }

  // Cards fade in once as they enter the viewport. Content stays visible without support.
  function initializeReveal() {
    const items = Array.from(document.querySelectorAll('.reveal'));
    if (!items.length) return;
    const showAll = () => items.forEach((item) => item.classList.add('is-visible'));
    if (!('IntersectionObserver' in window) || (reducedMotion && reducedMotion.matches)) { showAll(); return; }
    document.documentElement.classList.add('reveal-ready');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
    items.forEach((item) => observer.observe(item));
    onMediaChange(reducedMotion, () => { if (reducedMotion.matches) showAll(); });
  }

  function initialize() {
    initializeNavigation();
    initializeScrollPreference();
    initializeMobileMenu();
    initializeReveal();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
  else initialize();
})();
