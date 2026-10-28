(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Endless reels and marquee: duplicate content once so translate(-50%) loops seamlessly.
  document.querySelectorAll('.js-reel, .js-marquee').forEach((track) => {
    [...track.children].forEach((node) => {
      const copy = node.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true');
      if (copy.tagName === 'A') copy.tabIndex = -1;
      copy.querySelectorAll('a').forEach((a) => { a.tabIndex = -1; });
      track.appendChild(copy);
    });
  });

  // Hero prompt: modes change the placeholder and example chips.
  const MODES = {
    task: {
      placeholder: 'Например: частный дом 160 м², нужен щит, автоматы и кабель на всю разводку',
      chips: ['Щит на 24 модуля для дома', 'Освещение склада 600 м²', 'Кабель ВВГнг 3×2,5, 200 м'],
    },
    sku: {
      placeholder: 'Вставьте артикулы или названия, по одному в строке',
      chips: ['EZ9F34325', 'ВВГнг-LS 3×2,5', 'ЩРН-24'],
    },
    panel: {
      placeholder: 'Сколько групп, какая мощность, нужны ли УЗО и счётчик',
      chips: ['Квартира, 12 групп', 'Коттедж, 3 фазы, 15 кВт', 'Гараж с мастерской'],
    },
  };

  const form = document.querySelector('.js-prompt');
  const field = document.getElementById('prompt-text');
  const chipsBox = document.querySelector('.js-chips');
  const status = document.querySelector('.js-prompt-status');
  const modeTabs = [...document.querySelectorAll('.modes [data-mode]')];
  let typing = 0;

  const typeInto = (text) => {
    window.clearInterval(typing);
    field.focus();
    if (reduce) { field.value = text; return; }
    field.value = '';
    let i = 0;
    typing = window.setInterval(() => {
      field.value = text.slice(0, ++i);
      if (i >= text.length) window.clearInterval(typing);
    }, 22);
  };

  const setMode = (key) => {
    const mode = MODES[key] || MODES.task;
    modeTabs.forEach((tab) => tab.setAttribute('aria-selected', String(tab.dataset.mode === key)));
    field.placeholder = mode.placeholder;
    chipsBox.replaceChildren(...mode.chips.map((label) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.textContent = label;
      chip.addEventListener('click', () => typeInto(label));
      return chip;
    }));
  };

  modeTabs.forEach((tab) => tab.addEventListener('click', () => setMode(tab.dataset.mode)));
  setMode('task');

  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    const send = form.querySelector('.prompt__send');
    if (!field.value.trim()) {
      status.textContent = 'Опишите задачу или выберите пример под полем';
      status.classList.remove('is-ok');
      field.focus();
      return;
    }
    send.setAttribute('aria-busy', 'true');
    send.textContent = 'Отправляем';
    window.setTimeout(() => {
      send.removeAttribute('aria-busy');
      send.textContent = 'Отправить заявку';
      status.textContent = 'Заявка отправлена. Это демо, инженер не придёт, но на настоящем сайте ответит за 15 минут.';
      status.classList.add('is-ok');
      field.value = '';
    }, 700);
  });

  // Order steps: Runway-like tabs that advance on their own with a progress line.
  const steps = document.querySelector('.js-steps');
  if (steps) {
    const tabs = [...steps.querySelectorAll('[role="tab"]')];
    const panels = tabs.map((t) => document.getElementById(t.getAttribute('aria-controls')));
    const STEP_MS = 6000;
    let current = 0;
    let timer = 0;
    let visible = false;
    let hovering = false;

    const show = (n, focus) => {
      current = (n + tabs.length) % tabs.length;
      tabs.forEach((t, i) => {
        const on = i === current;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        panels[i].hidden = !on;
      });
      if (focus) tabs[current].focus();
      schedule();
    };

    const schedule = () => {
      window.clearTimeout(timer);
      if (reduce || !visible || hovering) return;
      // Restart the CSS progress animation for the active tab.
      steps.classList.remove('is-auto');
      void steps.offsetWidth;
      steps.classList.add('is-auto');
      timer = window.setTimeout(() => show(current + 1), STEP_MS);
    };

    steps.style.setProperty('--step-ms', `${STEP_MS}ms`);
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => show(i));
      t.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') show(current + 1, true);
        if (e.key === 'ArrowLeft') show(current - 1, true);
      });
    });
    steps.addEventListener('mouseenter', () => {
      hovering = true;
      window.clearTimeout(timer);
      steps.classList.remove('is-auto');
    });
    steps.addEventListener('mouseleave', () => { hovering = false; schedule(); });

    new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) schedule();
      else window.clearTimeout(timer);
    }, { threshold: 0.35 }).observe(steps);

    show(0);
  }

  // Catalog filter pills.
  const filters = document.querySelector('.js-filters');
  const cards = [...document.querySelectorAll('.js-cards .card')];
  filters?.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-f]');
    if (!btn) return;
    filters.querySelectorAll('[data-f]').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    cards.forEach((card) => { card.hidden = btn.dataset.f !== 'all' && card.dataset.g !== btn.dataset.f; });
  });
})();
