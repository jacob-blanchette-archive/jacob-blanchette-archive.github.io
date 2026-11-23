#!/usr/bin/env python3
"""Validate public photograph metadata without exposing the private catalog."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import re

REQUIRED = ("id", "collection_id", "title", "caption", "image", "alt", "photographer")
WITHDRAWN = {"JB-000002", "JB-000004", "JB-000007", "JB-000009", "JB-000011", "JB-000015"}
ID = re.compile(r"JB-\d{6}$")

def check(root: Path):
    photos = json.loads((root / "data/photos.json").read_text(encoding="utf-8"))
    collections = json.loads((root / "data/collections.json").read_text(encoding="utf-8"))
    known = {c["id"] for c in collections}
    errors = []
    counts = Counter(p.get("id") for p in photos)
    for photo in photos:
        pid = photo.get("id", "<missing>")
        if not ID.fullmatch(pid): errors.append(f"{pid}: invalid archival ID")
        if counts[pid] > 1: errors.append(f"{pid}: duplicate public ID")
        if pid in WITHDRAWN: errors.append(f"{pid}: withdrawn ID is published")
        if photo.get("published") is not True: errors.append(f"{pid}: not marked published")
        if photo.get("collection_id") not in known: errors.append(f"{pid}: unknown public collection")
        for key in REQUIRED:
            if not isinstance(photo.get(key), str) or not photo[key].strip():
                errors.append(f"{pid}: missing {key}")
        for key in ("image", "source_image"):
            value = photo.get(key)
            if value and not (root / value).is_file():
                errors.append(f"{pid}: missing {key} file: {value}")
        if photo.get("source_image") and not photo.get("source_label"):
            errors.append(f"{pid}: source image lacks source label")
    print(f"Public metadata: {len(photos)} records, {len(known)} collection definitions, {len(errors)} issues")
    for issue in errors[:100]: print(" -", issue)
    if errors: raise SystemExit(1)
    print("PASS: public IDs, collection assignments, required fields, withdrawal exclusions and referenced files")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root)
if __name__ == "__main__": main()
