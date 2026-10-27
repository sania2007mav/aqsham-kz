#!/usr/bin/env python3
import re
import urllib.request
from pathlib import Path

ROOT = Path(r"d:\Projects\058_aqsham.kz")
html = (ROOT / "_src.html").read_text(encoding="utf-8")
assets = ROOT / "assets"
assets.mkdir(parents=True, exist_ok=True)

urls = []
for pat in [
    r"""(?:src|href|data-src)=['"]([^'"]+)['"]""",
    r"""url\((['"]?)(https?://[^)'"]+)\1\)""",
]:
    for m in re.finditer(pat, html):
        u = m.group(1) if m.lastindex == 1 else m.group(2)
        if u.startswith("//"):
            u = "https:" + u
        urls.append(u)

wanted = []
for u in urls:
    if "aqsham.kz" not in u:
        continue
    low = u.lower().split("?")[0]
    if any(low.endswith(ext) for ext in (".css", ".png", ".jpg", ".jpeg", ".webp", ".svg")):
        wanted.append(u.split()[0])

# unique preserve order
seen = set()
uniq = []
for u in wanted:
    if u not in seen:
        seen.add(u)
        uniq.append(u)

# prioritize visual assets
priority = [
    "logo.svg",
    "logo-mobile.svg",
    "image-removebg",
    "bez-nazvaniya",
    "brand-",
    "project-",
    "photo_2026",
    "gemini_generated",
    "footer-watermark",
    "style",
    "main",
    "theme",
]
selected = []
for u in uniq:
    name = u.rsplit("/", 1)[-1].lower()
    if any(p in u.lower() or p in name for p in priority):
        selected.append(u)

# also grab stylesheet links with single quotes
for m in re.finditer(r"""['"](https://www\.aqsham\.kz/[^'"]+\.css[^'"]*)['"]""", html):
    selected.append(m.group(1))

seen2 = set()
final = []
for u in selected:
    if u not in seen2:
        seen2.add(u)
        final.append(u)

print(f"downloading {len(final)} assets")
ua = {"User-Agent": "Mozilla/5.0"}
mapping = {}
for u in final:
    name = u.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    # avoid collisions
    if name in mapping.values():
        stem = Path(name).stem
        suf = Path(name).suffix
        name = f"{stem}-{abs(hash(u)) % 10000}{suf}"
    dest = assets / name
    try:
        req = urllib.request.Request(u, headers=ua)
        with urllib.request.urlopen(req, timeout=40) as r:
            dest.write_bytes(r.read())
        mapping[u] = f"assets/{name}"
        print("OK", name, dest.stat().st_size)
    except Exception as ex:
        print("FAIL", u, ex)

(ROOT / "tools" / "_asset_map.txt").write_text(
    "\n".join(f"{k}\t{v}" for k, v in mapping.items()), encoding="utf-8"
)
print("done", len(mapping))
