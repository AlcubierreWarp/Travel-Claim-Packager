import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base/"shots"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width":1320,"height":900}, accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(500)
        print("default:", await q.inner_text("#fname"))
        await q.fill("#pk-fileno", "7209-1 (J1)"); await q.wait_for_timeout(300); print("with file no:", await q.inner_text("#fname"))
        await q.select_option("#pk-marking", "UNCLAS"); await q.wait_for_timeout(200); print("UNCLAS:", await q.inner_text("#fname"))
        await q.select_option("#pk-marking", ""); await q.wait_for_timeout(200); print("none:", await q.inner_text("#fname"))
        await q.select_option("#pk-marking", "PA"); await q.fill("#pk-fileno", "7209-1"); await q.wait_for_timeout(300)
        async with q.expect_download() as dl: await q.click("#build-btn")
        d = await dl.value; await d.save_as(str(shots/"named.pdf")); print("PDF download:", d.suggested_filename)
        await q.click("#menu-btn")
        async with q.expect_download() as dl2: await q.click("[data-act=save-draft]")
        print("draft download:", (await dl2.value).suggested_filename)
        await q.locator("#sec-P").screenshot(path=str(shots/"names-ui.png"))
        print("errors:", errs); await b.close()
asyncio.run(main())
