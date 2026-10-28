(() => {
  const section = document.querySelector('.cats');
  const sw = document.querySelector('.js-cats-switch');
  if (!section || !sw) return;

  const VIEWS = ['icons', 'photo', 'plain'];
  const KEY = 'aq-cats-view';
  const fromUrl = new URLSearchParams(location.search).get('cats');
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }

  const set = (view, persist) => {
    if (!VIEWS.includes(view)) view = 'icons';
    section.dataset.view = view;
    sw.querySelectorAll('[data-cats-view]').forEach((btn) => {
      btn.setAttribute('aria-pressed', String(btn.dataset.catsView === view));
    });
    if (persist) {
      try { localStorage.setItem(KEY, view); } catch (e) { /* private mode */ }
    }
  };

  set(fromUrl || saved || 'icons', false);
  sw.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-cats-view]');
    if (btn) set(btn.dataset.catsView, true);
  });
})();
