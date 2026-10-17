import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1])
(base / "fixtures").mkdir(exist_ok=True)
if not (base / "fixtures/r.png").exists():  # a plain white "receipt" photo
    from PIL import Image; Image.new("RGB", (400, 600), "white").save(base / "fixtures/r.png")
url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base / "shots"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}); pg = await c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("localStorage.setItem('caf-dti-lang','fr')"); await pg.goto(url); await pg.wait_for_timeout(500)
        await pg.check("#poc-on"); await pg.check("#sd-abroad"); await pg.select_option("#sd-juris", "BC"); await pg.wait_for_timeout(200)
        print("BC jurat:", (await pg.inner_text("#sd-jurat")).replace("\n", " ")[:260])
        await pg.select_option("#sd-juris", "SK"); await pg.select_option("#sd-env", "air"); await pg.wait_for_timeout(100)
        print("SK air:", (await pg.inner_text("#sd-jurat .who")).replace("\n", " ")[:200])
        await pg.select_option("#sd-juris", "ON"); await pg.uncheck("#sd-abroad")
        sid = await pg.eval_on_selector_all("#rows-stays .stay", "els => els[1].dataset.row")
        await pg.uncheck(f"#stays-{sid}-quarters"); await pg.wait_for_timeout(100); await pg.check(f"#stays-{sid}-quarters")
        await pg.set_input_files("#file-snap", str(base / "fixtures/r.png")); await pg.wait_for_timeout(600)
        for v in ["taxi", "fx", "hotel", "call", "other", "rental"]:
            await pg.click(f"input[name=snap-type][value={v}]", force=True); await pg.wait_for_timeout(50)
        await pg.screenshot(path=str(shots / "fr-snap.png"))
        await pg.click("[data-act=snap-save]"); await pg.wait_for_timeout(300); print("toast:", await pg.inner_text("#toast"))
        await pg.click("#menu-btn"); await pg.click("[data-act=install]") if await pg.is_visible("#install-btn") else None
        await pg.keyboard.press("Escape")
        await pg.click("[data-act=fill-stays]"); await pg.wait_for_timeout(200); print("toast2:", await pg.inner_text("#toast"))
        print("missing:", await pg.evaluate("[...window.__i18nMissing]"))
        print("errors:", errs); await b.close()
asyncio.run(main())
