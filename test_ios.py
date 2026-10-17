import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()
STUB = """Object.defineProperty(navigator,'standalone',{get:()=>window.__standalone}); navigator.canShare = d => !!(d && d.files); window.__shares=[]; navigator.share = async d => { window.__shares.push(d.files[0].name + ' files=' + d.files.length + ' text=' + (d.text !== undefined) + ' title=' + (d.title !== undefined)); };"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        dev = {k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"}
        for standalone in (True, False):
            c = await b.new_context(**dev, accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            downloads = []; q.on("download", lambda d: downloads.append(d.suggested_filename))
            await q.add_init_script(f"window.__standalone={'true' if standalone else 'false'};" + STUB); await q.goto(url); await q.wait_for_timeout(500)
            await q.click("[data-act=review]"); await q.wait_for_timeout(300); await q.click("#build-btn"); await q.wait_for_timeout(2500)
            print(f"standalone={standalone} after build: downloads={downloads} shares={await q.evaluate('window.__shares')}")
            print("  result:", (await q.inner_text("#result")).replace("\n"," | ")[:260])
            print("  buttons:", await q.eval_on_selector_all("#result .acts button", "els => els.map(e => e.textContent)"))
            await q.click("#result .acts button.primary"); await q.wait_for_timeout(800)
            print("  after Save PDF: downloads", downloads, "| shares", await q.evaluate("window.__shares"))
            await q.click("#menu-btn")
            print("  menu:", await q.eval_on_selector_all("#menu > button", "els => els.filter(e => !e.hidden).map(e => e.textContent)"))
            await q.click("#menu > button:not([hidden])[data-act$=draft]:not([data-act=open-draft])"); await q.wait_for_timeout(800)
            print("  after Save draft: downloads", downloads, "| shares", await q.evaluate("window.__shares"))
            await c.close()
        print("errors:", errs); await b.close()
asyncio.run(main())
