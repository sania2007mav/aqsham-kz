#!/usr/bin/env python3
"""Replace homepage category icons with line icons matching each category."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", *sorted((ROOT / "samples").glob("*.html"))]

# Order matches .cats__grid on the homepage (01..12).
ICONS = [
    # 01 Электромонтажные изделия, инструменты и силовые разъемы — отвёртка и пассатижи
    '<rect x="4.5" y="2.5" width="3.5" height="7" rx="1.2"/><path d="M6.25 9.5v9.5M5.5 19h1.5"/>'
    '<path d="M13 3c0 3.5 1.5 6 3.2 8M20.4 3c0 3.5-1.5 6-3.2 8"/><circle cx="16.7" cy="12" r="1.2"/>'
    '<path d="M16.1 13.1 14.5 21M17.3 13.1 18.9 21"/>',
    # 02 Электродвигатели и отопительное оборудование — электродвигатель
    '<rect x="4" y="7" width="12" height="9" rx="2"/><path d="M7.5 7v9M10 7v9M12.5 7v9"/>'
    '<path d="M16 11.5h5"/><path d="M6 16l-1 3h10l-1-3"/>',
    # 03 Щиты, боксы — щит с дверцей
    '<rect x="4" y="2.5" width="16" height="19" rx="1.5"/><path d="M4 6.5h16"/>'
    '<path d="M12.5 9 10 13.5h3.2L11 18"/><path d="M17 12.5v2"/>',
    # 04 Системы для прокладки кабеля — перфорированный лоток
    '<path d="M3 7v9h18V7"/><path d="M3 7h2.5M18.5 7H21"/><path d="M6.5 11.5h2M11 11.5h2M15.5 11.5h2"/>'
    '<path d="M3 19.5h18"/>',
    # 05 Силовое оборудование защиты и коммутации — силовой автомат
    '<rect x="6" y="2.5" width="12" height="19" rx="1.5"/><path d="M9 2.5v2.5M12 2.5v2.5M15 2.5v2.5'
    'M9 19v2.5M12 19v2.5M15 19v2.5"/><rect x="10" y="8.5" width="4" height="7" rx="1"/><path d="M12 9.5v3"/>',
    # 06 Светотехника — промышленный светильник
    '<path d="M12 2.5v3.5"/><path d="M9.5 6h5l1 3h-7z"/><path d="M3.5 15.5c0-3.6 3.8-6.5 8.5-6.5s8.5 2.9 8.5 6.5z"/>'
    '<path d="M7.5 18.5 6.5 21M12 18.5V21.5M16.5 18.5l1 2.5"/>',
    # 07 Сантехника — труба с вентилем
    '<path d="M2.5 13h5.5M16 13h5.5"/><path d="M2.5 10v6M21.5 10v6"/><rect x="8" y="10" width="8" height="6" rx="1"/>'
    '<path d="M12 10V6M8.5 5.5h7"/>',
    # 08 Радиоэлектроника — микросхема
    '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4'
    'M3 10h4M3 14h4M17 10h4M17 14h4"/><circle cx="9.8" cy="9.8" r=".6"/>',
    # 09 Модульное оборудование — трёхполюсный модульный автомат
    '<rect x="3" y="3.5" width="18" height="17" rx="1.5"/><path d="M9 3.5v17M15 3.5v17"/>'
    '<path d="M3 7.5h18M3 16.5h18"/><rect x="5" y="10" width="2" height="4" rx=".5"/>'
    '<rect x="11" y="10" width="2" height="4" rx=".5"/><rect x="17" y="10" width="2" height="4" rx=".5"/>',
    # 10 Кабельная продукция — барабан с кабелем
    '<circle cx="10" cy="12" r="8"/><circle cx="10" cy="12" r="5"/><circle cx="10" cy="12" r="1.5"/>'
    '<path d="M15 15.5c2 2 4 3 6.5 3"/>',
    # 11 Подкатегории изделий — выключатель и розетка
    '<rect x="2.5" y="6" width="9" height="12" rx="2"/><path d="M7 9v6"/>'
    '<rect x="12.5" y="6" width="9" height="12" rx="2"/><circle cx="17" cy="12" r="3"/>'
    '<path d="M15.8 12h.01M18.2 12h.01"/>',
    # 12 Приборы учета — мультиметр
    '<rect x="5" y="2.5" width="12" height="19" rx="2"/><rect x="7.5" y="5" width="7" height="4" rx=".6"/>'
    '<circle cx="11" cy="15" r="3"/><path d="M11 15l1.6-1.6"/><path d="M17 17h2.5v4.5"/>',
]

SVG_OPEN = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round">'
)
PATTERN = re.compile(
    r'(<span class="cats__icon" aria-hidden="true">)<svg\b[^>]*>.*?</svg>(</span>)',
    re.S,
)


def patch(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    found = len(PATTERN.findall(html))
    if found != len(ICONS):
        print(f"SKIP {path.name}: found {found} icons, expected {len(ICONS)}")
        return
    it = iter(ICONS)
    html = PATTERN.sub(lambda m: f"{m.group(1)}{SVG_OPEN}{next(it)}</svg>{m.group(2)}", html)
    path.write_text(html, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT)}: {found} icons")


def main() -> None:
    for page in PAGES:
        patch(page)


if __name__ == "__main__":
    main()
