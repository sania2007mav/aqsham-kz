#!/usr/bin/env python3
"""Set homepage category icons.

Entries starting with "img:" use a mask PNG cut from the client's category sheet
(see cut_category_icons.py); other entries are inline SVG bodies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", *sorted((ROOT / "samples").glob("*.html"))]

# Order matches .cats__grid on the homepage (01..12).
ICONS = [
    "img:montazhnye",  # 01 Электромонтажные изделия, инструменты и силовые разъемы
    "img:dvigateli",  # 02 Электродвигатели и отопительные оборудования
    "img:shchity",  # 03 Щиты, боксы и принадлежности к ним
    "img:prokladka",  # 04 Системы для прокладки кабеля
    "img:silovoe",  # 05 Силовое оборудование защиты и коммутации
    "img:svetotekhnika",  # 06 Светотехника
    "img:santekhnika",  # 07 Сантехника
    # 08 Радиоэлектроника — no counterpart on the sheet, drawn chip icon
    '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4'
    'M3 10h4M3 14h4M17 10h4M17 14h4"/><circle cx="9.8" cy="9.8" r=".6"/>',
    "img:modulnoe",  # 09 Модульное оборудование
    "img:kabel",  # 10 Кабельная продукция
    "img:ustanovochnye",  # 11 Подкатегории Изделий
    "img:pribory",  # 12 Приборы учета
]

SVG_OPEN = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round">'
)
PATTERN = re.compile(
    r'(<span class="cats__icon[^"]*" aria-hidden="true">).*?(</span>)',
    re.S,
)


def render(entry: str) -> tuple[str, str]:
    if entry.startswith("img:"):
        name = entry[4:]
        return (
            '<span class="cats__icon cats__icon--pic" aria-hidden="true">',
            f'<i class="cats__pic" style="--ico:url(/assets/cat-icons/{name}.png)"></i>',
        )
    return '<span class="cats__icon" aria-hidden="true">', f"{SVG_OPEN}{entry}</svg>"


def patch(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    found = len(PATTERN.findall(html))
    if found != len(ICONS):
        print(f"SKIP {path.name}: found {found} icons, expected {len(ICONS)}")
        return
    it = iter(ICONS)

    def repl(m: re.Match) -> str:
        open_tag, inner = render(next(it))
        return f"{open_tag}{inner}{m.group(2)}"

    html = PATTERN.sub(repl, html)
    path.write_text(html, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT)}: {found} icons")


def main() -> None:
    for page in PAGES:
        patch(page)


if __name__ == "__main__":
    main()
