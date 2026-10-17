# Export offline app: the file is built from the page as loaded, carries no claim data,
# has the strict no-network policy, and runs on its own (build a PDF, import an itinerary).
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok): print(("ok   " if ok else "FAIL ") + n); ok or fails.append(n)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs, reqs = [], []
        mk = await b.new_page()
        await mk.set_content("<table>" + "".join(f"<tr><td>{a}</td><td>{v}</td></tr>" for a, v in [("Air Canada", ""), ("Flight # AC1234", ""), ("Departing:", "Winnipeg Intl Airport, Winnipeg, Canada (YWG)"), ("Date/time:", "02 December 2026, 07:45"), ("Arriving:", "Ottawa Intl Airport, Ottawa, Canada (YOW)"), ("Date/time:", "02 December 2026, 11:05")]) + "</table>")
        await mk.pdf(path=str(fx / "tiny.pdf")); await mk.close()
        for ch in ("web", "web-beta"):
            c = await b.new_context(accept_downloads=True); q = await c.new_page()
            q.on("pageerror", lambda e: errs.append(str(e)))
            await q.goto((base / f"out/{ch}/index.html").resolve().as_uri()); await q.wait_for_timeout(400)
            await q.fill("#trip-ref", "PRIVATE TRIP XYZ"); await q.fill("#m-sur", "Privatename"); await q.wait_for_timeout(200)
            await q.click("#menu-btn")
            async with q.expect_download() as dl: await q.click("#dl-offline")
            d = await dl.value; path = fx / d.suggested_filename; await d.save_as(str(path)); html = path.read_text()
            print(ch, "->", d.suggested_filename, f"{len(html) / 1e6:.2f} MB"); print("  toast:", await q.inner_text("#toast"))
            check(f"{ch}: file name has the version", re.fullmatch(r"CAF_Digital_Travel_Itinerary_v\d+\.\d+(-beta\.\d+)?\.html", d.suggested_filename) is not None and (("beta" in d.suggested_filename) == (ch == "web-beta")))
            check(f"{ch}: no claim data in the file", "PRIVATE TRIP XYZ" not in html and "Privatename" not in html)
            check(f"{ch}: strict no-network policy", "connect-src 'none'" in html and "worker-src 'none'" in html and "'self'" not in html)
            check(f"{ch}: no installed-app links", re.search(r'<link rel="(manifest|icon|apple-touch-icon)" href', html) is None and '<meta name="theme-color"' not in html)
            check(f"{ch}: starts with a doctype", html.startswith("<!doctype html>"))
            check(f"{ch}: beta marker only in the beta copy", ('data-channel="beta"' in html) == (ch == "web-beta"))
            await c.close()
            # run the downloaded file on its own
            c2 = await b.new_context(accept_downloads=True); r = await c2.new_page()
            r.on("pageerror", lambda e: errs.append(str(e))); r.on("request", lambda x: reqs.append(x.url) if not x.url.startswith(("file:", "data:", "blob:")) else None)
            await r.goto(path.resolve().as_uri()); await r.wait_for_timeout(500)
            check(f"{ch}: offline copy opens with the example claim", (await r.input_value("#trip-ref")) not in ("", "PRIVATE TRIP XYZ"))
            print("  label:", await r.inner_text(".menu-ver"))
            async with r.expect_download() as dl2: await r.click("#build-btn")
            check(f"{ch}: offline copy builds the PDF", (await dl2.value).suggested_filename.endswith(".pdf"))
            await r.click("[data-act=imp-open]"); await r.set_input_files("#file-itin", str(fx / "tiny.pdf"))
            await r.wait_for_selector("#imp-review:not([hidden])", timeout=20000)
            check(f"{ch}: offline copy reads an itinerary", "AC1234" in await r.inner_text("#imp-list"))
            await r.click("#imp .snap-foot [data-act=imp-cancel]")
            await r.click("#menu-btn")
            async with r.expect_download() as dl3: await r.click("#dl-offline")
            again = await (await dl3.value).path(); check(f"{ch}: offline copy can pass itself on", "connect-src 'none'" in pathlib.Path(again).read_text())
            await c2.close()
        # French file name
        c = await b.new_context(accept_downloads=True); q = await c.new_page()
        await q.add_init_script("localStorage.setItem('caf-dti-lang','fr')"); await q.goto((base / "out/web/index.html").resolve().as_uri()); await q.wait_for_timeout(400)
        await q.click("#menu-btn"); check("FR: menu item translated", (await q.inner_text("#dl-offline .mi-t")) == "Exporter l'application hors ligne")
        async with q.expect_download() as dl: await q.click("#dl-offline")
        check("FR: French file name", (await dl.value).suggested_filename.startswith("Itineraire-voyage-numerique-FAC_v"))
        print("errors:", errs); print("external requests:", reqs); print("failures:", fails); await b.close()
asyncio.run(main())
