import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri(); shots = base/"shots"
DRAG = """(dx) => { const el = document.querySelector('#localonly'); const r = el.getBoundingClientRect(); const y = r.top + r.height/2, x = r.left + r.width*0.6;
  const ev = (t, cx) => el.dispatchEvent(new PointerEvent(t, { pointerId: 7, pointerType: 'touch', clientX: cx, clientY: y, bubbles: true, isPrimary: true }));
  ev('pointerdown', x); for (let i = 1; i <= 8; i++) ev('pointermove', x + dx*i/8); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for scheme in ("light", "dark"):
            c = await b.new_context(**{k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"}, color_scheme=scheme); r = await c.new_page(); r.on("pageerror", lambda e: errs.append(str(e)))
            await r.goto(url); await r.wait_for_timeout(400)
            await r.evaluate(DRAG, -90); await r.wait_for_timeout(100); await r.screenshot(path=str(shots/f"swipe-{scheme}-l.png"), clip={"x":0,"y":40,"width":390,"height":110})
            await r.evaluate(DRAG, -100); await r.wait_for_timeout(100)  # continues from same pointer: total beyond threshold
            await r.goto(url); await r.wait_for_timeout(300)
            await r.evaluate(DRAG, 150); await r.wait_for_timeout(100); print(scheme, "armed at 150:", await r.eval_on_selector("#localonly", "e => e.className"))
            await r.screenshot(path=str(shots/f"swipe-{scheme}-r.png"), clip={"x":0,"y":40,"width":390,"height":110})
            await c.close()
        print("errors:", errs); await b.close()
asyncio.run(main())
