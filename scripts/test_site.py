"""End-to-end browser tests for the Artemis website.

Runs headless Chromium (Playwright) against a running copy of the site and
checks every page, every internal link, the menu, the forms and the lab flow.
It saves desktop and phone screenshots for review.

    python scripts/test_site.py http://127.0.0.1:8800 --access-code CODE --shots runs/site_test

Against a local server whose Omnigent is the scripted test double, add
--full-run to start a proposal run, watch it stream, and check that it is
saved and published. Against the live site, leave --full-run off unless you
mean to spend a real run.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Page, sync_playwright

PAGES = ["/", "/lab", "/results", "/method", "/about", "/results/solar-absorbers-2026-10-03", "/status",
         "/results/run?id=doesnotexist", "/a-page-that-does-not-exist"]


class Report:
    """Collects pass/fail lines and prints a summary."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes = 0

    def check(self, ok: bool, label: str, detail: str = "") -> bool:
        if ok:
            self.passes += 1
            print(f"  PASS  {label}")
        else:
            self.failures.append(f"{label}: {detail}")
            print(f"  FAIL  {label}  {detail}")
        return ok


def collect_errors(page: Page, bucket: list[str]) -> None:
    page.on("console", lambda m: bucket.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: bucket.append(f"page error: {e}"))


def test_pages(page: Page, base: str, r: Report, shots: Path, label: str) -> set[str]:
    """Load each page, check basics, take a screenshot, return links found."""
    links: set[str] = set()
    for path in PAGES:
        errors: list[str] = []
        collect_errors(page, errors)
        response = page.goto(base + path, wait_until="networkidle")
        status = response.status if response else 0
        expect = 404 if "does-not-exist" in path else 200
        r.check(status == expect, f"{label} {path} answers {expect}", f"got {status}")
        title = page.title()
        r.check(bool(title) and "Artemis" in title, f"{label} {path} has a title", title)
        h1 = page.locator("h1").count()
        r.check(h1 == 1, f"{label} {path} has exactly one h1", str(h1))
        if "does-not-exist" not in path and "run?" not in path and path != "/status":
            desc = page.locator('meta[name="description"]').get_attribute("content") or ""
            r.check(70 <= len(desc) <= 200, f"{label} {path} description length {len(desc)}", desc[:60])
            canonical = page.locator('link[rel="canonical"]').get_attribute("href") or ""
            r.check(canonical.endswith(path) or (path == "/" and canonical.endswith("/")), f"{label} {path} canonical", canonical)
            for block in page.locator('script[type="application/ld+json"]').all():
                try:
                    json.loads(block.inner_text())
                    ok = True
                except ValueError:
                    ok = False
                r.check(ok, f"{label} {path} JSON-LD parses")
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        r.check(overflow <= 1, f"{label} {path} no sideways scrolling", f"{overflow}px")
        imgs_without_alt = page.evaluate("Array.from(document.images).filter(i => !i.hasAttribute('alt')).length")
        r.check(imgs_without_alt == 0, f"{label} {path} images have alt text", str(imgs_without_alt))
        unnamed = page.evaluate("""Array.from(document.querySelectorAll('a,button')).filter(e => {
            const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden') return false;
            return !(e.innerText.trim() || e.getAttribute('aria-label'));}).length""")
        r.check(unnamed == 0, f"{label} {path} buttons and links have names", str(unnamed))
        page.wait_for_timeout(600)
        page.screenshot(path=str(shots / f"{label}{path.replace('/', '_').replace('?', '_') or '_home'}.png"), full_page=True)
        real_errors = [e for e in errors if "404" not in e and "Failed to load resource" not in e]
        r.check(not real_errors, f"{label} {path} no script errors", "; ".join(real_errors)[:300])
        if "does-not-exist" in path:
            continue
        for href in page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))"):
            links.add(urljoin(base + path, href))
    return links


def test_links(page: Page, base: str, links: set[str], r: Report) -> list[str]:
    """Every internal link answers 200 and every #anchor exists; returns external links."""
    external = []
    host = urlparse(base).netloc
    for link in sorted(links):
        parsed = urlparse(link)
        if parsed.scheme in ("mailto", "tel"):
            continue
        if parsed.netloc != host:
            external.append(link)
            continue
        resp = page.request.get(link.split("#")[0])
        r.check(resp.status == 200, f"link {parsed.path}{'?' + parsed.query if parsed.query else ''}", str(resp.status))
        if parsed.fragment:
            page.goto(link.split("#")[0], wait_until="domcontentloaded")
            exists = page.locator(f"#{parsed.fragment}").count() > 0
            r.check(exists, f"anchor #{parsed.fragment} on {parsed.path}")
    return sorted(set(external))


def test_interactions(page: Page, base: str, r: Report, access_code: str, full_run: bool, shots: Path) -> None:
    # Home: chart draws 80 dots and shows a tooltip on hover.
    page.goto(base + "/", wait_until="networkidle")
    page.wait_for_selector(".strip-chart .dot")
    dots = page.locator(".strip-chart .dot").count()
    r.check(dots == 80, "home chart draws 80 dots", str(dots))
    page.locator(".strip-chart .dot").nth(70).dispatch_event("mouseenter")
    tip = page.locator(".chart-tip")
    r.check(tip.is_visible() and "Artemis method" in tip.inner_text(), "chart tooltip on hover", tip.inner_text() if tip.count() else "")
    canvas = page.locator("#lattice canvas").count()
    r.check(canvas == 1, "home Three.js lattice renders a canvas", str(canvas))
    page.click("text=Read the first result")
    r.check(page.url.endswith("/results/solar-absorbers-2026-10-03"), "hero button opens the result", page.url)

    # Result page: contents link scrolls, report expands, tables present.
    page.click(".toc a[href='#recommendations']")
    page.wait_for_timeout(400)
    r.check(page.url.endswith("#recommendations"), "contents link jumps to a section", page.url)
    rows = page.locator("#recommendations tbody tr").count()
    r.check(rows == 15, "recommendations table has 15 materials", str(rows))
    page.click("details.report > summary")
    r.check(page.locator("details.report[open]").count() == 1, "full lab report expands")

    # Lab page: validation messages.
    page.goto(base + "/lab", wait_until="networkidle")
    page.click("#start-button")
    r.check("at least a sentence" in page.inner_text("#form-status"), "lab asks for a question first", page.inner_text("#form-status"))
    page.fill("#question", "Which porous frameworks could capture carbon dioxide from air most efficiently?")
    page.click("#start-button")
    r.check("access code" in page.inner_text("#form-status"), "lab asks for the access code", page.inner_text("#form-status"))
    page.check("input[value=solar]")
    r.check(not page.is_visible("#question"), "question box hides for the flagship program")
    page.check("input[value=proposal]")
    page.fill("#access-code", "wrong-code")
    page.click("#start-button")
    page.wait_for_function("document.getElementById('form-status').textContent.includes('not correct')", timeout=10000)
    r.check(True, "lab rejects a wrong access code")

    if full_run:
        dialogs: list[str] = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
        page.fill("#access-code", access_code)
        page.click("#start-button")
        page.wait_for_function("document.querySelector('#stages li[data-stage=done]').dataset.state === 'done'", timeout=90000)
        r.check(True, "proposal run streams to completion and is published")
        r.check("carbon capture" in page.inner_text("#feed").lower(), "live feed shows the agent's text")
        r.check("ARTEMIS-RUN-COMPLETE" not in page.inner_text("#feed"), "completion marker hidden from visitors")
        page.screenshot(path=str(shots / "flow_lab_finished.png"), full_page=True)
        href = page.get_attribute("#result-link", "href")
        page.click("#result-link")
        page.wait_for_selector("#run-body .prose h3", timeout=15000)
        r.check(page.url.endswith(href), "result link opens the saved run", page.url)
        scripts = page.evaluate("document.querySelectorAll('#run-body script, #run-body [onerror], #run-body iframe').length")
        r.check(scripts == 0 and not dialogs, "saved report never runs injected script", f"{scripts} elements, dialogs {dialogs}")
        hrefs = page.evaluate("Array.from(document.querySelectorAll('#run-body a')).map(a => a.getAttribute('href'))")
        r.check(all(h.startswith(("https://", "http://", "/", "#", "mailto:")) for h in hrefs), "only safe links are clickable", str(hrefs))
        r.check(page.locator("#run-body table.data").count() == 1, "report table renders")
        page.screenshot(path=str(shots / "flow_saved_run.png"), full_page=True)
        page.goto(base + "/results", wait_until="networkidle")
        page.wait_for_function("document.querySelectorAll('#result-list li').length >= 1", timeout=10000)
        r.check(True, "results list shows the new saved run")

    # Status page: live checks fill in.
    page.goto(base + "/status", wait_until="networkidle")
    page.wait_for_function("document.querySelector('[data-hop=website] [data-state]').textContent !== 'checking'", timeout=15000)
    r.check(page.inner_text("[data-hop=website] [data-state]") == "working", "status shows the website working")

    # Unknown saved run.
    page.goto(base + "/results/run?id=doesnotexist", wait_until="networkidle")
    page.wait_for_timeout(800)
    r.check("No saved run" in page.inner_text("#run-body"), "unknown run shows a helpful message", page.inner_text("#run-body")[:80])


def test_mobile_menu(browser, base: str, r: Report, shots: Path) -> set[str]:
    context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = context.new_page()
    links = test_pages(page, base, r, shots, "phone")
    page.goto(base + "/", wait_until="networkidle")
    r.check(page.is_visible(".menu-toggle"), "phone shows the Menu button")
    r.check(not page.is_visible("#site-nav a[href='/method']"), "phone menu starts closed")
    page.click(".menu-toggle")
    r.check(page.is_visible("#site-nav a[href='/method']"), "Menu button opens the menu")
    page.screenshot(path=str(shots / "phone_menu_open.png"))
    page.click("#site-nav a[href='/method']")
    page.wait_for_load_state("networkidle")
    r.check(page.url.endswith("/method"), "menu link navigates", page.url)
    page.click(".menu-toggle")
    page.keyboard.press("Escape")
    r.check(not page.is_visible("#site-nav a[href='/about']"), "Escape closes the menu")
    context.close()
    return links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base")
    parser.add_argument("--access-code", default="")
    parser.add_argument("--full-run", action="store_true")
    parser.add_argument("--shots", default="runs/site_test")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    shots = Path(args.shots)
    shots.mkdir(parents=True, exist_ok=True)
    r = Report()
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        print("Desktop pages")
        links = test_pages(page, base, r, shots, "desktop")
        print("Phone pages and menu")
        links |= test_mobile_menu(browser, base, r, shots)
        print("Links")
        external = test_links(page, base, links, r)
        print("Interactions")
        test_interactions(page, base, r, args.access_code, args.full_run, shots)
        browser.close()
    (shots / "external_links.txt").write_text("\n".join(external) + "\n", encoding="utf-8")
    print(f"\n{r.passes} checks passed, {len(r.failures)} failed. External links to verify: {len(external)} "
          f"(listed in {shots / 'external_links.txt'}).")
    for f in r.failures:
        print("  - " + f)
    return 0 if not r.failures else 1


if __name__ == "__main__":
    sys.exit(main())
