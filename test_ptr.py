import sys, pathlib, asyncio
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/web-beta/index.html").resolve().as_uri(); shots = base/"shots"
PULL = """(dist) => new Promise(res => { const t = document.querySelector('.sec h2') || document.body;
  const mk = y => new Touch({ identifier: 1, target: t, clientX: 200, clientY: y });
  const fire = (type, y) => t.dispatchEvent(new TouchEvent(type, { touches: type === 'touchend' ? [] : [mk(y)], changedTouches: [mk(y)], bubbles: true }));
  fire('touchstart', 150); let i = 0; const n = 10;
  const step = () => { i++; fire('touchmove', 150 + dist * i / n); if (i < n) setTimeout(step, 25); else { window.__ptrShot = 1; setTimeout(() => { fire('touchend', 150 + dist); res(); }, 250); } }; setTimeout(step, 25); })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(**{k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"})
        await c.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true});")
        q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(url); await q.wait_for_timeout(500)
        print("standalone class:", await q.evaluate("document.documentElement.className"))
        await q.fill("#trip-ref", "Pull test trip"); await q.wait_for_timeout(700)
        # short pull: no reload
        nav = []; q.on("framenavigated", lambda f: nav.append(f.url))
        await q.evaluate(PULL, 80); await q.wait_for_timeout(500); print("short pull reloads:", bool(nav))
        # long pull: reload, state kept, toast
        task = asyncio.ensure_future(q.evaluate(PULL, 220))
        await q.wait_for_timeout(330); await q.screenshot(path=str(shots/"ptr.png"), clip={"x":0,"y":0,"width":390,"height":160})
        try: await task
        except Exception: pass
        await q.wait_for_timeout(1500)
        print("long pull reloaded:", bool(nav), "| trip kept:", await q.input_value("#trip-ref"), "| toast:", await q.inner_text("#toast"))
        # browser tab (not installed): no pull handling
        c2 = await b.new_context(**{k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"}); r = await c2.new_page(); await r.goto(url); await r.wait_for_timeout(400)
        print("in Safari tab, standalone class:", repr(await r.evaluate("document.documentElement.className")))
        print("errors:", errs); await b.close()
asyncio.run(main())
