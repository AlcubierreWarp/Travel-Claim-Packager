import sys, pathlib, asyncio, json
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # A: share sheet supported (stubbed so we can inspect what is handed over)
        ctx = await b.new_context(accept_downloads=True); pg = await ctx.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("""navigator.canShare = d => !!(d && d.files); navigator.share = async d => { window.__shared = { title: d.title, text: d.text, name: d.files[0].name, type: d.files[0].type, body: await d.files[0].text() }; };""")
        await pg.goto(url); await pg.wait_for_timeout(500)
        await pg.click("#menu-btn"); await pg.click("[data-act=email-draft]"); await pg.wait_for_timeout(500)
        sh = await pg.evaluate("window.__shared")
        d = json.loads(sh["body"])
        print("A title:", sh["title"]); print("  file:", sh["name"], sh["type"], "| app:", d["app"], "| stops:", len(d["state"]["stops"]))
        print("  text:", sh["text"].replace("\n"," | "))
        # A2: blank trip, no dates
        await pg.evaluate("() => { navigator.share = async d => { window.__shared = { title: d.title } } }")
        await pg.click("#menu-btn"); await pg.click("#clear-btn"); await pg.click("#clear-btn"); await pg.wait_for_timeout(600)
        for btn in ["text=Clear", "text=Start blank"]:
            pass
        await pg.wait_for_timeout(300)
        await pg.click("#menu-btn"); await pg.click("[data-act=email-draft]"); await pg.wait_for_timeout(400)
        print("A2 title after clear:", (await pg.evaluate("window.__shared"))["title"])
        # B: no file sharing (Firefox-like): save + mailto
        ctx2 = await b.new_context(accept_downloads=True); q = await ctx2.new_page()
        q.on("pageerror", lambda e: errs.append(str(e)))
        await q.add_init_script("""delete Navigator.prototype.share; delete Navigator.prototype.canShare; window.__mail=null; const oc = HTMLAnchorElement.prototype.click; HTMLAnchorElement.prototype.click = function(){ if (this.href.startsWith('mailto:')) { window.__mail = this.href; return; } return oc.call(this); };""")
        await q.goto(url); await q.wait_for_timeout(500)
        await q.click("#menu-btn")
        async with q.expect_download() as dl:
            await q.click("[data-act=email-draft]")
        dd = await dl.value; await q.wait_for_timeout(300)
        print("B download:", dd.suggested_filename)
        m = await q.evaluate("window.__mail"); from urllib.parse import unquote
        print("  mailto:", unquote(m)[:400].replace("\n"," | "))
        print("  toast:", await q.inner_text("#toast"))
        print("errors:", errs)
        await b.close()
asyncio.run(main())
