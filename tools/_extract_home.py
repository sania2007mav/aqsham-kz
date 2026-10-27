#!/usr/bin/env python3
"""Extract main homepage body markup from scraped aqsham HTML."""
import re
from pathlib import Path

ROOT = Path(r"d:\Projects\058_aqsham.kz")
html = (ROOT / "_src.html").read_text(encoding="utf-8")

# body inner
m = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
body = m.group(1) if m else html

# drop scripts
body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.S | re.I)
# drop wp admin / noise
body = re.sub(r"<!--.*?-->", "", body, flags=re.S)

# rewrite asset urls to local
repls = []
map_file = ROOT / "tools" / "_asset_map.txt"
if map_file.exists():
    for line in map_file.read_text(encoding="utf-8").splitlines():
        if "\t" in line:
            src, dst = line.split("\t", 1)
            repls.append((src, dst))
            # also without query
            repls.append((src.split("?")[0], dst))

# sort longest first
repls.sort(key=lambda x: len(x[0]), reverse=True)
for src, dst in repls:
    body = body.replace(src, dst)

# also generic theme/uploads to local assets by filename when possible
def local_asset(match: re.Match) -> str:
    url = match.group(0)
    name = url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    local = ROOT / "assets" / name
    if local.exists():
        return f"assets/{name}"
    return url


body = re.sub(
    r"https://www\.aqsham\.kz/wp-content/(?:themes/aqsham/assets|uploads)/[^\"'\s)]+",
    local_asset,
    body,
)

out = ROOT / "tools" / "_body_extract.html"
out.write_text(body, encoding="utf-8")
print("wrote", out, "chars", len(body))

# print section markers
for cls in [
    "header",
    "hero-sliders",
    "catalog",
    "brands",
    "projects",
    "news",
    "footer",
    "footer-cta",
]:
    print(cls, "->", body.find(cls))
