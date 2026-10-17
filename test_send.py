import sys, pathlib, asyncio, json
from urllib.parse import unquote
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base / "shots"; shots.mkdir(exist_ok=True)
STUB = """navigator.canShare = d => !!(d && d.files) && (window.__allow || ['application/json','application/pdf','text/plain']).includes(d.files[0].type); navigator.share = async d => { window.__shared = { title: d.title, text: d.text, name: d.files[0].name, type: d.files[0].type, size: d.files[0].size }; };"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        # desktop: no send button, footer + help present
        ctx = await b.new_context(viewport={"width":1320,"height":900}); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script(STUB); await pg.goto(url); await pg.wait_for_timeout(500)
        await pg.click("#menu-btn")
        print("desktop send-draft visible:", await pg.is_visible("#send-draft"), "| help in menu:", await pg.is_visible("#help-menu"))
        await pg.keyboard.press("Escape")
        print("footer:", await pg.inner_text(".sitefoot p"))
        h = unquote(await pg.get_attribute("#help-foot", "href")); print("help href:\n ", h.replace("\n", "\n  ")[:900])
        h = unquote(await pg.get_attribute("#fb-foot", "href")); print("feedback href:\n ", h.replace("\n", "\n  ")[:1200])
        await pg.click("#menu-btn"); print("menu feedback visible:", await pg.is_visible("#fb-menu")); await pg.keyboard.press("Escape")
        print("totop at top hidden:", await pg.eval_on_selector("#totop", "e => e.hidden"))
        await pg.evaluate("window.scrollTo(0, 3000)"); await pg.wait_for_timeout(300)
        print("totop after scroll visible:", await pg.is_visible("#totop"), await pg.eval_on_selector("#totop", "e => getComputedStyle(e).opacity"))
        await pg.click("#totop"); await pg.wait_for_timeout(1200); print("scrollY after click:", await pg.evaluate("scrollY"))
        await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=str(shots/"foot-desktop.png"))
        # phone (touch) iOS-like: json allowed
        dev = p.devices["iPhone 13"]
        c2 = await b.new_context(**{k:v for k,v in dev.items() if k!="default_browser_type"}, accept_downloads=True); q = await c2.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.add_init_script(STUB); await q.goto(url); await q.wait_for_timeout(500)
        await q.click("#menu-btn"); print("phone send-draft visible:", await q.is_visible("#send-draft"), "| label:", await q.inner_text("#send-draft"))
        await q.click("#send-draft"); await q.wait_for_timeout(400); sh = await q.evaluate("window.__shared"); print("  shared:", sh["name"], sh["type"], "|", sh["title"])
        await q.click("[data-act=review]"); await q.wait_for_timeout(300)
        async with q.expect_download() as dl: await q.click("#build-btn")
        await dl.value; await q.wait_for_timeout(500)
        print("  result buttons:", await q.eval_on_selector_all("#result .acts button", "els => els.map(e => e.textContent)"))
        await q.click("[data-act=send-pdf]"); await q.wait_for_timeout(300); sh = await q.evaluate("window.__shared"); print("  shared pdf:", sh["name"], sh["type"], sh["size"], "|", sh["title"])
        await q.evaluate("window.scrollTo(0, document.body.scrollHeight)"); await q.wait_for_timeout(400)
        await q.screenshot(path=str(shots/"foot-phone.png"))
        tb = await (await q.query_selector("#totop")).bounding_box(); bar = await (await q.query_selector(".totalbar")).bounding_box()
        print("  totop bottom", round(tb["y"]+tb["height"]), "bar top", round(bar["y"]))
        # Android-like: json refused, txt allowed
        c3 = await b.new_context(**{k:v for k,v in p.devices["Pixel 7"].items() if k!="default_browser_type"}, accept_downloads=True); r = await c3.new_page(); r.on("pageerror", lambda e: errs.append(str(e)))
        await r.add_init_script("window.__allow=['text/plain','application/pdf'];" + STUB); await r.goto(url); await r.wait_for_timeout(500)
        await r.click("#menu-btn"); await r.click("#send-draft"); await r.wait_for_timeout(300); print("android shared:", (await r.evaluate("window.__shared"))["name"])
        # reopen a .txt draft
        txt = base / "fixtures"; txt.mkdir(exist_ok=True)
        await r.click("#menu-btn")
        async with r.expect_download() as dl: await r.click("[data-act=save-draft]")
        await (await dl.value).save_as(str(txt/"d.txt"))
        await r.set_input_files("#file-draft", str(txt/"d.txt")); await r.wait_for_timeout(400); print("  reopen txt toast:", await r.inner_text("#toast"))
        print("errors:", errs); await b.close()
asyncio.run(main())
