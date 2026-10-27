
(() => {
  const root = document.querySelector('.js-news-slider');
  if (!root) return;
  const slides = [...root.querySelectorAll('.news-slide')];
  if (slides.length < 2) return;
  let i = slides.findIndex((s) => s.classList.contains('is-active'));
  if (i < 0) i = 0;
  const dotsWrap = root.querySelector('.js-ns-dots');
  const dots = slides.map((_, idx) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'news-slider__dot';
    dot.setAttribute('aria-label', `Слайд ${idx + 1}`);
    dot.addEventListener('click', () => show(idx));
    dotsWrap?.appendChild(dot);
    return dot;
  });
  const show = (n) => {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, idx) => s.classList.toggle('is-active', idx === i));
    dots.forEach((dot, idx) => dot.classList.toggle('is-active', idx === i));
  };
  show(i);
  root.querySelector('.js-ns-prev')?.addEventListener('click', () => show(i - 1));
  root.querySelector('.js-ns-next')?.addEventListener('click', () => show(i + 1));
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce) setInterval(() => show(i + 1), 4500);
})();
