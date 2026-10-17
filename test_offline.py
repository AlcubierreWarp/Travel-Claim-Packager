import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); c = await b.new_context(); q = await c.new_page()
        await q.goto("http://localhost:8766/beta/"); await q.evaluate("navigator.serviceWorker.ready.then(r => r.scope)"); await q.reload(); await q.wait_for_timeout(800)
        await c.set_offline(True); await q.reload(); await q.wait_for_timeout(800)
        print("offline open:", await q.inner_text(".menu-ver"))
        await q.goto("http://localhost:8766/beta/?x=1"); await q.wait_for_timeout(500); print("offline with query:", await q.inner_text(".menu-ver"))
        await b.close()
asyncio.run(main())
