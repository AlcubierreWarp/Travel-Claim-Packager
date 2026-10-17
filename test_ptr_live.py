import asyncio, time, re, pathlib
from playwright.async_api import async_playwright
U = "http://localhost:8766/beta/"
PULL = """(dist) => { const t = document.querySelector('.sec h2') || document.body;
  const mk = y => new Touch({ identifier: 1, target: t, clientX: 200, clientY: y });
  const fire = (type, y) => t.dispatchEvent(new TouchEvent(type, { touches: type === 'touchend' ? [] : [mk(y)], changedTouches: [mk(y)], bubbles: true }));
  fire('touchstart', 150); for (let i = 1; i <= 10; i++) fire('touchmove', 150 + dist * i / 10); fire('touchend', 150 + dist); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(**{k:v for k,v in p.devices["iPhone 13"].items() if k!="default_browser_type"})
        await c.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true});")
        q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        print("goto", flush=True); await q.goto(U); print("loaded", flush=True); await q.evaluate("navigator.serviceWorker.ready.then(r => r.scope)"); print("sw ready", flush=True); await q.reload(); await q.wait_for_timeout(800)
        print("controlled:", await q.evaluate("!!navigator.serviceWorker.controller"), "|", await q.inner_text(".menu-ver"))
        # publish a "new build" on the server
        f = pathlib.Path("site2/beta/index.html"); s = f.read_text().replace("beta 6, built", "beta 99, built").replace("1.3-beta.6", "1.3-beta.99"); f.write_text(s)
        t0 = time.time()
        await q.evaluate(PULL, 220)
        await q.wait_for_function("() => document.querySelector('#toast') && !document.querySelector('#toast').hidden && /date|Updated/.test(document.querySelector('#toast').textContent)", timeout=15000)
        print(f"refreshed in {time.time()-t0:.1f}s |", await q.inner_text("#toast"), "|", await q.inner_text(".menu-ver"))
        # second pull, nothing new
        t0 = time.time(); await q.evaluate(PULL, 220)
        await q.wait_for_timeout(300)
        await q.wait_for_function("() => !document.querySelector('#toast').hidden && /date|Updated/.test(document.querySelector('#toast').textContent)", timeout=15000)
        print(f"second pull {time.time()-t0:.1f}s |", await q.inner_text("#toast"))
        print("cache keys:", await q.evaluate("caches.keys().then(ks => Promise.all(ks.map(k => caches.open(k).then(c => c.keys()).then(r => [k, r.length]))))"))
        print("errors:", errs); await b.close()
asyncio.run(main())
