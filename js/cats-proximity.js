/* Spotlight across the catalog grid. Hover reveals stay in CSS,
   so the cards still work with JavaScript off. */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const grid = document.querySelector('.cats__grid');
  if (!grid || reduce || coarse) return;

  const cards = () => grid.querySelectorAll('.cats__card, .cats__promo');
  const radius = 280;
  let frame = 0;
  let x = 0;
  let y = 0;

  const paint = () => {
    frame = 0;
    cards().forEach((card) => {
      const rect = card.getBoundingClientRect();
      const dx = x - (rect.left + rect.width / 2);
      const dy = y - (rect.top + rect.height / 2);
      const dist = Math.hypot(dx, dy) || 1;
      const near = Math.max(0, 1 - dist / radius);
      const pull = near * 8;
      card.style.setProperty('--near', near.toFixed(3));
      card.style.setProperty('--mx', `${((x - rect.left) / rect.width * 100).toFixed(1)}%`);
      card.style.setProperty('--my', `${((y - rect.top) / rect.height * 100).toFixed(1)}%`);
      card.style.setProperty('--tx', `${(dx / dist * pull).toFixed(2)}px`);
      card.style.setProperty('--ty', `${(dy / dist * pull).toFixed(2)}px`);
      card.style.setProperty('--ry', `${(-dx / rect.width * 8 * near).toFixed(2)}deg`);
      card.style.setProperty('--rx', `${(dy / rect.height * 6 * near).toFixed(2)}deg`);
      card.style.setProperty('--zoom', (1 + near * 0.08).toFixed(3));
    });
  };

  grid.addEventListener('pointermove', (event) => {
    if (event.pointerType && event.pointerType !== 'mouse') return;
    x = event.clientX;
    y = event.clientY;
    if (!frame) frame = requestAnimationFrame(paint);
  });

  grid.addEventListener('pointerleave', () => {
    cards().forEach((card) => {
      ['--near', '--mx', '--my', '--tx', '--ty', '--rx', '--ry', '--zoom'].forEach((name) => {
        card.style.removeProperty(name);
      });
    });
  });
})();
