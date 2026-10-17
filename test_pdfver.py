# The PDF package carries the app version on every page footer and in its file properties.
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for ch, lang in (("web", "en"), ("web-beta", "en"), ("web", "fr")):
            c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}')")
            await q.goto((base / f"out/{ch}/index.html").resolve().as_uri()); await q.wait_for_timeout(400)
            ver = (base / "VERSION").read_text().strip()
            async with q.expect_download() as dl: await q.click("#build-btn")
            f = fx / f"{ch}-{lang}.pdf"; await (await dl.value).save_as(str(f))
            r = PdfReader(str(f)); texts = [pg.extract_text() for pg in r.pages]
            want = re.compile(r"v\d+\.\d+ b[eê]ta \d+") if ch == "web-beta" else re.compile(r"v" + re.escape(ver) + r"\b")
            check(f"{ch}/{lang}: version on every page ({len(texts)} pages)", all(want.search(t) for t in texts), [t[-160:] for t in texts if not want.search(t)][:1])
            meta = r.metadata
            check(f"{ch}/{lang}: version in file properties", want.search(meta.get("/Keywords", "")) is not None and "Itinerary" in meta.get("/Creator", ""), (meta.get("/Keywords"), meta.get("/Creator")))
            print("  footer:", [l for l in texts[0].splitlines() if want.search(l)][:1])
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
