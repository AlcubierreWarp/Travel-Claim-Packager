# Add stays from itinerary: leave stops get a read-only leave card (removable, with Undo) instead of a stay to fill
# in, so the missing lodging reads as intended. The card never reaches the PDF and is not added twice.
import sys, pathlib, asyncio, json
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for lang in ("en", "fr"):
            c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}')")
            await q.goto((base / "out/web-beta/index.html").resolve().as_uri()); await q.wait_for_timeout(600)
            await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
            await q.click("#menu-btn")
            async with q.expect_download() as dl: await q.click("#save-draft")
            d = fx / f"d-{lang}.json"; await (await dl.value).save_as(str(d)); o = json.loads(d.read_text()); o["state"]["lodging"] = {"stays": []}
            d.write_text(json.dumps(o)); await q.keyboard.press("Escape"); await q.set_input_files("#file-draft", str(d)); await q.wait_for_timeout(900)
            await q.click("[data-act=fill-stays]"); await q.wait_for_timeout(400)
            stays, cards = await q.locator("#rows-stays .stay").count(), q.locator("#rows-stays .leave-card")
            txt = await cards.first.inner_text() if await cards.count() else ""
            print(f"  {lang}:", stays, "stays;", " / ".join(txt.split("\n")))
            check(f"{lang}: duty stops become stays, the leave stop a leave card", stays == 2 and await cards.count() == 1 and "Digby" in txt and ("1 night" in txt or "1 nuit" in txt), (stays, txt))
            check(f"{lang}: the leave card has nothing to fill in", await cards.first.locator("input, select, textarea").count() == 0)
            order = await q.eval_on_selector_all("#rows-stays > *", "els => els.map(e => e.classList.contains('leave-card') ? 'leave' : 'stay')")
            check(f"{lang}: it sits in date order, after the stays before it", order == ["stay", "stay", "leave"], order)
            toast = await q.inner_text("#toast"); check(f"{lang}: the message says leave nights have nothing to claim", ("nothing to claim" in toast) if lang == "en" else ("sans rien à réclamer" in toast), toast)
            await q.click("[data-act=fill-stays]"); await q.wait_for_timeout(300)
            check(f"{lang}: adding again does not repeat it", await cards.count() == 1 and await q.locator("#rows-stays .stay").count() == 2)
            await q.click("[data-act=del-leave]"); await q.wait_for_timeout(200)
            check(f"{lang}: removable", await cards.count() == 0)
            await q.click("#toast button"); await q.wait_for_timeout(200)
            check(f"{lang}: Undo brings it back", await cards.count() == 1)
            await q.wait_for_timeout(800); await q.reload(); await q.wait_for_timeout(800)
            check(f"{lang}: kept after a reload", await q.locator("#rows-stays .leave-card").count() == 1)
            for k in range(await q.locator("#rows-stays .stay input[data-k=quarters]").count()): await q.locator("#rows-stays .stay input[data-k=quarters]").nth(k).check(); await q.wait_for_timeout(150)
            check(f"{lang}: the leave card stays put when the stays change", await q.locator("#rows-stays .leave-card").count() == 1)
            await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
            async with q.expect_download() as dl: await q.click("#build-btn")
            f = fx / f"leave-{lang}.pdf"; await (await dl.value).save_as(str(f)); t = " ".join(pg.extract_text() for pg in PdfReader(str(f)).pages)
            check(f"{lang}: not in the PDF", "no lodging to claim" not in t and "aucun hébergement à réclamer" not in t)
            if lang == "fr": check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
