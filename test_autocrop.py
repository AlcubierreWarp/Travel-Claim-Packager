# Crop guesses the receipt's corners when it opens: found on the usual surfaces (dark table, wood, carpet with a
# shadow, angled or partly out of frame), and the whole photo when it cannot tell (white on white, no receipt).
import sys, pathlib, asyncio, random, math, time
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFilter
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True); (base / "shots").mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
random.seed(7)
def rot(cx, cy, w, h, a, persp=0):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2 + persp), (w / 2, h / 2 - persp), (-w / 2, h / 2)]
    ca, sa = math.cos(a), math.sin(a); return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
def receipt(im, quad, paper=(248, 247, 242)):
    d = ImageDraw.Draw(im); d.polygon(quad, fill=paper)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = quad
    for k in range(1, 12):  # print lines across the paper
        t = k / 12; a = (x0 + (x3 - x0) * t, y0 + (y3 - y0) * t); b = (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        a2 = (a[0] + (b[0] - a[0]) * .12, a[1] + (b[1] - a[1]) * .12); b2 = (a[0] + (b[0] - a[0]) * (.5 + .4 * random.random()), a[1] + (b[1] - a[1]) * (.5 + .4 * random.random()))
        d.line([a2, b2], fill=(30, 30, 30), width=6)
def noise(im, amt):
    px = im.load(); w, h = im.size
    for _ in range(w * h // 6):
        x, y = random.randrange(w), random.randrange(h); r, g, b = px[x, y]; v = random.randint(-amt, amt); px[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))
def wood(w, h):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for y in range(h): v = int(18 * math.sin(y / 9) + 10 * math.sin(y / 31)); d.line([(0, y), (w, y)], fill=(120 + v, 78 + v // 2, 45))
    return im
def carpet_shadow(w, h):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for x in range(w): v = int(110 - 60 * x / w); d.line([(x, 0), (x, h)], fill=(v, v, v + 6))
    noise(im, 30); return im
CASES = [  # name, background, quad, expect found
    ("dark table, angled", lambda w, h: Image.new("RGB", (w, h), (45, 48, 50)), [(300, 200), (900, 260), (860, 1400), (260, 1350)], True),
    ("wood, turned 35 degrees", wood, rot(600, 800, 520, 1000, math.radians(35)), True),
    ("carpet with a shadow, slight perspective", carpet_shadow, rot(620, 780, 560, 1100, math.radians(-8), persp=40), True),
    ("partly out of frame", lambda w, h: Image.new("RGB", (w, h), (60, 70, 85)), [(330, 300), (930, 330), (950, 1700), (310, 1700)], True),
    ("white on a white counter", lambda w, h: Image.new("RGB", (w, h), (236, 236, 233)), [(300, 200), (900, 260), (860, 1400), (260, 1350)], False),
    ("no receipt at all", carpet_shadow, None, False),
]
async def main():
    W0, H0 = 1200, 1600
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto((base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()); await q.wait_for_timeout(500)
        for i, (name, bg, quad, found) in enumerate(CASES):
            im = bg(W0, H0)
            if quad: receipt(im, quad)
            im = im.filter(ImageFilter.GaussianBlur(1.2)); noise(im, 8)
            f = fx / f"auto-{i}.jpg"; im.save(f, quality=88)
            await q.set_input_files("#file-snap", str(f)); await q.wait_for_selector("#snap[open]")
            t0 = time.time(); await q.click("[data-act=snap-crop]"); await q.wait_for_selector("#crop[open]"); await q.wait_for_timeout(150); dt = time.time() - t0
            svg = q.locator("#crop-svg"); sw = float(await svg.get_attribute("width")); k = sw / W0
            got = await q.eval_on_selector_all("#crop-svg .hit", "cs => cs.map(c => [+c.getAttribute('cx'), +c.getAttribute('cy')])")
            got = [(x / k, y / k) for x, y in got]; hint = await q.inner_text("#crop-hint")
            if found:
                want = [(min(W0, max(0, x)), min(H0, max(0, y))) for x, y in quad]
                err = max(math.hypot(a[0] - b2[0], a[1] - b2[1]) for a, b2 in zip(got, want)); diag = math.hypot(W0, H0)
                print(f"  {name}: worst corner off by {err:.0f} px ({100 * err / diag:.1f}% of the diagonal), {dt * 1000:.0f} ms")
                check(f"{name}: corners found on the receipt", err < .025 * diag and "Check the corners" in hint, (err, hint))
            else:
                full = [(0, 0), (W0, 0), (W0, H0), (0, H0)]; err = max(math.hypot(a[0] - b2[0], a[1] - b2[1]) for a, b2 in zip(got, full))
                print(f"  {name}: {'whole photo' if err < 8 else 'a guess'}, {dt * 1000:.0f} ms")
                check(f"{name}: falls back to the whole photo", err < 8 and "Drag the corners" in hint, (got, hint))
            if i == 2: await q.screenshot(path=str(base / "shots/autocrop.png"))
            await q.click("#crop [data-act=crop-cancel] >> nth=-1"); await q.click("#snap [data-act=snap-cancel] >> nth=-1"); await q.wait_for_timeout(150)
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
