# Colour themes: production is navy and blue, the beta is violet, each in light and dark mode.
# Also guards the beta-only stylesheet against comments that swallow its rules.
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1])
WANT = {("web", "light"): "#0b4f8c", ("web", "dark"): "#7fb2e8", ("web-beta", "light"): "#5a3e9e", ("web-beta", "dark"): "#b7a2ec"}
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
css = (base / "pwa/beta.css").read_text()
body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
check("beta.css has no text outside comments and rules", not re.search(r"[A-Za-z]{3,}[^{};]*\s[A-Za-z]{3,}[^{};:]*;", re.sub(r"\{[^}]*\}", "{}", body.replace("@media (prefers-color-scheme: dark){", ""))), body[:200])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for (ch, scheme), want in WANT.items():
            q = await (await b.new_context(color_scheme=scheme)).new_page()
            await q.goto((base / f"out/{ch}/index.html").resolve().as_uri()); await q.wait_for_timeout(300)
            got = (await q.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--accent')")).strip().lower()
            check(f"{ch} {scheme}: accent {want}", got == want, got)
        await b.close()
    print("failures:", fails)
asyncio.run(main())
