#!/usr/bin/env python3
"""Build direct (event or thematic) photographic collection pages.

Run: python3 scripts/build_direct_collection_pages.py [--check].
The template and manifest are authoritative. Gallery images are loaded
from the existing published data/photos.json at runtime, not duplicated.
"""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
FIELD = re.compile(r"{{([A-Z_]+)}}")


def e(s: str) -> str:
    return escape(str(s), quote=True)


def doc_link(d: dict) -> str:
    attrs = (
        ("class", "archive-doclink editorial-photo-trigger"),
        ("id", d["trigger_id"]), ("href", d["href"]),
        ("data-image", d["image"]), ("data-title", d["title"]),
        ("data-type", d.get("type", "document")),
        ("data-id", d["item_id"]), ("data-creator", d["creator"]),
        ("data-credit", d["credit"]), ("data-alt", d["alt"]),
        ("data-date", d["date"]), ("data-context", d["context"]),
        ("data-collection-title", d["collection_title"]),
        ("data-collection", d["collection_id"]), ("aria-label", d["aria_label"]))
    fields = " ".join(f'{key}="{e(value)}"' for key, value in attrs)
    return f'<a {fields}>{e(d["label"])}</a>'


def render(tpl: str, dialog: str, page: dict, collections: dict, photos: list) -> str:
    path, cid = page["path"], page["collection_id"]
    if "/" in path or ".." in path or not path.endswith(".html"):
        raise ValueError(f"Unsafe direct collection page path: {path}")
    if page["page_type"] not in ("event", "thematic"):
        raise ValueError(f"{path}: unsupported page type")
    if collections[cid]["intro"] != path or not page["history_paragraphs"]:
        raise ValueError(f"{path}: unknown intro route or empty narrative")
    available = [p for p in photos if p["collection_id"] == cid and
                 p.get("published") is not False and
                 "Jacob Blanchette" in str(p.get("photographer", "")) and
                 not str(p.get("photographer", "")).startswith(("Not applicable", "Not established"))]
    if not available:
        raise ValueError(f"{path}: no published photographs to show")
    documents = page.get("documents", [])
    for d in documents:
        if d["collection_id"] != cid:
            raise ValueError(f"{path}: unrelated document")
        if not any(p["id"] == d["item_id"] and p["collection_id"] == cid and
                   p.get("published") is not False for p in photos):
            raise ValueError(f"{path}: unapproved or missing document")
    actions = '<div class="single-occasion-actions">' + "".join(doc_link(d) for d in documents) + '</div>' if documents else ""
    fields = {
        "PAGE_TYPE": e(page["page_type"]), "PAGE_TITLE": e(page["page_title"]),
        "PAGE_EYEBROW": e(page["page_eyebrow"]), "PAGE_LEAD": e(page["page_lead"]),
        "PARENT_HREF": e(page["parent_href"]), "PARENT_LABEL": e(page["parent_label"]),
        "HISTORY_EYEBROW": e(page["history_eyebrow"]), "HISTORY_HEADING": e(page["history_heading"]),
        "HISTORY_PARAGRAPHS": "\n".join(f"<p>{p}</p>" for p in page["history_paragraphs"]),
        "GALLERY_EYEBROW": e(page["gallery_eyebrow"]), "GALLERY_HEADING": e(page["gallery_heading"]),
        "COLLECTION_ID": e(cid), "DOCUMENT_ACTIONS": actions,
        "DOCUMENT_DIALOG": dialog if documents else "",
        "DOCUMENT_SCRIPT": '<script src="assets/js/editorial-photo.js" defer></script>' if documents else ""
    }
    if set(FIELD.findall(tpl)) != set(fields):
        raise ValueError("Direct collection template placeholders are inconsistent")
    result = FIELD.sub(lambda m: fields[m.group(1)], tpl)
    if "{{" in result or result.count('id="photo-grid"') != 1:
        raise ValueError(f"{path}: invalid template output")
    if result.index('class="prose collection-history"') > result.index('id="photo-grid"'):
        raise ValueError(f"{path}: grid precedes the narrative")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = args.root
    manifest = json.loads((root / "data/direct-collection-pages.json").read_text(encoding="utf-8"))
    template = (root / "templates/direct-collection-page.html").read_text(encoding="utf-8")
    dialog = (root / "templates/components/editorial-document-dialog.html").read_text(encoding="utf-8")
    collections = {c["id"]: c for c in json.loads((root / "data/collections.json").read_text(encoding="utf-8"))}
    photos = json.loads((root / "data/photos.json").read_text(encoding="utf-8"))
    paths = set()
    for page in manifest["pages"]:
        if page["path"] in paths:
            raise ValueError(f"Duplicate configured page: {page['path']}")
        paths.add(page["path"])
        output = root / page["path"]
        expected = render(template, dialog, page, collections, photos)
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != expected:
                raise ValueError(f"Generated page out of date: {page['path']}")
        else:
            output.write_text(expected, encoding="utf-8")
    print(f"PASS: {len(paths)} direct collection pages "+("current" if args.check else "generated"))


if __name__ == "__main__":
    main()
