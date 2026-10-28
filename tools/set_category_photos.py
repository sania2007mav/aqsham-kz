#!/usr/bin/env python3
"""Add category photos and the icons/photos view switch to the homepage catalog.

Photos are original AI-generated product shots (no third-party images).
Re-runnable: existing photos and the switch are replaced, not duplicated.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
GENERATED = Path.home() / ".cursor" / "projects" / "d-Projects-058-aqsham-kz" / "assets"
PHOTOS = ROOT / "assets" / "cat-photos"
PAGES = [ROOT / "index.html", *sorted((ROOT / "samples").glob("*.html"))]

# Order matches .cats__grid on the homepage (01..12).
ORDER = [
    "montazhnye",
    "dvigateli",
    "shchity",
    "prokladka",
    "silovoe",
    "svetotekhnika",
    "santekhnika",
    "radioelektronika",
    "modulnoe",
    "kabel",
    "ustanovochnye",
    "pribory",
]

SWITCH = (
    '<div class="cats__switch js-cats-switch" role="group" aria-label="Вид карточек каталога">'
    '<button type="button" data-cats-view="icons">Иконки</button>'
    '<button type="button" data-cats-view="photo">Фото в нашем стиле</button>'
    '<button type="button" data-cats-view="plain">Каталог</button>'
    "</div>"
)

PHOTO_RE = re.compile(r'\s*<img class="cats__photo"[^>]*>')
SWITCH_RE = re.compile(r'<div class="cats__switch js-cats-switch".*?</div>', re.S)
ICON_SPAN_RE = re.compile(r'(<span class="cats__icon[^"]*" aria-hidden="true">.*?</span>)', re.S)
LINE_RE = re.compile(r'(<div class="cats__line" aria-hidden="true"></div>)')


def build_photos() -> None:
    PHOTOS.mkdir(parents=True, exist_ok=True)
    for name in ORDER:
        dst = PHOTOS / f"{name}.jpg"
        src = GENERATED / f"{name}.jpg"
        if not src.exists():
            if dst.exists():
                continue
            raise SystemExit(f"missing generated photo: {src}")
        img = Image.open(src).convert("RGB")
        img.thumbnail((640, 480))
        img.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
        print(f"photo {dst.name}: {img.size}, {dst.stat().st_size // 1024} KB")


def patch(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = PHOTO_RE.sub("", html)
    html = SWITCH_RE.sub("", html)

    if len(ICON_SPAN_RE.findall(html)) != len(ORDER):
        print(f"SKIP {path.name}: icon count mismatch")
        return

    it = iter(ORDER)

    def add_photo(m: re.Match) -> str:
        name = next(it)
        return (
            f"{m.group(1)}\n\t\t\t\t\t"
            f'<img class="cats__photo" src="/assets/cat-photos/{name}.jpg" alt="" '
            f'width="640" height="480" loading="lazy" decoding="async">'
        )

    html = ICON_SPAN_RE.sub(add_photo, html)
    html = LINE_RE.sub(lambda m: f"{m.group(1)}\n\n\t\t{SWITCH}", html, count=1)
    if "/js/cats-view.js" not in html:
        html = html.replace("</body>", '  <script src="/js/cats-view.js"></script>\n</body>', 1)
    path.write_text(html, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT)}")


def main() -> None:
    build_photos()
    for page in PAGES:
        patch(page)


if __name__ == "__main__":
    main()
