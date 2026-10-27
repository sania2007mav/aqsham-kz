
(() => {
  const root = document.querySelector('.js-news-slider');
  if (!root) return;
  const slides = [...root.querySelectorAll('.news-slide')];
  if (slides.length < 2) return;
  let i = slides.findIndex((s) => s.classList.contains('is-active'));
  if (i < 0) i = 0;
  const show = (n) => {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, idx) => s.classList.toggle('is-active', idx === i));
  };
  root.querySelector('.js-ns-prev')?.addEventListener('click', () => show(i - 1));
  root.querySelector('.js-ns-next')?.addEventListener('click', () => show(i + 1));
  setInterval(() => show(i + 1), 4500);
})();
