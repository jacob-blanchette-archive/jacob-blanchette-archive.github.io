#!/usr/bin/env python3
"""Guard the site's semantic section-spacing contract.

Run: python3 scripts/check_spacing_contract.py [--root SITE_ROOT]
Static checks complement, but do not replace, visual desktop/mobile review.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re


def source(root: Path, path: str) -> str:
    file = root / path
    if not file.is_file():
        raise ValueError(f"Missing file: {path}")
    return file.read_text(encoding="utf-8")


def need(haystack: str, needle: str, location: str) -> None:
    if needle not in haystack:
        raise ValueError(f"{location}: missing spacing contract: {needle}")


def check(root: Path) -> None:
    shared = source(root, "assets/css/curatorial.css")
    home = source(root, "assets/css/home.css")
    themes = source(root, "assets/css/collections.css")
    home_themes = source(root, "assets/css/home-collections.css")
    bio = source(root, "assets/css/biography.css")
    interior = source(root, "assets/css/site.css")

    # Single shared major-section value on desktop and mobile.
    need(shared, "--space-major-section: 72px;", "curatorial.css")
    need(shared, "--space-major-section: 56px;", "curatorial.css")
    need(shared, "--space-internal-divider: 40px;", "curatorial.css")
    need(shared, "--space-internal-divider: 32px;", "curatorial.css")
    need(shared, "--space-chapter-divider: 56px;", "curatorial.css")
    need(shared, "--space-chapter-divider: 44px;", "curatorial.css")
    need(shared, "--space-internal-divider-half: calc(var(--space-internal-divider) / 2);", "curatorial.css")
    need(shared, "--space-chapter-divider-half: calc(var(--space-chapter-divider) / 2);", "curatorial.css")

    # Every site page must load the shared tokens after its structural CSS.
    for path in ("index.html", "collections.html", "biography.html"):
        page = source(root, path)
        styles = re.findall(r'<link[^>]+href="(assets/css/[^"]+\.css)"', page)
        if "assets/css/curatorial.css" not in styles:
            raise ValueError(f"{path}: missing shared curatorial styles")
        if path != "biography.html" and (
            "assets/css/collection-previews.css" not in styles
            or styles.index("assets/css/collection-previews.css")
            < styles.index("assets/css/curatorial.css")
        ):
            raise ValueError(f"{path}: collection preview stylesheet order changed")

    # Home's major bands use the common inset; inner home themes use a smaller divider.
    need(home, ".section{padding:var(--space-major-section) 0}", "home.css")
    need(home_themes,
         "margin-top:var(--space-internal-divider-half);padding-top:var(--space-internal-divider-half)",
         "home-collections.css")

    # Collections must not add another outer content inset around the theme sections.
    need(themes, ".content.collection-themes { padding: 0;", "collections.css")
    need(themes, ".theme-section { padding: var(--space-major-section) 0;", "collections.css")
    need(themes, ".theme-section:not(:last-child) { padding-bottom: var(--space-internal-divider-half); }", "collections.css")
    need(themes, ".theme-section + .theme-section { padding-top: var(--space-internal-divider-half); }", "collections.css")
    need(themes, ".theme-section:last-child { border-bottom: 0; }", "collections.css")
    if re.search(r"\.theme-section:last-child\s*\{[^}]*padding", themes):
        raise ValueError("collections.css: last theme has ad-hoc padding override")

    # Biography major bands share the inset, internal chapters retain a distinct role.
    for selector in (".bio-lead", ".bio-career", ".bio-end"):
        need(bio, selector + "{padding:var(--space-major-section) 0", "biography.css")
    need(bio, "margin-top:var(--space-internal-divider-half);padding-top:var(--space-internal-divider-half)", "biography.css")
    need(bio, "margin:var(--space-chapter-divider-half) 0 22px;padding-top:var(--space-chapter-divider-half)", "biography.css")

    # Other collection/event pages deliberately continue to use their own token.
    need(interior, ".section{padding:var(--space-section) 0}", "site.css")
    for path, css in {
        "home.css": home, "collections.css": themes,
        "home-collections.css": home_themes, "biography.css": bio
    }.items():
        if re.search(r"\b(?:padding|margin(?:-top)?)\s*:\s*(?:7[02]|56)px\s+0\b", css):
            raise ValueError(f"{path}: major padding must use a semantic token")
        for obsolete in (
            "--space-section-home", "--space-theme-top", "--space-theme-bottom",
            "--space-home-theme-gap", "--space-bio-lead-top",
            "--space-bio-career-top", "--space-bio-story-gap"
        ):
            if obsolete in css:
                raise ValueError(f"{path}: obsolete token {obsolete}")
    for path, css in {
        "curatorial.css": shared, "home.css": home, "collections.css": themes,
        "home-collections.css": home_themes, "biography.css": bio
    }.items():
        if css.count("{") != css.count("}"):
            raise ValueError(f"{path}: CSS brace count mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        check(args.root)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print("PASS: shared major sections, internal dividers and mobile tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
