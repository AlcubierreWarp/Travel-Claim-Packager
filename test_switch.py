# Switch between production and beta from the menu, in one window. Production offers the switch only
# on a device that has opened the beta. Tab-only claims stay with their own version.
import sys, pathlib, asyncio, shutil, subprocess, time
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]).resolve(); site = base / "live/sw"; shutil.rmtree(site, ignore_errors=True)
shutil.copytree(base / "out/web", site / "Travel-Claim-Packager"); shutil.copytree(base / "out/web-beta", site / "Travel-Claim-Packager/beta")
srv = subprocess.Popen([sys.executable, str(base / "serve_cached.py"), str(site), "8768"]); time.sleep(0.8)
U = "http://localhost:8768/Travel-Claim-Packager/"
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(U); await q.wait_for_timeout(600)
        check("production hides the switch on a device that never opened the beta", await q.is_hidden("#switch-channel"))
        await q.fill("#trip-ref", "Production claim"); await q.wait_for_timeout(700)
        await q.goto(U + "beta/"); await q.wait_for_timeout(600)
        check("beta does not pick up the production tab claim", await q.input_value("#trip-ref") != "Production claim", await q.input_value("#trip-ref"))
        await q.click("#menu-btn"); check("beta shows Switch to production", (await q.inner_text("#switch-t")) == "Switch to production", await q.inner_text("#switch-t"))
        await q.fill("#trip-ref", "Beta claim") if not await q.is_visible("#menu") else None
        await q.keyboard.press("Escape"); await q.fill("#trip-ref", "Beta claim"); await q.wait_for_timeout(200)
        await q.click("#menu-btn"); await q.click("#switch-channel"); await q.wait_for_load_state(); await q.wait_for_timeout(700)
        check("lands on production", q.url == U and "beta" not in (await q.inner_text(".menu-ver")), (q.url, await q.inner_text(".menu-ver")))
        check("production claim still there", await q.input_value("#trip-ref") == "Production claim", await q.input_value("#trip-ref"))
        await q.click("#menu-btn"); check("production now offers Switch to beta", await q.is_visible("#switch-channel") and (await q.inner_text("#switch-t")) == "Switch to beta")
        await q.click("#switch-channel"); await q.wait_for_load_state(); await q.wait_for_timeout(700)
        check("lands on beta", q.url == U + "beta/" and "beta" in (await q.inner_text(".menu-ver")), q.url)
        check("beta claim kept, saved just before switching", await q.input_value("#trip-ref") == "Beta claim", await q.input_value("#trip-ref"))
        await c.close()
        # the offline single file never shows the switch
        c = await b.new_context(); q = await c.new_page(); await q.goto((base / "out/CAF_Digital_Travel_Itinerary.html").as_uri()); await q.wait_for_timeout(400)
        await q.evaluate("localStorage.setItem('caf-dti-beta-seen','1')"); await q.reload(); await q.wait_for_timeout(400)
        check("offline file has no switch", await q.is_hidden("#switch-channel"))
        print("errors:", errs); print("failures:", fails); await b.close()
try: asyncio.run(main())
finally: srv.terminate(); shutil.rmtree(base / "live", ignore_errors=True)
