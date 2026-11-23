#!/usr/bin/env python3
"""Check local website links, fragments, HTML/CSS assets, and public image references."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ASSET_FIELDS = {"src", "poster"}
LINK_TAGS = {"a", "area"}
RESOURCE_TAGS = {"link", "script", "img", "source", "video", "audio", "iframe"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "blob:")
CSS_URL = re.compile(r'''url\(\s*['"]?([^)'"]+)''', re.I)

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"): self.ids.add(a["id"])
        for key in ("href", "src", "poster", "srcset"):
            if not a.get(key): continue
            if key == "href" and tag not in LINK_TAGS | {"link"}: continue
            if key in ASSET_FIELDS and tag not in RESOURCE_TAGS: continue
            if key == "srcset" and tag not in {"img", "source"}: continue
            if key == "srcset":
                for entry in a[key].split(","):
                    if entry.strip(): self.refs.append((tag, key, entry.strip().split()[0]))
            else: self.refs.append((tag, key, a[key]))
    handle_startendtag = handle_starttag

def check(root: Path):
    errors = []
    counts = {"html_pages": 0, "html_references": 0, "css_references": 0, "manifest_images": 0}
    pages = {}
    for page in root.rglob("*.html"):
        if ".git" in page.parts or "templates" in page.relative_to(root).parts: continue
        doc = Scan()
        doc.feed(page.read_text(encoding="utf-8"))
        pages[page.resolve()] = doc
        counts["html_pages"] += 1

    def resolve(origin: Path, ref: str, fragment: bool = True):
        ref = ref.strip()
        if not ref or ref.startswith(("//", *SKIP_SCHEMES)): return
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc: return
        raw = unquote(parsed.path)
        if raw.startswith("/"):
            # GitHub Pages project root; only local absolute links are in scope.
            dest = root / raw.lstrip("/")
        else: dest = origin.parent / raw if raw else origin
        if raw.endswith("/"): dest /= "index.html"
        if dest.is_dir(): dest /= "index.html"
        try: dest = dest.resolve()
        except OSError: errors.append(f"{origin.relative_to(root)}: invalid path {ref}"); return
        if not dest.is_relative_to(root.resolve()):
            errors.append(f"{origin.relative_to(root)}: path escapes site root: {ref}"); return
        if not dest.is_file():
            errors.append(f"{origin.relative_to(root)}: missing target: {ref}"); return
        if fragment and parsed.fragment and dest.suffix == ".html":
            target = pages.get(dest)
            if target and unquote(parsed.fragment) not in target.ids:
                errors.append(f"{origin.relative_to(root)}: missing fragment: {ref}")

    for page, doc in pages.items():
        for tag, key, ref in doc.refs:
            counts["html_references"] += 1
            resolve(page, ref, fragment=(key == "href" and tag in LINK_TAGS))

    for css in root.rglob("*.css"):
        for ref in CSS_URL.findall(css.read_text(encoding="utf-8")):
            counts["css_references"] += 1
            resolve(css, ref, fragment=False)

    manifest = root / "data/photos.json"
    if manifest.is_file():
        for row in json.loads(manifest.read_text(encoding="utf-8")):
            for field in ("image", "source_image"):
                if row.get(field):
                    counts["manifest_images"] += 1
                    resolve(root / "index.html", row[field], fragment=False)

    return counts, errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    counts, errors = check(args.root.resolve())
    print("Site integrity scan:", ", ".join(f"{k}={v}" for k,v in counts.items()))
    if errors:
        print(f"{len(errors)} broken references:")
        for err in errors[:100]: print(" -", err)
        if len(errors)>100: print(f" ... {len(errors)-100} additional errors")
        raise SystemExit(1)
    print("PASS: no broken local references or HTML fragments found.")

if __name__ == "__main__": main()
