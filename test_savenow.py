# Save now: writes the claim at once, reads it back, and says where it is kept. Ctrl+S does the same.
import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1])
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
async def toast(q): await q.wait_for_selector("#toast:not([hidden])"); return await q.inner_text("#toast")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        url = (base / "out/web/index.html").resolve().as_uri()
        c = await b.new_context(viewport={"width": 1320, "height": 900}); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(500)
        await q.fill("#trip-ref", "Save test one")
        await q.click("#save-now"); t = await toast(q); print("  tab:", t)
        check("tab only: says it lasts until the tab closes", "Saved in this tab at" in t and "Keep on this device" in t, t)
        check("tab only: written straight away", "Save test one" in await q.evaluate("sessionStorage.getItem('caf-dti-v1') || ''"))
        await q.fill("#trip-ref", "Save test two"); await q.keyboard.press("Control+s"); t = await toast(q)
        check("Ctrl+S saves, while still typing", "Saved in this tab" in t and "Save test two" in await q.evaluate("sessionStorage.getItem('caf-dti-v1') || ''"), t)
        await q.click("#toast button"); await q.wait_for_timeout(800)  # Keep on this device
        await q.fill("#trip-ref", "Save test three"); await q.click("#save-now"); await q.wait_for_timeout(300); t = await toast(q); print("  device:", t)
        check("device: saved and checked", "Saved on this device at" in t and "checked" in t, t)
        check("header shows the save time", (await q.inner_text("#savechip")).startswith("Saved"), await q.inner_text("#savechip"))
        await q.reload(); await q.wait_for_timeout(1200)
        check("device: claim comes back after reload", await q.input_value("#trip-ref") == "Save test three", await q.input_value("#trip-ref"))
        # a browser that refuses to store: Save now says so and offers the export
        await q.evaluate("() => { IDBObjectStore.prototype.put = function () { throw new DOMException('full', 'QuotaExceededError'); }; }")
        await q.fill("#trip-ref", "Save test four"); await q.click("#save-now"); await q.wait_for_timeout(300); t = await toast(q); print("  refused:", t)
        check("refused: warns and offers Export claim file", "did not save" in t and "Export claim file" in t, t)
        check("refused: header shows Not saved", await q.inner_text("#savechip") == "Not saved", await q.inner_text("#savechip"))
        await c.close()
        # phones: no header button, Save now in the menu
        c = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.add_init_script("localStorage.setItem('caf-dti-lang','fr')"); await q.goto(url); await q.wait_for_timeout(500)
        check("phone: header button hidden", await q.is_hidden("#save-now"))
        await q.click("#menu-btn"); check("phone: Save now in the menu (French)", (await q.inner_text("#save-now-menu")) == "Enregistrer maintenant", await q.inner_text("#save-now-menu"))
        await q.click("#save-now-menu"); t = await toast(q); check("phone: saves from the menu", "Enregistré dans cet onglet" in t, t)
        check("no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [])
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
