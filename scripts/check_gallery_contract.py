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

    # Person and organization subject collections share one navigation contract.
    subjects = json.loads(read(root, "data/subjects.json"))
    subject_map = {entry["id"]: entry for entry in subjects}
    if len(subject_map) != len(subjects):
        raise ValueError("Duplicate subject IDs in data/subjects.json")
    gallery_to_subject = {}
    for subj in subjects:
        sid = subj["id"]
        if subj["subject_type"] not in {"person", "organization", "topic"}:
            raise ValueError(f"{sid}: invalid subject_type")
        if not (root / subj["page"]).is_file():
            raise ValueError(f"{sid}: subject page not found: {subj['page']}")
        page = read(root, subj["page"])
        if "collection-history" not in page:
            raise ValueError(f"{sid}: missing subject historical introduction")
        if not subj.get("collection_ids"):
            raise ValueError(f"{sid}: no published occasion galleries")
        for cid in subj["collection_ids"]:
            if cid in gallery_to_subject:
                raise ValueError(f"{cid}: gallery assigned to multiple subjects")
            gallery_to_subject[cid] = sid
            if cid not in collection_map:
                raise ValueError(f"{sid}: gallery {cid} missing from collections register")
            record = collection_map[cid]
            if record.get("subject_id") != sid:
                raise ValueError(f"{cid}: subject_id does not match subject register")
            if record.get("intro") not in {subj["page"], "bfhf-1987.html", "bfhf-1988.html", "bfhf-1990.html"}:
                raise ValueError(f"{cid}: unexpected gallery intro route")
    if set(gallery_to_subject) != set(collection_map):
        raise ValueError("Every published gallery must have exactly one subject")
    dellums = subject_map.get("ronald-v-dellums")
    if not dellums or dellums["subject_type"] != "person":
        raise ValueError("Dellums should be a person subject")
    dellums_page = read(root, dellums["page"])
    dellums_cards = cards(dellums_page, "archive-event")
    expected_title = collection_map["dellums-1987"].get("display_title")
    if len(dellums_cards) != 1 or dellums_cards[0][0] != expected_title:
        raise ValueError("Dellums occasion card title must match the gallery display title")
    if parse_qs(urlsplit(dellums_cards[0][1]).query).get("collection") != ["dellums-1987"]:
        raise ValueError("Dellums occasion card must link to the original gallery ID")
    if 'data-id="JB-000103"' not in dellums_page or 'data-type="document"' not in dellums_page:
        raise ValueError("Dellums invitation must use the shared document viewer")
    if 'src="assets/js/editorial-photo.js"' not in dellums_page:
        raise ValueError("Dellums document viewer script is missing")
    checked += len(dellums_cards)

    # Topic-led collections use the same matched gallery title contract.
    for cid, page_name in (("community-baseball", "community-baseball.html"),
                           ("portraits", "portraits.html"), ("environmental", "environmental.html")):
        thematic_cards = cards(read(root, page_name), "archive-event")
        display = collection_map[cid].get("display_title") or collection_map[cid]["title"]
        if len(thematic_cards) != 1 or thematic_cards[0][0] != display:
            raise ValueError(f"{page_name}: card title must match gallery heading {display!r}")
        if parse_qs(urlsplit(thematic_cards[0][1]).query).get("collection") != [cid]:
            raise ValueError(f"{page_name}: gallery card must link to {cid}")
        checked += 1

    # Published civic subjects sit under exactly one thematic parent; archival galleries stay unchanged.
    groups = json.loads(read(root, "data/collection-groups.json"))
    seen_subjects = set()
    for group in groups:
        if group["theme"] != "community-civic-life":
            raise ValueError(f"{group['id']}: unexpected theme")
        page = read(root, group["page"])
        if "collection-history" not in page or 'class="archive-event-grid"' not in page:
            raise ValueError(f"{group['page']}: missing parent introduction or photograph index")
        if not group["subject_ids"]:
            raise ValueError(f"{group['id']}: empty public subject group")
        for sid in group["subject_ids"]:
            if sid not in subject_map or sid in seen_subjects:
                raise ValueError(f"Missing or duplicated subject in groups: {sid}")
            seen_subjects.add(sid)
            subject = subject_map[sid]
            if subject.get("parent_group_id") != group["id"]:
                raise ValueError(f"{sid}: parent group mismatch")
            if ('href="' + subject["page"] + '"') not in page or ('<h3>' + subject["title"] + '</h3>') not in page:
                raise ValueError(f"{sid}: parent page missing the subject card")
    if seen_subjects != {s["id"] for s in subjects if s["theme"] == "community-civic-life"}:
        raise ValueError("Not all published civic subjects are present in parent groups")

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
    print(f"PASS: {checked} gallery cards across BFHF, BRG and Dellums; subject mapping and source note layout verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())