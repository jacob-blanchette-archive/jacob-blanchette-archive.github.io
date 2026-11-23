#!/usr/bin/env python3
"""Browser-level regression tests for the archive's three photograph/document viewers.

Runs a local HTTP server against the checked-out public site, then exercises
real Chromium interactions. No external service, private catalog or master file
is required. This is interaction QA, not a visual or historical-content audit.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import threading

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def check_featured(page, base):
    page.goto(base + "/collections.html")
    expand = page.locator(".featured-image-expand").first
    expect(expand).to_be_visible()
    expand.click()
    dialog = page.locator(".featured-image-dialog")
    expect(dialog).to_be_visible()
    expect(dialog.locator("h2")).not_to_be_empty()
    expect(dialog.locator(".featured-image-stage img")).to_have_js_property("complete", True)
    assert dialog.locator(".featured-image-stage img").evaluate("(e) => e.naturalWidth > 0"), "Featured photograph did not decode"
    dialog.locator("summary").click()
    citation = dialog.locator(".featured-image-citation").inner_text()
    assert "Jacob Blanchette Photography Archive" in citation
    record = dialog.locator(".featured-image-record")
    expect(record).to_be_visible()
    url = record.get_attribute("href")
    assert "gallery.html?" in url and "photo=JB-" in url, url
    dialog.locator(".featured-image-copy").click()
    expect(dialog.locator(".featured-image-copy-status")).to_contain_text("Citation copied.")
    assert "Jacob Blanchette Photography Archive" in page.evaluate("navigator.clipboard.readText()")
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()
    assert expand.evaluate("(e) => document.activeElement === e"), "Featured viewer did not restore focus"
    page.locator("a.collection-card").first.click()
    expect(page).to_have_url(re.compile(r"/bfhf\\.html$"))
    print("PASS: collection featured enlargement, citation/copy, focus return, card navigation")

    page.goto(base + "/bfhf-1987.html")
    expand = page.locator(".featured-image-expand").first
    expect(expand).to_be_visible()
    expand.click()
    expect(page.locator(".featured-image-dialog")).to_be_visible()
    page.locator(".featured-image-close").click()
    expect(page.locator(".featured-image-dialog")).not_to_be_visible()
    page.locator("a.bfhf-event-photo").first.click()
    expect(page).to_have_url(re.compile(r"/gallery\\.html\\?bfhf_year=1987&event=symposium"))
    expect(page.locator("#photo-grid .photo-card").first).to_be_visible()
    print("PASS: BFHF featured photo enlargement does not intercept event navigation")


def check_editorial(page, base):
    page.goto(base + "/index.html")
    trigger = page.locator(".editorial-photo-trigger").first
    trigger.click()
    dialog = page.locator("#editorial-photo-dialog")
    expect(dialog).to_be_visible()
    expect(dialog.locator("#editorial-photo-title")).to_contain_text("Jacob Blanchette")
    dialog.locator("summary").click()
    assert "Photographer not established" in dialog.locator("#editorial-photo-citation").inner_text()
    expect(dialog.locator("#editorial-photo-record")).to_be_hidden()
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()
    assert trigger.evaluate("(e) => document.activeElement === e"), "Editorial portrait did not restore focus"
    print("PASS: homepage editorial portrait, unknown creator, hidden record link, focus return")

    page.goto(base + "/bfhf-1987.html")
    trigger = page.locator(".editorial-photo-trigger").first
    trigger.click()
    dialog = page.locator("#editorial-photo-dialog")
    expect(dialog).to_be_visible()
    expect(dialog.locator("#editorial-photo-title")).to_contain_text("1987")
    dialog.locator("summary").click()
    citation = dialog.locator("#editorial-photo-citation").inner_text()
    assert "Creator not established" in citation and "JB-000105" in citation, citation
    record = dialog.locator("#editorial-photo-record")
    expect(record).to_be_visible()
    assert "photo=JB-000105" in record.get_attribute("href")
    dialog.locator("#editorial-photo-copy").click()
    expect(dialog.locator("#editorial-copy-status")).to_contain_text("Citation copied.")
    dialog.locator("#editorial-photo-close").click()
    expect(dialog).not_to_be_visible()
    assert trigger.evaluate("(e) => document.activeElement === e"), "Document viewer did not restore focus"
    print("PASS: BFHF document viewer, creator/date citation, record link and copy")


def check_gallery(page, base):
    page.goto(base + "/gallery.html?collection=bfhf-pilot")
    first = page.locator("#photo-grid .photo-card").first
    expect(first).to_be_visible()
    first.click()
    dialog = page.locator("#photo-dialog")
    expect(dialog).to_be_visible()
    expect(dialog.locator("#viewer-photo-id")).to_contain_text("JB-000024")
    assert "photo=JB-000024" in page.url
    expect(dialog.locator("#viewer-comparison")).to_be_visible()
    dialog.locator("#view-source").click()
    expect(dialog.locator("#view-source")).to_have_attribute("aria-pressed", "true")
    assert "/as-found/" in dialog.locator("#viewer-stage img").get_attribute("src")
    dialog.locator("#view-presentation").click()
    expect(dialog.locator("#view-presentation")).to_have_attribute("aria-pressed", "true")
    dialog.locator("#viewer-citation summary").click()
    citation = dialog.locator("#viewer-citation-text").inner_text()
    assert "JB-000024" in citation and "Jacob Blanchette Photography Archive" in citation
    dialog.locator("#viewer-copy-citation").click()
    expect(dialog.locator("#viewer-copy-status")).to_contain_text("Citation copied.")
    dialog.locator("#viewer-next").click()
    expect(dialog.locator("#viewer-photo-id")).not_to_contain_text("JB-000024")
    page.keyboard.press("ArrowLeft")
    expect(dialog.locator("#viewer-photo-id")).to_contain_text("JB-000024")
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()
    assert "photo=" not in page.url
    print("PASS: gallery viewer, source comparison, citation/copy, arrows, Escape and URL cleanup")

    page.goto(base + "/gallery.html?collection=bfhf-pilot&photo=JB-000025")
    expect(page.locator("#photo-dialog")).to_be_visible()
    expect(page.locator("#viewer-photo-id")).to_contain_text("JB-000025")
    page.locator("#viewer-close").click()
    expect(page.locator("#photo-dialog")).not_to_be_visible()
    page.locator("#gallery-search").fill("JB-000025")
    expect(page.locator("#results-count")).to_contain_text("1 of")
    expect(page.locator("#photo-grid .photo-card")).to_have_count(1)
    print("PASS: deep-linked photograph, viewer close and gallery search")

    page.goto(base + "/gallery.html?collection=brg-1990")
    page.locator("#photo-grid .photo-card").first.click()
    expect(page.locator("#photo-dialog")).to_be_visible()
    expect(page.locator("#viewer-comparison")).to_be_hidden()
    print("PASS: no source-comparison controls when source representation is unavailable")


def check_mobile(browser, base):
    context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + "/collections.html")
    page.locator(".featured-image-expand").first.click()
    expect(page.locator(".featured-image-dialog")).to_be_visible()
    page.locator(".featured-image-close").click()
    expect(page.locator(".featured-image-dialog")).not_to_be_visible()
    assert not errors, "Mobile JavaScript errors: " + "; ".join(errors)
    context.close()
    print("PASS: narrow mobile viewport featured viewer open/close (interaction only)")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                permissions=["clipboard-read", "clipboard-write"],
            )
            page = context.new_page()
            page.set_default_timeout(15000)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            check_featured(page, base)
            check_editorial(page, base)
            check_gallery(page, base)
            assert not errors, "JavaScript page errors: " + "; ".join(errors)
            context.close()
            check_mobile(browser, base)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("PASS: all viewer interaction checks completed")


if __name__ == "__main__":
    main()
