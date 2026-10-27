/* Liquid glass motion: scroll reveal, shrinking header, card light, counters.
   Content and numbers stay the same — only how they appear changes. */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const root = document.documentElement;

  const revealNodes = [
    ...document.querySelectorAll(
      '.hero-sliders, .cats__title, .cats__card, .brands, .project-card, .home-news, .news-card, .footer-cta, .footer-main, .footer-copyright'
    ),
  ];

  revealNodes.forEach((el, i) => {
    el.classList.add('liq-reveal');
    el.style.setProperty('--d', `${(i % 8) * 50}ms`);
  });

  const show = (el) => el.classList.add('is-in');

  if (reduce || !('IntersectionObserver' in window)) {
    revealNodes.forEach(show);
  } else {
    root.classList.add('liq-js');
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          show(entry.target);
          countInside(entry.target);
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.01, rootMargin: '0px 0px 40px 0px' }
    );
    revealNodes.forEach((el) => io.observe(el));
  }

  const header = document.querySelector('.header');
  const mobileTop = document.querySelector('.mobile-top');
  const onScroll = () => {
    const shrunk = window.scrollY > 18;
    header?.classList.toggle('is-shrunk', shrunk);
    mobileTop?.classList.toggle('is-shrunk', shrunk);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  if (!reduce && fine) {
    const cards = document.querySelectorAll('.cats__card, .project-card, .news-card, .brand-card');
    cards.forEach((card) => {
      card.addEventListener('mousemove', (event) => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;
        card.style.setProperty('--mx', `${(x * 100).toFixed(1)}%`);
        card.style.setProperty('--my', `${(y * 100).toFixed(1)}%`);
        const rx = (0.5 - y) * 7;
        const ry = (x - 0.5) * 8;
        card.style.transform = `perspective(900px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg) translateY(-3px)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  }

  function formatCount(value, pad, money) {
    const rounded = Math.round(value);
    if (money) {
      return rounded.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₸';
    }
    return pad ? String(rounded).padStart(pad, '0') : String(rounded);
  }

  function runCount(el) {
    if (el.dataset.liqCounted) return;
    const raw = el.textContent.trim();
    const digits = raw.replace(/[^\d]/g, '');
    if (!digits) return;
    const target = Number(digits);
    if (!Number.isFinite(target)) return;
    el.dataset.liqCounted = '1';
    const money = raw.includes('₸');
    const pad = !money && digits.length <= 2 ? digits.length : 0;
    if (reduce) {
      el.textContent = formatCount(target, pad, money);
      return;
    }
    const start = performance.now();
    const duration = 900;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = formatCount(target * eased, pad, money);
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function countInside(scope) {
    scope.querySelectorAll('.cats__num, .news-slide__price').forEach(runCount);
    if (scope.matches('.cats__num, .news-slide__price')) runCount(scope);
  }

  document.querySelectorAll('.news-slide.is-active .news-slide__price').forEach(runCount);

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
      if (!button || button.dataset.liqDone) return;
      const previous = button.textContent;
      if (form.classList.contains('js-request-form')) {
        button.dataset.liqDone = '1';
        button.textContent = 'Заявка отправлена';
        setTimeout(() => {
          button.textContent = previous;
          delete button.dataset.liqDone;
        }, 1600);
      }
    });
  });
})();
