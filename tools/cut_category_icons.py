#!/usr/bin/env python3
"""Cut white line icons from the client's category sheet into alpha masks."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source" / "categories-sheet.jpg"
OUT = ROOT / "assets" / "cat-icons"

# Approximate icon areas on the 976x1024 sheet (left, top, right, bottom).
BOXES = {
    "modulnoe": (88, 10, 202, 130),
    "silovoe": (570, 10, 664, 135),
    "pribory": (88, 155, 202, 285),
    "shchity": (568, 155, 688, 290),
    "prokladka": (82, 305, 225, 435),
    "ustanovochnye": (562, 318, 724, 418),
    "kommutacionnoe": (86, 455, 256, 580),
    "istochniki": (564, 450, 776, 585),
    "svetotekhnika": (80, 600, 314, 722),
    "montazhnye": (572, 600, 724, 724),
    "kabel": (88, 740, 296, 870),
    "dvigateli": (558, 740, 756, 868),
    "santekhnika": (106, 885, 268, 1006),
}

LOW, HIGH = 120, 215  # red channel: blue background stays low, white lines are high


def to_mask(tile: Image.Image) -> Image.Image:
    red = tile.getchannel("R")
    return red.point(lambda v: 0 if v <= LOW else 255 if v >= HIGH else int((v - LOW) * 255 / (HIGH - LOW)))


def trim(mask: Image.Image, pad: int = 4) -> Image.Image:
    bbox = mask.point(lambda v: 255 if v > 60 else 0).getbbox()
    if not bbox:
        return mask
    l, t, r, b = bbox
    return mask.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, mask.width), min(b + pad, mask.height)))


def main() -> None:
    sheet = Image.open(SRC).convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    previews = []
    for name, box in BOXES.items():
        mask = trim(to_mask(sheet.crop(box)))
        white = Image.new("RGBA", mask.size, (255, 255, 255, 255))
        white.putalpha(mask)
        white.save(OUT / f"{name}.png", optimize=True)
        previews.append((name, white))
        print(f"{name}: {mask.size}")

    cell = 220
    sheet_out = Image.new("RGB", (cell * 4, cell * ((len(previews) + 3) // 4)), (30, 28, 24))
    for i, (name, img) in enumerate(previews):
        thumb = img.copy()
        thumb.thumbnail((cell - 20, cell - 20))
        x = (i % 4) * cell + (cell - thumb.width) // 2
        y = (i // 4) * cell + (cell - thumb.height) // 2
        yellow = Image.new("RGBA", thumb.size, (255, 228, 0, 255))
        yellow.putalpha(thumb.getchannel("A"))
        sheet_out.paste(yellow, (x, y), yellow)
    sheet_out.save(ROOT / "tools" / "_icons_preview.png")
    print("preview saved")


if __name__ == "__main__":
    main()
