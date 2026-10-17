# File number: 7209-1 by default in every file name, until the member changes or clears it.
import sys, pathlib, asyncio, json
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(400)
        f = await q.inner_text("#fname"); check("example claim uses 7209-1", "_7209-1_" in f, f)
        check("field shows 7209-1", await q.input_value("#pk-fileno") == "7209-1")
        await q.click("[data-act=start-blank]"); await q.wait_for_timeout(300)
        f = await q.inner_text("#fname"); check("blank claim uses 7209-1", "_7209-1_" in f, f)
        await q.click("#menu-btn")
        async with q.expect_download() as dl: await q.click("#save-draft")
        d = await dl.value; check("claim file name has 7209-1", "_7209-1_" in d.suggested_filename, d.suggested_filename)
        await q.fill("#pk-fileno", "1234-5"); await q.wait_for_timeout(200)
        f = await q.inner_text("#fname"); check("changed number is used", "_1234-5_" in f and "7209-1" not in f, f)
        await q.fill("#pk-fileno", ""); await q.wait_for_timeout(200)
        f = await q.inner_text("#fname"); check("cleared number leaves it out", "7209" not in f and "1234" not in f, f)
        await q.click("#menu-btn")
        async with q.expect_download() as dl: await q.click("#save-draft")
        cleared = fx / "cleared.json"; await (await dl.value).save_as(str(cleared))
        await q.wait_for_timeout(900); await q.reload(); await q.wait_for_timeout(500)
        print("  after reload:", await q.input_value("#trip-ref"), "/", await q.inner_text("#fname"))
        check("cleared number stays cleared after reload", await q.input_value("#pk-fileno") == "", await q.input_value("#pk-fileno"))
        # a claim file saved before the default existed (empty file number, no flag) gets the default
        o = json.loads(cleared.read_text()); o["state"]["fileNo"] = ""; o["state"].pop("fileNoSet", None); old = fx / "old.json"; old.write_text(json.dumps(o))
        await q.set_input_files("#file-draft", str(old)); await q.wait_for_timeout(600)
        check("older claim file gets 7209-1", await q.input_value("#pk-fileno") == "7209-1", await q.input_value("#pk-fileno"))
        await q.set_input_files("#file-draft", str(cleared)); await q.wait_for_timeout(600)
        check("claim file with the number cleared on purpose stays cleared", await q.input_value("#pk-fileno") == "", await q.input_value("#pk-fileno"))
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
