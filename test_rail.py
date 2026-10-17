import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base/"shots"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(**{k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"}); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(500)
        H = await q.evaluate("document.documentElement.scrollHeight - innerHeight")
        for f in [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1]:
            await q.evaluate(f"scrollTo(0, {int(H*f)})"); await q.wait_for_timeout(120)
            print(f"{f:.1f} scrollLeft={await q.evaluate('Math.round(rail.scrollLeft)')} here={await q.eval_on_selector('#rail .here .nm', 'e => e.textContent')}")
            if f in (.5,): await q.screenshot(path=str(shots/"rail-mid.png"))
        # desktop highlight only
        d = await b.new_context(viewport={"width":1320,"height":900}); r = await d.new_page(); await r.goto(url); await r.wait_for_timeout(400)
        await r.evaluate("scrollTo(0, 2500)"); await r.wait_for_timeout(150)
        print("desktop here:", await r.eval_on_selector('#rail .here .nm', 'e => e.textContent'))
        print("errors:", errs); await b.close()
asyncio.run(main())
