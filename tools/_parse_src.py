#!/usr/bin/env python3
import re
from collections import Counter
from pathlib import Path

html = Path(r"d:\Projects\058_aqsham.kz\_src.html").read_text(encoding="utf-8")

print("=== CSS ===")
for m in re.findall(r'href="([^"]+\.css[^"]*)"', html):
    print(m)

print("\n=== IMGS ===")
imgs = re.findall(r'(?:src|srcset|data-src)="([^"]+)"', html)
seen = set()
for u in imgs:
    if any(x in u.lower() for x in (".jpg", ".png", ".webp", ".svg", ".jpeg")):
        u0 = u.split()[0]
        if u0 not in seen:
            seen.add(u0)
            print(u0[:200])

print("\n=== KEY CLASSES ===")
c = Counter()
for cl in re.findall(r'class="([^"]+)"', html):
    for x in cl.split():
        low = x.lower()
        if any(
            k in low
            for k in (
                "hero",
                "banner",
                "catalog",
                "brand",
                "footer",
                "header",
                "slide",
                "project",
                "news",
                "menu",
                "aq-",
                "swiper",
            )
        ):
            c[x] += 1
for name, n in c.most_common(50):
    print(f"{n:3} {name}")

print("\n=== HEADINGS ===")
for t in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", html, re.S)[:30]:
    txt = re.sub(r"<[^>]+>", "", t).strip()
    if txt:
        print("-", txt[:100])
