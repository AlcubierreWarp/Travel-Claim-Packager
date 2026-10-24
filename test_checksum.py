# Offline copy checksums: the menu shows the SHA-256 of this version's published offline file, Download offline copy
# hands over that exact file, a copy built on the device says its checksum will differ, an offline copy points to
# the published checksums instead of showing one, and the offline helper never mistakes the offline file for the app.
import sys, pathlib, asyncio, hashlib, subprocess, socket, time, re
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
sha = lambda b: hashlib.sha256(b).hexdigest()
async def main():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "-d", str((base / "out").resolve())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
    errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for ch in ("web", "web-beta"):
            pub = (base / f"out/{ch}/CAF_Digital_Travel_Itinerary.html").read_bytes(); want = sha(pub)
            url = f"http://localhost:{port}/{ch}/index.html"
            # the offline helper is tested on its own below; blocked here so the test can stand in for the site
            c = await b.new_context(accept_downloads=True, service_workers="block"); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.goto(url); await q.wait_for_timeout(600)
            await q.click("#menu-btn")
            shown = (await q.inner_text("#offline-sha code")).strip()
            check(f"{ch}: menu shows the offline file's SHA-256", shown == want, (shown, want))
            check(f"{ch}: the page does not contain its offline file's bytes' hash placeholder", "__OFFLINE_SHA__" not in (base / f"out/{ch}/index.html").read_text())
            async with q.expect_download() as dl: await q.click("#dl-offline")
            got = pathlib.Path(await (await dl.value).path()).read_bytes(); await q.wait_for_timeout(300)
            check(f"{ch}: Download offline copy gives the published file, byte for byte", sha(got) == want, sha(got))
            toast = await q.inner_text("#toast")
            check(f"{ch}: no 'built on this device' note for the published file", "built on this device" not in toast, toast)
            # the page may read its own site, still nothing outside it
            r = await q.evaluate(f"() => Promise.all([fetch('http://127.0.0.1:{port}/web/sw.js').then(() => 'sent', () => 'blocked'), fetch('sw.js').then(x => x.ok ? 'own site' : 'no', () => 'blocked')])")
            check(f"{ch}: other origins stay blocked, own site readable", r == ["blocked", "own site"], r)
            # a newer file on the site than the open page: asks for a reload, saves nothing
            await q.route("**/CAF_Digital_Travel_Itinerary.html", lambda rt: rt.fulfill(status=200, body="<!doctype html>newer", content_type="text/html"))
            await q.click("#menu-btn") if not await q.is_visible("#menu") else None
            await q.click("#dl-offline"); await q.wait_for_timeout(500)
            check(f"{ch}: a newer file on the site asks for a reload", "newer version" in await q.inner_text("#toast"))
            # the file cannot be read at all: a copy is built here, and it says the checksum will differ
            await q.unroute("**/CAF_Digital_Travel_Itinerary.html"); await q.route("**/CAF_Digital_Travel_Itinerary.html", lambda rt: rt.abort())
            await q.click("#menu-btn") if not await q.is_visible("#menu") else None
            async with q.expect_download() as dl: await q.click("#dl-offline")
            built = pathlib.Path(await (await dl.value).path()).read_text(); await q.wait_for_timeout(300)
            check(f"{ch}: unreadable file: a copy is built and the note says so", "built on this device" in await q.inner_text("#toast"))
            check(f"{ch}: a built copy does not claim the published checksum", "const OFFLINE_SHA = ''" in built and want not in built)
            await c.close()
            # inside the offline file: no checksum of its own, a link to the published ones
            c = await b.new_context(); q = await c.new_page(); await q.goto((base / f"out/{ch}/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()); await q.wait_for_timeout(500)
            await q.click("#menu-btn"); note = await q.inner_text("#offline-sha")
            href = await q.get_attribute("#offline-sha a", "href")
            check(f"{ch}: the offline file points to the published checksums", "GitHub" in note and href and href.endswith("#checksums") and await q.locator("#offline-sha code").count() == 0, (note, href))
            await c.close()
        # offline helper: opening the offline file under the app's address must not replace the saved app
        c = await b.new_context(); q = await c.new_page()
        await q.goto(f"http://localhost:{port}/web/index.html"); await q.wait_for_timeout(500)
        await q.evaluate("() => navigator.serviceWorker.ready"); await q.reload(); await q.wait_for_timeout(800)
        await q.goto(f"http://localhost:{port}/web/CAF_Digital_Travel_Itinerary.html"); await q.wait_for_timeout(800)
        await c.set_offline(True)
        await q.goto(f"http://localhost:{port}/web/index.html"); await q.wait_for_timeout(800)
        html = await q.content()
        check("offline helper: the app still opens offline as the app, not the offline file", '<link rel="manifest"' in html, html[:200])
        q2 = await c.new_page(); await q2.goto(f"http://localhost:{port}/web/CAF_Digital_Travel_Itinerary.html"); await q2.wait_for_timeout(800)
        check("offline helper: the offline file is kept for offline use", "connect-src 'none'" in await q2.content())
        q3 = await c.new_page(); await q3.goto(f"http://localhost:{port}/web/index.html"); await q3.wait_for_timeout(800)
        await q3.click("#menu-btn")
        async with q3.expect_download() as dl: await q3.click("#dl-offline")
        got = pathlib.Path(await (await dl.value).path()).read_bytes()
        check("offline helper: Download offline copy works offline with the published file", sha(got) == sha((base / "out/web/CAF_Digital_Travel_Itinerary.html").read_bytes()))
        await c.close()
        # French
        c = await b.new_context(); q = await c.new_page(); await q.add_init_script("localStorage.setItem('caf-dti-lang','fr')")
        await q.goto(f"http://localhost:{port}/web/index.html"); await q.wait_for_timeout(600); await q.click("#menu-btn")
        check("FR: checksum label translated", "copie hors ligne" in await q.inner_text("#offline-sha"))
        check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
        await c.close(); await b.close()
    srv.terminate()
    print("errors:", errs); print("failures:", fails)
asyncio.run(main())
