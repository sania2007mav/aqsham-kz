/* UI behaviour only. Nothing here hides content.
   Sections stay visible with or without this script. */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const header = document.querySelector('.header');
  const mobileTop = document.querySelector('.mobile-top');
  const onScroll = () => {
    const shrunk = window.scrollY > 24;
    header?.classList.toggle('is-shrunk', shrunk);
    mobileTop?.classList.toggle('is-shrunk', shrunk);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const burger = document.querySelector('.js-burger');
  const openBurger = () => {
    if (!burger) return;
    burger.hidden = false;
    requestAnimationFrame(() => burger.classList.add('is-open'));
  };
  const closeBurger = () => {
    if (!burger) return;
    burger.classList.remove('is-open');
    const hide = () => { burger.hidden = true; };
    if (reduce) hide();
    else burger.addEventListener('transitionend', hide, { once: true });
  };
  document.querySelector('.js-burger-open')?.addEventListener('click', openBurger);
  document.querySelector('.js-burger-close')?.addEventListener('click', closeBurger);

  const catalog = document.querySelector('.js-catalog-menu');
  const catalogBtn = document.querySelector('.js-catalog-trigger');
  catalogBtn?.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    const open = catalog.classList.toggle('is-open');
    catalogBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  const langList = document.querySelector('.js-lang-list');
  const langToggle = document.querySelector('.js-lang-toggle');
  langToggle?.addEventListener('click', (event) => {
    event.stopPropagation();
    const willOpen = langList.hasAttribute('hidden');
    langList.toggleAttribute('hidden', !willOpen);
    langToggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  });

  document.addEventListener('click', (event) => {
    if (catalog && !catalog.contains(event.target)) {
      catalog.classList.remove('is-open');
      catalogBtn?.setAttribute('aria-expanded', 'false');
    }
    if (langList && !event.target.closest('.js-lang')) {
      langList.hidden = true;
      langToggle?.setAttribute('aria-expanded', 'false');
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    closeBurger();
    catalog?.classList.remove('is-open');
    if (langList) langList.hidden = true;
  });

  document.querySelectorAll('.lang__item, .burger__lang-btn').forEach((item) => {
    item.addEventListener('click', () => {
      const code = item.querySelector('b')?.textContent?.trim();
      if (!code) return;
      document.querySelectorAll('.lang__code').forEach((el) => { el.textContent = code; });
      document.querySelectorAll('.lang__item').forEach((el) => {
        el.setAttribute('aria-selected', el === item ? 'true' : 'false');
      });
      document.querySelectorAll('.burger__lang-btn').forEach((el) => {
        el.setAttribute('aria-pressed', el === item ? 'true' : 'false');
      });
      if (langList) langList.hidden = true;
    });
  });

  document.querySelector('.js-tab-search')?.addEventListener('click', () => {
    const search = document.querySelector('.search-mobile');
    search?.classList.toggle('is-open');
    if (search?.classList.contains('is-open')) search.querySelector('input')?.focus();
  });

  const wireScroll = (button, selector, direction) => {
    button?.addEventListener('click', () => {
      document.querySelector(selector)?.scrollBy({
        left: direction * 280,
        behavior: reduce ? 'auto' : 'smooth',
      });
    });
  };
  wireScroll(document.querySelector('.js-brands-prev'), '.brands__viewport', -1);
  wireScroll(document.querySelector('.js-brands-next'), '.brands__viewport', 1);
  wireScroll(document.querySelector('.js-strip-prev'), '.js-strip-track', -1);
  wireScroll(document.querySelector('.js-strip-next'), '.js-strip-track', 1);

  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"], button:not([type])');
      if (!button || !form.classList.contains('js-request-form') || button.dataset.liqDone) return;
      const previous = button.textContent;
      button.dataset.liqDone = '1';
      button.textContent = 'Заявка отправлена';
      setTimeout(() => {
        button.textContent = previous;
        delete button.dataset.liqDone;
      }, 1600);
    });
  });
})();
