#!/usr/bin/env python3
"""Check the public gallery card/title/source-note contract.

Run from the website root: python3 scripts/check_gallery_contract.py
Or point to a local checkout: python3 scripts/check_gallery_contract.py --root PATH

This intentionally checks the reusable gallery interface, not historical
accuracy or the private archival catalog. It uses Python's standard library.
"""
from __future__ import annotations

import argparse
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit


def read(root: Path, path: str) -> str:
    file = root / path
    if not file.is_file():
        raise ValueError(f"Missing required site file: {path}")
    return file.read_text(encoding="utf-8")


def cards(source: str, card_class: str) -> list[tuple[str, str]]:
    """Return (card title, gallery href) for gallery-navigation cards."""
    article_re = re.compile(
        rf'<article\s+class="{re.escape(card_class)}"[^>]*>(.*?)</article>', re.S
    )
    result: list[tuple[str, str]] = []
    for body in article_re.findall(source):
        heading = re.search(r"<h3\b[^>]*>(.*?)</h3>", body, re.S)
        if not heading:
            raise ValueError(f"A {card_class} card has no h3 title")
        title = unescape(re.sub(r"<[^>]+>", "", heading.group(1))).strip()
        links = re.findall(r'href="([^"]+)"', body)
        href = next(
            (unescape(link) for link in links if link.startswith("gallery.html?")), None
        )
        if not title or not href:
            raise ValueError(f"A {card_class} card is missing a title/gallery link")
        result.append((title, href))
    return result


def check(root: Path) -> tuple[int, int]:
    collections = json.loads(read(root, "data/collections.json"))
    years = json.loads(read(root, "data/bfhf-events.json"))["years"]
    collection_map = {entry["id"]: entry for entry in collections}
    if len(collection_map) != len(collections):
        raise ValueError("Duplicate collection IDs in data/collections.json")

    checked = 0
    year_pages = sorted(root.glob("bfhf-[0-9][0-9][0-9][0-9].html"))
    if not year_pages:
        raise ValueError("No BFHF year pages found")
    for page in year_pages:
        year = page.stem.removeprefix("bfhf-")
        if year not in years:
            raise ValueError(f"{page.name}: year is missing from bfhf-events.json")
        expected = {
            e["key"]: e["title"] for e in years[year]["events"]
            if e.get("show_in_navigation") is not False
        }
        found: set[str] = set()
        page_cards = cards(page.read_text(encoding="utf-8"), "bfhf-event")
        for title, href in page_cards:
            params = parse_qs(urlsplit(href).query)
            key = params.get("event", [None])[0]
            ref_year = params.get("bfhf_year", [None])[0]
            if ref_year != year or key not in expected:
                raise ValueError(f"{page.name}: unrecognized event gallery link {href}")
            if title != expected[key]:
                raise ValueError(
                    f"{page.name}: card title {title!r} differs from gallery title "
                    f"{expected[key]!r} for {key}"
                )
            if key in found:
                raise ValueError(f"{page.name}: event {key} has duplicate cards")
            found.add(key)
            checked += 1
        if found != set(expected):
            raise ValueError(
                f"{page.name}: visible event cards {sorted(found)} do not match "
                f"configured events {sorted(expected)}"
            )

    # A long-running organization uses an occasion card, not a binder label.
    brg_page = read(root, "brg-1990.html")
    brg_cards = cards(brg_page, "archive-event")
    if not brg_cards:
        raise ValueError("brg-1990.html: no archive-event cards found")
    for title, href in brg_cards:
        params = parse_qs(urlsplit(href).query)
        cid = params.get("collection", [None])[0]
        collection = collection_map.get(cid)
        if not collection:
            raise ValueError(f"BRG card points to unknown collection {cid!r}")
        displayed = collection.get("display_title") or collection["title"]
        if title != displayed:
            raise ValueError(
                f"BRG card title {title!r} differs from gallery title {displayed!r} "
                f"for collection {cid}"
            )
        checked += 1

    # The common gallery template must not place a source note below Back.
    gallery = read(root, "gallery.html")
    header_start = gallery.find('<section class="page-header">')
    gallery_start = gallery.find('id="photo-grid"')
    more_start = gallery.find('id="load-more"')
    note_start = gallery.find('id="gallery-notice"')
    section_end = gallery.find("</section>", gallery_start)
    note = re.search(r'<p\b[^>]*id="gallery-notice"[^>]*>', gallery)
    if -1 in (header_start, gallery_start, more_start, note_start, section_end):
        raise ValueError("gallery.html: expected gallery regions are missing")
    if not (gallery_start < more_start < note_start < section_end):
        raise ValueError(
            "gallery.html: the source note must follow the photographic grid and "
            "load-more action, inside the gallery content section"
        )
    if not note or 'class="gallery-source-note"' not in note.group(0):
        raise ValueError("gallery.html: source note must use gallery-source-note")
    if "hidden" not in note.group(0):
        raise ValueError("gallery.html: optional source note must be hidden by default")

    css = read(root, "assets/css/curatorial.css")
    if not re.search(r"\.gallery-source-note\s*\{", css) or not re.search(
        r"\.gallery-source-note\[hidden\]\s*\{\s*display\s*:\s*none", css
    ):
        raise ValueError("Missing shared source-note CSS/hidden behavior")

    js = read(root, "assets/js/gallery.js")
    if "collection.gallery_source_note||collection.notice" not in js:
        raise ValueError("The gallery renderer must prefer gallery_source_note")
    if "collection.display_title||collection.title" not in js:
        raise ValueError("The gallery heading must prefer display_title")
    return checked, len(year_pages)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        checked, years = check(args.root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: {checked} gallery cards across {years} BFHF year pages and BRG; source note layout verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())