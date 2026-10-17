import asyncio, shutil, pathlib, re, sys
base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")  # run through test_live.py
from playwright.async_api import async_playwright
U = "http://localhost:8767/Travel-Claim-Packager/"; root = base / "live/s3/Travel-Claim-Packager"  # starts as the live production site
async def ver(pg): return await pg.evaluate("() => (document.querySelector('.menu-ver') || document.querySelector('#app-ver') || {}).textContent")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        dev = {k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"}
        A = await b.new_context(**dev); a = await A.new_page(); a.on("pageerror", lambda e: errs.append(str(e)))
        await a.goto(U); await a.evaluate("navigator.serviceWorker.ready.then(r => r.scope)"); await a.reload(); await a.wait_for_timeout(600)
        await a.click("#menu-btn"); await a.click("#opt-keep"); await a.keyboard.press("Escape"); await a.wait_for_timeout(300)
        await a.fill("#trip-ref", "Kept upgrade test"); await a.wait_for_timeout(1800)
        B = await b.new_context(**dev); bb = await B.new_page()
        await bb.goto(U); await bb.wait_for_timeout(600); await bb.fill("#trip-ref", "Tab only upgrade test"); await bb.wait_for_timeout(1200)
        print("before:", await ver(a), "| kept:", await a.input_value("#trip-ref"), "| tab only:", await bb.input_value("#trip-ref"))
        # publish the next production build
        for f in (base / "out/web").iterdir(): shutil.copy(f, root / f.name)
        s = re.sub(r"(Version \d+\.\d+), updated", r"\1 TEST, updated", (root / "index.html").read_text()); (root / "index.html").write_text(s)
        (root / "sw.js").write_text((root / "sw.js").read_text().replace("const CACHE = PREFIX + '", "const CACHE = PREFIX + 'next-"))
        # A: app closed and reopened
        await a.close(); a2 = await A.new_page(); a2.on("pageerror", lambda e: errs.append(str(e)))
        await a2.goto(U); await a2.wait_for_timeout(1200)
        print("A reopen 1:", await ver(a2), "| trip:", await a2.input_value("#trip-ref"))
        await a2.close(); a3 = await A.new_page(); await a3.goto(U); await a3.wait_for_timeout(1200)
        print("A reopen 2:", await ver(a3), "| trip:", await a3.input_value("#trip-ref"))
        await a3.reload(); await a3.wait_for_timeout(1500)
        print("A after reload:", await ver(a3), "| trip:", await a3.input_value("#trip-ref"), "| keep on:", await a3.eval_on_selector("#opt-keep", "e => e.checked"))
        await a3.close(); a4 = await A.new_page(); await a4.goto(U); await a4.wait_for_timeout(1200)
        print("A reopen 3:", await ver(a4), "| trip:", await a4.input_value("#trip-ref"))
        # B: same session reload (pull to refresh / app kept in memory)
        await bb.reload(); await bb.wait_for_timeout(1200)
        print("B reload:", await ver(bb), "| trip:", await bb.input_value("#trip-ref"))
        print("errors:", errs); await b.close()
asyncio.run(main())
