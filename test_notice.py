import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base/"shots"
SWIPE = """(dx) => new Promise(res => { const el = document.querySelector('#localonly'); const r = el.getBoundingClientRect(); const y = r.top + r.height/2, x = r.left + r.width*0.6;
  const ev = (t, cx) => el.dispatchEvent(new PointerEvent(t, { pointerId: 7, pointerType: 'touch', clientX: cx, clientY: y, bubbles: true, isPrimary: true }));
  ev('pointerdown', x); let i = 0; const steps = 8; const tick = () => { i++; ev('pointermove', x + dx*i/steps); if (i < steps) setTimeout(tick, 30); else { ev('pointerup', x + dx); setTimeout(res, 400); } }; setTimeout(tick, 30); })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width":1320,"height":900}); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(400)
        await q.screenshot(path=str(shots/"notice-desktop.png"), clip={"x":0,"y":0,"width":1320,"height":160})
        await q.click(".lo-close"); await q.wait_for_timeout(200)
        print("desktop X: hidden", not await q.is_visible("#localonly"), "| toast:", await q.inner_text("#toast"))
        await q.click("#menu-btn"); print("  menu restore item visible:", await q.is_visible("#show-notice")); await q.keyboard.press("Escape")
        await q.reload(); await q.wait_for_timeout(400); print("  after reload hidden:", not await q.is_visible("#localonly"))
        await q.click("#menu-btn"); await q.click("#show-notice"); await q.wait_for_timeout(200)
        print("  restored:", await q.is_visible("#localonly"), "| menu item hidden:", await q.eval_on_selector("#show-notice", "e => e.hidden"))
        await q.click(".lo-close"); await q.click("#toast button"); await q.wait_for_timeout(200); print("  undo restores:", await q.is_visible("#localonly"))
        # phone swipe
        m = await b.new_context(**{k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"}); r = await m.new_page(); r.on("pageerror", lambda e: errs.append(str(e)))
        await r.goto(url); await r.wait_for_timeout(400)
        await r.screenshot(path=str(shots/"notice-phone.png"), clip={"x":0,"y":0,"width":390,"height":200})
        await r.evaluate(SWIPE, -60); print("phone short swipe stays:", await r.is_visible("#localonly"))
        await r.evaluate(SWIPE, -220); print("  long swipe left hides:", not await r.is_visible("#localonly"), "| toast:", await r.inner_text("#toast"))
        await r.click("#toast button"); await r.wait_for_timeout(200)
        await r.evaluate(SWIPE, 220); print("  swipe right hides:", not await r.is_visible("#localonly"))
        await r.click("#menu-btn"); await r.click("#show-notice"); await r.wait_for_timeout(200)
        await r.click(".lo-more summary"); await r.wait_for_timeout(200); print("  More still opens:", await r.eval_on_selector(".lo-more", "e => e.open"), "| visible:", await r.is_visible("#localonly"))
        await r.screenshot(path=str(shots/"notice-phone-open.png"), clip={"x":0,"y":0,"width":390,"height":260})
        print("errors:", errs); await b.close()
asyncio.run(main())
