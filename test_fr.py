# French mode: no untranslated strings, no errors, every screen exercised, PDF and file names in French.
import sys, pathlib, asyncio, json, re
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base / "shots"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True); pg = await c.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto(url); await pg.wait_for_timeout(500)
        print("start lang:", await pg.evaluate("document.documentElement.lang"), "| button:", await pg.inner_text("#lang-btn"))
        await pg.click("#lang-btn"); await pg.wait_for_timeout(500)
        print("after toggle:", await pg.evaluate("document.documentElement.lang"), "| h1:", await pg.inner_text("h1"), "| trip:", await pg.input_value("#trip-ref"))
        await pg.screenshot(path=str(shots / "fr-desktop-top.png"))
        # exercise: menu, snap, calls and exchange rows, private stay, install text
        await pg.click("#menu-btn"); await pg.keyboard.press("Escape")
        async with pg.expect_download() as dl: await pg.click("#build-btn")
        d = await dl.value; await d.save_as(str(shots / "fr.pdf")); print("PDF:", d.suggested_filename)
        print("result:", (await pg.inner_text("#result")).replace("\n", " | ")[:220])
        await pg.click("#menu-btn")
        async with pg.expect_download() as dl2: await pg.click("[data-act=save-draft]")
        print("draft:", (await dl2.value).suggested_filename)
        h = await pg.get_attribute("#help-foot", "href"); from urllib.parse import unquote; print("help:", unquote(h).split("&body=")[0][:120])
        print("footer:", await pg.inner_text(".sitefoot p"))
        await pg.click("[data-act=add][data-sec=calls]"); await pg.click("[data-act=add][data-sec=exchange]")
        sid = await pg.eval_on_selector_all("#rows-stays .stay", "els => els[0].dataset.row")
        await pg.check(f"#stays-{sid}-priv"); await pg.wait_for_timeout(200)
        await pg.click("[data-act=review]"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=str(shots / "fr-checks.png"), full_page=True)
        await pg.uncheck(f"#stays-{sid}-priv")
        print("missing:", await pg.evaluate("[...window.__i18nMissing]"))
        # visible text scan for English leftovers
        txt = await pg.evaluate("document.body.innerText")
        eng = [w for w in ["Receipt", "Lodging", "Meals", "Add ", "Save", "Build", "Choose", "Remove", "Total cost", "Check-in", "None", " the "] if w in txt]
        print("english words still visible:", eng)
        # switch back
        await pg.click("#lang-btn"); await pg.wait_for_timeout(400); print("back:", await pg.inner_text("h1"), "| trip:", await pg.input_value("#trip-ref"))
        # phone in French
        m = await b.new_context(**{k: v for k, v in p.devices["iPhone 13"].items() if k != "default_browser_type"}); q = await m.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.add_init_script("localStorage.setItem('caf-dti-lang','fr')"); await q.goto(url); await q.wait_for_timeout(500)
        print("phone width:", await q.evaluate("document.documentElement.scrollWidth"), "| bar h:", round((await (await q.query_selector(".totalbar")).bounding_box())["height"]))
        await q.screenshot(path=str(shots / "fr-phone-top.png"))
        await q.evaluate("document.querySelector('#sec-B').scrollIntoView()"); await q.wait_for_timeout(300); await q.screenshot(path=str(shots / "fr-phone-itin.png"))
        await q.evaluate("document.querySelector('#sec-SD').scrollIntoView()"); await q.wait_for_timeout(300); await q.screenshot(path=str(shots / "fr-phone-sd.png"))
        print("errors:", errs); await b.close()
asyncio.run(main())
