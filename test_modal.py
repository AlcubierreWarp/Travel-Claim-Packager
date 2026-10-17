# Open dialogs hold the screen: the page behind does not scroll, and closing returns to the same place.
import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs, fails = [], []
        c = await b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(400)
        def check(n, ok): print(("ok   " if ok else "FAIL ") + n); ok or fails.append(n)
        await q.evaluate("document.querySelector('#sec-B .imp-tools').scrollIntoView({block:'center'})"); await q.wait_for_timeout(300)
        y0 = await q.evaluate("scrollY"); top0 = await q.evaluate("document.querySelector('#sec-B').getBoundingClientRect().top")
        await q.click("[data-act=imp-open]"); await q.wait_for_timeout(200)
        check("page pinned while open", await q.evaluate("getComputedStyle(document.body).position") == "fixed")
        for x, y in ((195, 60), (195, 500)):  # backdrop strip above the sheet, and inside the sheet
            await q.mouse.move(x, y); await q.mouse.wheel(0, 900); await q.wait_for_timeout(250)
        # CDP touch swipe on the backdrop
        cdp = await c.new_cdp_session(q)
        await cdp.send("Input.synthesizeScrollGesture", {"x": 195, "y": 40, "yDistance": -600, "gestureSourceType": "touch"}); await q.wait_for_timeout(300)
        top1 = await q.evaluate("document.querySelector('#sec-B').getBoundingClientRect().top")
        check(f"background did not move ({top0:.0f} -> {top1:.0f})", abs(top1 - top0) < 2)
        await q.click("#imp .snap-foot [data-act=imp-cancel]"); await q.wait_for_timeout(200)
        y2 = await q.evaluate("scrollY"); check(f"scroll restored ({y0} -> {y2})", abs(y2 - y0) < 2)
        check("page unpinned", await q.evaluate("getComputedStyle(document.body).position") != "fixed")
        await q.mouse.wheel(0, 300); await q.wait_for_timeout(300); check("page scrolls again after close", await q.evaluate("scrollY") != y2)
        # receipt dialog too
        await q.set_input_files("#file-snap", {"name": "r.png", "mimeType": "image/png", "buffer": bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000" + "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")})
        await q.wait_for_timeout(500); check("receipt dialog pins page", await q.evaluate("getComputedStyle(document.body).position") == "fixed")
        await q.click("#snap .snap-foot [data-act=snap-cancel]"); await q.wait_for_timeout(200)
        check("receipt dialog unpins page", await q.evaluate("getComputedStyle(document.body).position") != "fixed")
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
