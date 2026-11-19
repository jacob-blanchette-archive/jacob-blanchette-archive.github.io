#!/usr/bin/env python3
"""Check shared preview cards and intentionally distinct interior card roles.

Run: python3 scripts/check_preview_contract.py [--root PATH]
Requires Python standard library only; does not replace browser/mobile QA.
"""
from __future__ import annotations

import argparse
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit


CARD = re.compile(
    r'<div class="collection-card-wrap">\s*'
    r'<a class="collection-card" href="([^"]+)">([\s\S]*?)</a>\s*'
    r'<p class="featured-photo-credit">([\s\S]*?)</p>\s*</div>'
)


def read(root: Path, path: str) -> str:
    file = root / path
    if not file.is_file():
        raise ValueError(f"Missing site file: {path}")
    return file.read_text(encoding="utf-8")


def previews(root: Path, page: str, photos: dict) -> dict:
    source = read(root, page)
    blocks = CARD.findall(source)
    if not blocks or source.count('class="collection-card-wrap"') != len(blocks):
        raise ValueError(f"{page}: inconsistent collection-card-wrap / credit structure")
    found = {}
    for destination, body, credit in blocks:
        title = re.search(r'<h[34]>([^<]+)</h[34]>', body)
        image = re.search(r'<div class="collection-art">\s*<img\s+[^>]*src="([^"]+)"', body)
        action = re.search(r'<span class="textlink">([^<]+)</span>', body)
        record = re.search(r'<a href="([^"]+)"[^>]*>', credit)
        if not (title and image and action and record):
            raise ValueError(f"{page}: incomplete preview card {destination}")
        if '<a ' in body or '<a\n' in body:
            raise ValueError(f"{page}: nested link inside preview card {destination}")
        if "Photograph by Jacob Blanchette" not in credit or "View photo record and citation" not in credit:
            raise ValueError(f"{page}: missing credit below card {destination}")
        destination = unescape(destination)
        if destination in found or not (root / urlsplit(destination).path).is_file():
            raise ValueError(f"{page}: duplicate or missing destination {destination}")
        href = unescape(record.group(1))
        identifier = parse_qs(urlsplit(href).query).get("photo", [None])[0]
        if identifier not in photos or photos[identifier].get("published") is False:
            raise ValueError(f"{page}: unpublished or unresolvable photo record {identifier}")
        found[destination] = (unescape(title.group(1)), image.group(1), identifier, href)
    return found


def check(root: Path) -> int:
    rows = json.loads(read(root, "data/photos.json"))
    photos = {row["id"]: row for row in rows}
    if len(photos) != len(rows):
        raise ValueError("Duplicate public photo identifiers")
    home = previews(root, "index.html", photos)
    overview = previews(root, "collections.html", photos)
    if home != overview:
        raise ValueError("Home and Collections previews differ in title, image, route or credit link")
    portraiture = re.search(
        r'<section class="home-theme home-portraiture"[\s\S]*?</section>',
        read(root, "index.html"),
    )
    if not portraiture or "Collection in development" in portraiture.group(0) or portraiture.group(0).count('class="collection-card-wrap"') != 2:
        raise ValueError("Published Portraiture must have exactly two photographic previews")
    for page in ("index.html", "collections.html"):
        head = read(root, page).split("</head>", 1)[0]
        main = 'assets/css/curatorial.css'
        previews_css = 'assets/css/collection-previews.css'
        if not (main in head and previews_css in head and head.index(main) < head.index(previews_css)):
            raise ValueError(f"{page}: shared preview stylesheet must follow curatorial.css")
    css = read(root, 'assets/css/collection-previews.css')
    for selector in ('.collection-card-wrap .collection-art',
                     '.collection-card-wrap .collection-body',
                     '.collection-card-wrap>.featured-photo-credit'):
        if selector not in css:
            raise ValueError(f"Missing shared preview rule: {selector}")
    event_css = read(root, 'assets/css/bfhf-years.css')
    for selector in ('.bfhf-year-grid{',
                     '.bfhf-year-image{',
                     '.bfhf-year-text{',
                     '.bfhf-event-grid,.archive-event-grid{',
                     '.bfhf-event-photo,.archive-event-photo{',
                     '.bfhf-event-copy,.archive-event-copy{',
                     '.bfhf-event-actions,.archive-event-actions{'):
        if selector not in event_css:
            raise ValueError(f"Missing role-specific interior rule: {selector}")
    if 'class="bfhf-year-grid"' not in read(root, "bfhf.html"):
        raise ValueError("BFHF year overview must retain its distinct grid")
    for page in ('bfhf-1987.html', 'bfhf-1988.html', 'bfhf-1990.html',
                 'brg-1990.html', 'dellums-1987.html'):
        source = read(root, page)
        prefix = "bfhf-event" if page.startswith("bfhf-") else "archive-event"
        for name in (f'{prefix}-grid', prefix,
                     f'{prefix}-photo', f'{prefix}-copy', f'{prefix}-actions'):
            if f'class="{name}"' not in source:
                raise ValueError(f"{page}: missing interior card role {name}")
        if 'assets/css/bfhf-years.css' not in source.split("</head>", 1)[0]:
            raise ValueError(f"{page}: missing shared interior-card stylesheet")
    return len(home)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        count = check(args.root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: {count} matching Home/Collections previews; intentional year/occasion card roles preserved")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
