import asyncio
from playwright.async_api import async_playwright
B = "http://localhost:8765/Travel-Claim-Packager/"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(); errs = []
        for url in (B, B + "beta/"):
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto(url); await pg.wait_for_timeout(1500)
            await pg.evaluate("navigator.serviceWorker.ready"); await pg.wait_for_timeout(800)
            print(url, "|", await pg.inner_text(".sitefoot p"))
            print("  sw scope:", await pg.evaluate("navigator.serviceWorker.ready.then(r => r.scope)"))
        print("caches:", await pg.evaluate("caches.keys()"))
        print("dbs:", [d["name"] for d in await pg.evaluate("indexedDB.databases()")])
        # reload prod: beta cache must survive
        pg2 = await ctx.new_page(); await pg2.goto(B); await pg2.wait_for_timeout(1000)
        print("caches after prod reload:", await pg2.evaluate("caches.keys()"))
        print("errors:", errs); await b.close()
asyncio.run(main())
