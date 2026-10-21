# The menu, grouped by function: Claim file, On this device, Experimental, App, Help (and Beta testing in the beta).
# Its options, and the yes/no choices on the page, are on/off switches. Itinerary import is on unless turned off,
# and off hides the import card; both experimental options are remembered on the device and cleared by Reset the beta.
import sys, pathlib, asyncio, subprocess, socket, time
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); shots = base / "shots"; shots.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
HEADS = "() => [...document.querySelectorAll('#menu .menu-h')].filter(e => e.offsetParent).map(e => e.textContent.trim())"
SWITCH = """sel => { const e = document.querySelector(sel); const s = getComputedStyle(e); const r = e.getBoundingClientRect();
  return { app: s.appearance || s.webkitAppearance, w: Math.round(r.width), h: Math.round(r.height), bg: s.backgroundColor, pos: s.backgroundPosition }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        # served over http: headless Chromium sometimes drops localStorage writes across a reload of a file:// page
        s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
        srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "-d", str((base / "out").resolve())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
        prod = f"http://localhost:{port}/web/index.html"; beta = f"http://localhost:{port}/web-beta/index.html"
        for lang, url, vp, scheme in (("en", beta, {"width": 390, "height": 844}, "light"), ("en", prod, {"width": 1280, "height": 900}, "dark"), ("fr", beta, {"width": 390, "height": 844}, "light")):
            ch = "beta" if url == beta else "prod"
            c = await b.new_context(viewport=vp, color_scheme=scheme, device_scale_factor=2); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}'); localStorage.setItem('caf-dti-lang-beta','{lang}')")
            await q.goto(url); await q.wait_for_timeout(600)
            tag = f"{lang}/{ch}"
            check(f"{tag}: import card shows by default", await q.is_visible("#imp-hero"))
            check(f"{tag}: import card says experimental", "EXP" in (await q.inner_text("#imp-hero .pill-exp")).upper() and await q.locator("#imp-hero .pill-beta").count() == 0)
            await q.click("#menu-btn"); await q.wait_for_timeout(200)
            heads = await q.evaluate(HEADS)
            want = {"en": ["Claim file", "On this device", "Experimental", "App", "Help"], "fr": ["Fichier de réclamation", "Sur cet appareil", "Expérimental", "Application", "Aide"]}[lang] + (["Beta testing" if lang == "en" else "Essais de la version bêta"] if ch == "beta" else [])
            check(f"{tag}: menu sections in order", [h.lower() for h in heads] == [h.lower() for h in want], heads)
            check(f"{tag}: Itinerary import is on, Beautify export is off", await q.is_checked("#opt-imp") and not await q.is_checked("#opt-pretty"))
            sw = await q.evaluate(SWITCH, "#opt-imp")
            check(f"{tag}: options are switches, big enough to tap", sw["app"] == "none" and sw["w"] >= 38 and sw["h"] >= 22 and sw["w"] > sw["h"], sw)
            order = await q.evaluate("() => [...document.querySelectorAll('#save-now-menu, #opt-keep')].map(e => e.id)")
            check(f"{tag}: Save now sits above Keep my work", order == ["save-now-menu", "opt-keep"], order)
            hgt = await q.evaluate("() => document.getElementById('menu').scrollHeight")
            print(f"  {tag}: menu height {hgt}px")
            check(f"{tag}: menu is compact", hgt < (1000 if ch == "beta" else 800), hgt)
            check(f"{tag}: no description lines except the version switch", await q.evaluate("() => [...document.querySelectorAll('#menu .mi-sub')].filter(e => e.offsetParent && e.id !== 'switch-sub').length") == 0)
            mb = await q.locator("#menu").bounding_box()
            check(f"{tag}: menu fits the screen width", mb["x"] >= 0 and mb["x"] + mb["width"] <= vp["width"], mb)
            await q.screenshot(path=str(shots / f"menu-{lang}-{ch}-{scheme}.png"))
            if lang == "en" and ch == "beta":
                await q.locator("#menu").evaluate("m => m.scrollTop = m.scrollHeight"); await q.screenshot(path=str(shots / "menu-en-beta-bottom.png"))
                await q.locator("#menu").evaluate("m => m.scrollTop = 0")
            # turn import off: the card goes, and stays gone after a reload
            await q.click("label:has(#opt-imp)"); await q.wait_for_timeout(250)
            check(f"{tag}: the switch turns import off", not await q.is_checked("#opt-imp"))
            on = await q.evaluate(SWITCH, "#opt-imp")
            check(f"{tag}: off and on look different", on["pos"] != sw["pos"] and on["bg"] != sw["bg"], (sw, on))
            await q.keyboard.press("Escape"); await q.wait_for_timeout(200)
            check(f"{tag}: import off hides the import card", not await q.is_visible("#imp-hero"))
            await q.reload(); await q.wait_for_timeout(600)
            check(f"{tag}: import off is remembered", not await q.is_visible("#imp-hero"))
            await q.click("#menu-btn"); check(f"{tag}: the menu shows it off after a reload", not await q.is_checked("#opt-imp"))
            await q.click("label:has(#opt-imp)"); await q.click("label:has(#opt-pretty)"); await q.keyboard.press("Escape"); await q.wait_for_timeout(200)
            check(f"{tag}: back on, the card returns", await q.is_visible("#imp-hero") and await q.is_visible("#pretty-note"))
            # yes/no choices on the page are switches too; the meals grid keeps its check boxes
            ps = await q.evaluate(SWITCH, "#poc-on")
            check(f"{tag}: page choices are switches", ps["app"] == "none" and ps["w"] > ps["h"], ps)
            if ch == "beta":
                await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
                meal = await q.evaluate("() => { const e = document.querySelector('[data-meal]'); const s = getComputedStyle(e); return s.appearance || s.webkitAppearance; }")
                check(f"{tag}: meals grid keeps check boxes", meal != "none", meal)
                await q.evaluate("document.getElementById('sec-L') && document.getElementById('sec-L').scrollIntoView()"); await q.wait_for_timeout(300)
                await q.screenshot(path=str(shots / f"toggles-page-{lang}.png"))
                # Reset the beta clears both experimental choices
                await q.click("#menu-btn"); await q.click("label:has(#opt-imp)"); await q.wait_for_timeout(200)
                await q.click("#beta-reset"); await q.click("#beta-reset"); await q.wait_for_timeout(1500)
                await q.reload(); await q.wait_for_timeout(600)
                check(f"{tag}: after Reset the beta, import is on and Beautify export off", await q.is_visible("#imp-hero") and not await q.is_visible("#pretty-note"))
            if lang == "fr": check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
            await c.close()
        srv.terminate()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
