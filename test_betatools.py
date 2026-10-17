# Beta-only tools: Load test data (every section and feature) and Reset the beta. Both sit at the
# bottom of the menu with help, feedback and the version switch, and do not exist in production.
import sys, pathlib, asyncio, shutil, subprocess, time
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]).resolve(); site = base / "live/bt"; shutil.rmtree(site, ignore_errors=True)
shutil.copytree(base / "out/web", site / "Travel-Claim-Packager"); shutil.copytree(base / "out/web-beta", site / "Travel-Claim-Packager/beta")
srv = subprocess.Popen([sys.executable, str(base / "serve_cached.py"), str(site), "8769"]); time.sleep(0.8)
U = "http://localhost:8769/Travel-Claim-Packager/"
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
MENU = "() => [...document.querySelectorAll('#menu > *')].filter(e => !e.hidden && e.tagName !== 'HR' && !e.classList.contains('menu-note')).map(e => (e.querySelector('.mi-t') || e).textContent.trim()).slice(-6)"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        # production: keep a claim on the device, then check the beta tools are absent
        await q.goto(U); await q.wait_for_timeout(600)
        await q.click("[data-act=start-blank]"); await q.fill("#trip-ref", "Production kept claim"); await q.click("[data-act=hide-notice]")
        await q.click("#menu-btn"); await q.check("#opt-keep"); await q.keyboard.press("Escape"); await q.click("#save-now"); await q.wait_for_timeout(500)
        check("production has no beta tools", await q.locator("#beta-reset, #beta-testdata").count() == 0)
        # beta
        await q.goto(U + "beta/"); await q.wait_for_timeout(700)
        check("beta: own first-run state (example claim and notice, whatever production did)", await q.input_value("#trip-ref") == "Winnipeg course" and await q.is_visible("#localonly"), await q.input_value("#trip-ref"))
        await q.click("[data-act=hide-notice]"); await q.click("[data-act=start-blank]")
        await q.click("#menu-btn"); order = await q.evaluate(MENU); print("  beta menu bottom:", order)
        check("beta: tools at the bottom with help, feedback and the switch", order == ["Get help", "Send feedback", "Beta testing", "Load test data", "Reset the beta", "Switch to production"], order)
        await q.keyboard.press("Escape"); await q.fill("#trip-ref", "Before test data"); await q.wait_for_timeout(200)
        await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
        cnt = await q.evaluate("() => ({ stops: document.querySelectorAll('#itin input.city').length, tr: document.querySelectorAll('#rows-transport .row').length, st: document.querySelectorAll('#rows-stays .stay').length, gen: document.querySelectorAll('#rows-general .row').length, fx: document.querySelectorAll('#rows-exchange .row').length, calls: document.querySelectorAll('#rows-calls .row').length, sd: document.querySelectorAll('#sd-items > li').length, edited: document.querySelectorAll('#sd-items .sd-it-h .tag').length, poc: document.getElementById('poc-on').checked, refs: !document.getElementById('trip-refs').hidden })")
        print("  test data:", cnt)
        check("test data fills every section", cnt == {"stops": 9, "tr": 5, "st": 3, "gen": 2, "fx": 2, "calls": 2, "sd": 4, "edited": 1, "poc": True, "refs": True}, cnt)
        status = await q.inner_text(".barstatus"); print("  status:", status, await q.inner_text("#checks"))
        await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
        async with q.expect_download() as dl: await q.click("#build-btn")
        check("test data builds the one-PDF package", (await dl.value).suggested_filename.endswith(".pdf"))
        await q.check("#pk-split"); await q.click("#build-btn"); await q.wait_for_selector(".part-list li")
        check("test data builds separate files (worksheet, receipts, 4 declarations)", await q.locator(".part-list li").count() == 6, await q.locator(".part-list li").count())
        await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(800)
        await q.click("#toast button"); await q.wait_for_timeout(400)
        # undo of the second load returns the first test data; load once more from a known claim
        await q.fill("#trip-ref", "Before test data"); await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(800); await q.click("#toast button"); await q.wait_for_timeout(400)
        check("Undo brings the previous claim back", await q.input_value("#trip-ref") == "Before test data", await q.input_value("#trip-ref"))
        # reset: keep a beta claim, then reset
        await q.click("#menu-btn"); await q.check("#opt-keep"); await q.check("#opt-remember"); await q.keyboard.press("Escape"); await q.click("#save-now"); await q.wait_for_timeout(600)
        dbs = await q.evaluate("indexedDB.databases().then(d => d.map(x => x.name).sort())"); print("  databases before:", dbs)
        await q.click("#menu-btn"); await q.click("#beta-reset"); check("reset asks for a second tap", (await q.inner_text("#beta-reset-t")) == "Tap again to reset the beta")
        await q.click("#beta-reset"); await q.wait_for_load_state(); await q.wait_for_timeout(1500)
        t = await q.inner_text("#toast"); check("after reset: says it was reset", "The beta was reset" in t, t)
        check("after reset: beta claim gone", await q.input_value("#trip-ref") != "Before test data", await q.input_value("#trip-ref"))
        check("after reset: example claim is back", await q.input_value("#trip-ref") == "Winnipeg course", await q.input_value("#trip-ref"))
        check("after reset: local-only notice is back", await q.is_visible("#localonly"))
        check("after reset: keep-on-this-device question is back", await q.is_visible("#keep-banner"))
        ls = await q.evaluate("() => Object.keys(localStorage).filter(k => k.endsWith('-beta')).sort()")
        check("after reset: no beta preferences left", ls == [], ls)
        await q.click("#menu-btn"); check("after reset: Keep and Remember are off", not await q.is_checked("#opt-keep") and not await q.is_checked("#opt-remember")); await q.keyboard.press("Escape")
        await q.goto(U); await q.wait_for_timeout(900)
        check("production claim untouched by the beta reset", await q.input_value("#trip-ref") == "Production kept claim", await q.input_value("#trip-ref"))
        check("production notice stays hidden after the beta reset", not await q.is_visible("#localonly"))
        await q.click("#menu-btn"); order = await q.evaluate(MENU); print("  production menu bottom:", order)
        check("production: switch sits under Send feedback", order[-3:] == ["Get help", "Send feedback", "Switch to beta"], order)
        print("errors:", errs); print("failures:", fails); await b.close()
try: asyncio.run(main())
finally: srv.terminate(); shutil.rmtree(base / "live", ignore_errors=True)
