import sys, pathlib, asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
base = pathlib.Path(sys.argv[1]); out = base / "shots"; out.mkdir(exist_ok=True)
fx = base / "fixtures"; fx.mkdir(exist_ok=True)
page_url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()

# generic dummy receipts only
img = Image.new("RGB", (600, 800), "white"); d = ImageDraw.Draw(img)
d.text((40, 40), "DUMMY TEST RECEIPT\nSample Hardware\nTOTAL CAD 42.00", fill="black")
img.save(fx / "dummy-receipt.png")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        tmp = await b.new_page()
        await tmp.set_content("<h1>Dummy test receipt</h1><p>Sample Conference Centre</p><p>Registration fee: CAD 150.00</p>")
        await tmp.pdf(path=str(fx / "dummy-receipt.pdf")); await tmp.close()

        ctx = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True)
        pg = await ctx.new_page()
        errs, reqs = [], []
        pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        pg.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
        await pg.goto(page_url); await pg.wait_for_timeout(600)
        print("example build enabled:", await pg.is_enabled("#build-btn"), "| checks:", (await pg.inner_text("#checks"))[:200].replace("\n", " "))
        print("SD visible:", await pg.is_visible("#sec-SD"))
        print("meals counts:", [await pg.inner_text(f"#mc-{k}") for k in "bld"])

        # rations toggle off on quarters stay -> meals ticked again
        qid = await pg.eval_on_selector_all("#rows-stays .stay", "els => els[1].dataset.row")
        await pg.uncheck(f"#stays-{qid}-rations")
        print("after rations off:", [await pg.inner_text(f"#mc-{k}") for k in "bld"])
        await pg.check(f"#stays-{qid}-rations")
        print("after rations on:", [await pg.inner_text(f"#mc-{k}") for k in "bld"])

        # jurisdiction must be confirmed
        await pg.select_option("#sd-juris", "")
        print("blocked without jurat:", not await pg.is_enabled("#build-btn"))
        await pg.select_option("#sd-juris", "NB")
        print("jurat NB:", (await pg.inner_text("#sd-jurat")).replace("\n", " "))
        await pg.select_option("#sd-juris", "ON")

        # general row with generated receipts
        await pg.click("[data-act=add][data-sec=general]")
        rid = await pg.eval_on_selector_all("#rows-general .row", "els => els[els.length-1].dataset.row")
        await pg.fill(f"#general-{rid}-location", "Winnipeg")
        await pg.fill(f"#general-{rid}-desc", "Course materials")
        await pg.fill(f"#general-{rid}-cost", "42")
        await pg.click(f"#rc-{rid} .attach")
        await pg.set_input_files("#file-rc", [str(fx / "dummy-receipt.pdf"), str(fx / "dummy-receipt.png")])
        await pg.wait_for_timeout(800)
        print("build enabled:", await pg.is_enabled("#build-btn"))

        async with pg.expect_download() as dl:
            await pg.click("#build-btn")
        dd = await dl.value
        await dd.save_as(str(out / "v3.pdf"))
        print("download:", dd.suggested_filename)
        print("result:", (await pg.inner_text("#result")).replace("\n", " "))
        await pg.screenshot(path=str(out / "v3-desktop.png"), full_page=True)

        ctx2 = await b.new_context(viewport={"width": 400, "height": 860}, color_scheme="dark")
        p2 = await ctx2.new_page()
        await p2.goto(page_url); await p2.wait_for_timeout(500)
        print("phone scrollWidth:", await p2.evaluate("document.documentElement.scrollWidth"))
        for sid in ("sec-E", "sec-SD"):
            el = await p2.query_selector("#" + sid); await el.screenshot(path=str(out / f"v3-phone-{sid}.png"))
        print("errors:", errs); print("external requests:", reqs)
        await b.close()
asyncio.run(main())
