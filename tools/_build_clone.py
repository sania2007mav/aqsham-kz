#!/usr/bin/env python3
"""Build a scrollable static clone of aqsham.kz with glassmorphism samples."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(r"d:\Projects\058_aqsham.kz")
ASSETS = ROOT / "assets"
DIST = ROOT  # site root = project root for deploy

# CSS needed for look
CSS_FILES = [
    "variables.css",
    "base.css",
    "layout.css",
    "header.css",
    "burger.css",
    "footer.css",
    "home.css",
    "home-sections.css",
    "catalog.css",
    "news.css",
    "reveal.css",
]


def rewrite_css(text: str) -> str:
    # flatten theme-relative image urls into /assets/
    text = re.sub(
        r"url\(\s*['\"]?(?:\.\./)+img/([^)'\"]+)['\"]?\s*\)",
        r"url('../assets/\1')",
        text,
    )
    text = re.sub(
        r"url\(\s*['\"]?(?:\.\./)+icons/([^)'\"]+)['\"]?\s*\)",
        r"url('../assets/\1')",
        text,
    )
    return text


def clean_body(body: str) -> str:
    # remove PWA splash / sticky widgets / modals noise for dummy
    drop_blocks = [
        r'<div class="pwa-splash".*?</div>\s*</div>',
        r'<div class="mystickyelements-fixed[^"]*".*?(?=<footer|<div class="footer|$)',
        r'<div id="wpadminbar".*?</div>',
    ]
    # softer: remove known modal/cart overlays at end
    for pat in [
        r'<div class="toast[\s\S]*$',
        r'<div class="modal[\s\S]*$',
        r'<div class="cart-drawer[\s\S]*$',
        r'<div class="aq-compare[\s\S]*$',
        r'<div class="pwa-install[\s\S]*$',
        r'<div class="tab-bar[\s\S]*$',
    ]:
        body = re.sub(pat, "", body, flags=re.I)

    # neutralize live links to # for dummy
    body = body.replace("https://www.aqsham.kz/cart/", "#")
    body = body.replace('href="https://www.aqsham.kz/"', 'href="#"')
    body = body.replace("https://www.aqsham.kz/", "#")
    body = re.sub(r'action="[^"]*"', 'action="#"', body)

    # strip leftover script-ish empty
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def write_theme_css_bundle() -> None:
    css_dir = ROOT / "css"
    css_dir.mkdir(exist_ok=True)
    parts = []
    for name in CSS_FILES:
        src = ASSETS / name
        if not src.exists():
            print("missing css", name)
            continue
        parts.append(f"/* === {name} === */\n" + rewrite_css(src.read_text(encoding="utf-8", errors="replace")))
    (css_dir / "theme-clone.css").write_text("\n\n".join(parts), encoding="utf-8")
    print("theme-clone.css", sum(len(p) for p in parts), "chars")


GLASS_CSS = r"""
/* Glass modernization overlay on top of AQSHAM clone */
:root {
  --glass-bg: rgba(255, 255, 255, 0.55);
  --glass-bg-dark: rgba(58, 54, 45, 0.72);
  --glass-line: rgba(255, 255, 255, 0.35);
  --glass-blur: 16px;
}

body {
  background:
    radial-gradient(900px 500px at 10% -10%, rgba(255, 228, 0, 0.18), transparent 55%),
    radial-gradient(800px 480px at 90% 0%, rgba(111, 220, 255, 0.14), transparent 50%),
    linear-gradient(180deg, #f4f1ec 0%, #ece8e2 40%, #f7f7f5 100%) !important;
}

.header,
.header-mobile,
.nav-bar,
.site-nav,
.burger {
  backdrop-filter: blur(var(--glass-blur)) saturate(1.2);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(1.2);
}

.header {
  background: var(--glass-bg-dark) !important;
  border-bottom: 1px solid rgba(255,255,255,.12);
}

.news-slide,
.brand-card,
.project-card,
.catalog-card,
.home-catalog__item,
.catalog-grid__item,
.news-card,
.footer-cta,
.footer-main {
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-line) !important;
  backdrop-filter: blur(var(--glass-blur)) saturate(1.25);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(1.25);
  box-shadow: 0 18px 40px rgba(40, 30, 10, 0.08);
}

.news-slider,
.hero-sliders {
  position: relative;
}
.news-slider::before {
  content: "";
  position: absolute;
  inset: -8% -4%;
  z-index: -1;
  background:
    radial-gradient(circle at 70% 40%, rgba(255,228,0,.22), transparent 40%),
    radial-gradient(circle at 20% 60%, rgba(111,220,255,.16), transparent 42%);
  filter: blur(8px);
  pointer-events: none;
}

.demo-note {
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(26,26,26,.88);
  color: #fff;
  font: 600 13px/1.3 Outfit, Inter, system-ui, sans-serif;
  backdrop-filter: blur(12px);
}
.demo-note a {
  color: #ffe400;
  text-decoration: none;
  margin-left: 10px;
}
.demo-note .links a {
  color: #fff;
  opacity: .85;
  margin-left: 12px;
}
.demo-note .links a:hover { opacity: 1; color: #ffe400; }
"""

DARK_GLASS = r"""
body {
  background:
    radial-gradient(900px 500px at 12% -8%, rgba(255,228,0,.16), transparent 55%),
    radial-gradient(700px 420px at 88% 5%, rgba(111,220,255,.12), transparent 50%),
    linear-gradient(180deg, #12110f, #1a1814 45%, #10100e) !important;
  color: #f3f0ea !important;
}
:root { --glass-bg: rgba(255,255,255,.08); --glass-line: rgba(255,255,255,.14); }
.news-slide__title, .section-title, h1, h2, h3 { color: #fff !important; }
.news-slide__desc, p, .footer-main { color: #cfc8bc !important; }
.brand-card { background: rgba(255,255,255,.1) !important; }
"""

AURORA_GLASS = r"""
body {
  background: #090b12 !important;
}
body::before {
  content: "";
  position: fixed;
  inset: -15%;
  z-index: -1;
  background:
    radial-gradient(circle at 20% 20%, rgba(255,228,0,.28), transparent 32%),
    radial-gradient(circle at 75% 15%, rgba(90,140,255,.28), transparent 30%),
    radial-gradient(circle at 60% 75%, rgba(111,220,255,.2), transparent 34%);
  filter: blur(40px);
  animation: aurora 18s ease-in-out infinite alternate;
}
@keyframes aurora {
  from { transform: translate3d(0,0,0) scale(1); }
  to { transform: translate3d(2%,-2%,0) scale(1.05); }
}
:root { --glass-bg: rgba(255,255,255,.1); --glass-line: rgba(255,255,255,.18); }
.news-slide__title, .section-title, h1, h2, h3 { color: #fff !important; }
.news-slide__desc, p { color: #b9c3d6 !important; }
"""


def page(title: str, extra_css: str, body: str, variant: str) -> str:
    note_links = """
      <span class="links">
        <a href="/">V1 копия+стекло</a>
        <a href="/samples/v2-dark.html">V2 dark glass</a>
        <a href="/samples/v3-aurora.html">V3 aurora glass</a>
        <a href="/samples/v4-live.html">V4 live</a>
      </span>
    """
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="robots" content="noindex,nofollow" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/theme-clone.css" />
  <link rel="stylesheet" href="/css/glass.css" />
  {f'<link rel="stylesheet" href="/css/{extra_css}" />' if extra_css else ''}
</head>
<body class="aq-clone variant-{variant}">
  <div class="demo-note">
    <div>AQSHAM · пустышка-копия шаблона · glass · не прод</div>
    {note_links}
  </div>
  {body}
  <script src="/js/clone.js"></script>
</body>
</html>
"""


def write_js() -> None:
    js = ROOT / "js"
    js.mkdir(exist_ok=True)
    (js / "clone.js").write_text(
        r"""
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
""",
        encoding="utf-8",
    )


def main() -> None:
    write_theme_css_bundle()
    write_js()
    css = ROOT / "css"
    css.mkdir(exist_ok=True)
    (css / "glass.css").write_text(GLASS_CSS, encoding="utf-8")
    (css / "glass-dark.css").write_text(DARK_GLASS, encoding="utf-8")
    (css / "glass-aurora.css").write_text(AURORA_GLASS, encoding="utf-8")

    raw = (ROOT / "tools" / "_body_extract.html").read_text(encoding="utf-8")
    body = clean_body(raw)

    # fix asset paths for nested samples
    body_root = body  # assets/...
    body_nested = body.replace('src="assets/', 'src="/assets/').replace("src='assets/", "src='/assets/")
    body_root = body_nested  # always absolute from site root

    (ROOT / "index.html").write_text(
        page("AQSHAM Electric — копия + glass", "", body_root, "v1"),
        encoding="utf-8",
    )
    samples = ROOT / "samples"
    samples.mkdir(exist_ok=True)
    (samples / "v2-dark.html").write_text(
        page("AQSHAM — V2 Dark Glass", "glass-dark.css", body_root, "v2"),
        encoding="utf-8",
    )
    (samples / "v3-aurora.html").write_text(
        page("AQSHAM — V3 Aurora Glass", "glass-aurora.css", body_root, "v3"),
        encoding="utf-8",
    )

    # hub
    (ROOT / "hub.html").write_text(
        """<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AQSHAM — образцы</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&display=swap" rel="stylesheet"/>
<style>
body{margin:0;font-family:Outfit,system-ui,sans-serif;background:#12110f;color:#fff;min-height:100vh;display:grid;place-items:center}
.wrap{max-width:720px;padding:32px}
a{display:block;padding:18px 20px;margin:10px 0;border-radius:16px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);color:#fff;text-decoration:none;backdrop-filter:blur(12px)}
a:hover{border-color:#ffe400;color:#ffe400}
h1{margin:0 0 8px;font-size:1.8rem}
p{opacity:.7}
</style></head><body><div class="wrap">
<h1>AQSHAM — копии шаблона</h1>
<p>Листаемые пустышки с реального шаблона aqsham.kz + стекло</p>
<a href="/">V1 — копия + светлое стекло</a>
<a href="/samples/v2-dark.html">V2 — тёмное стекло</a>
<a href="/samples/v3-aurora.html">V3 — aurora стекло</a>
</div></body></html>
""",
        encoding="utf-8",
    )
    print("built index + samples")


if __name__ == "__main__":
    main()
