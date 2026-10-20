# Receipt photos can be cropped on the device: drag four corners (mouse, touch or arrow keys), the
# photo is straightened to that shape, from the snap dialog or later from an attached receipt (with Undo).
import sys, pathlib, asyncio, base64, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True); (base / "shots").mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
W0, H0 = 1200, 1600
QUAD = [(300, 200), (900, 260), (860, 1400), (260, 1350)]   # a white receipt seen at an angle, on a dark table
def fixture():
    im = Image.new("RGB", (W0, H0), (45, 48, 50)); d = ImageDraw.Draw(im); d.polygon(QUAD, fill=(250, 250, 248))
    for k in range(8): y = 330 + k * 120; d.line([(360, y + k * 3), (820, y + 20 + k * 3)], fill=(20, 20, 20), width=10)
    f = fx / "angled-receipt.jpg"; im.save(f, quality=90); return f
def decode(du):
    return Image.open(io.BytesIO(base64.b64decode(du.split(",", 1)[1]))).convert("RGB")
async def drag(q, i, to):
    b = await q.locator("#crop-svg").bounding_box(); s = b["width"] / W0
    hit = q.locator("#crop-svg .hit").nth(i); hb = await hit.bounding_box()
    await q.mouse.move(hb["x"] + hb["width"] / 2, hb["y"] + hb["height"] / 2); await q.mouse.down()
    tx, ty = b["x"] + to[0] * s, b["y"] + to[1] * s
    await q.mouse.move(tx, ty, steps=6)
    loupe = await q.is_visible("#crop-loupe")
    await q.mouse.up(); return loupe
async def main():
    f = fixture()
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for lang, vp in (("en", {"width": 1320, "height": 900}), ("fr", {"width": 390, "height": 844})):
            c = await b.new_context(viewport=vp, device_scale_factor=2 if lang == "fr" else 1); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}')")
            await q.goto((base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()); await q.wait_for_timeout(500)
            await q.set_input_files("#file-snap", str(f)); await q.wait_for_selector("#snap[open]")
            check(f"{lang}: snap dialog offers Crop for a photo", await q.is_visible("[data-act=snap-crop]"))
            await q.click("[data-act=snap-crop]"); await q.wait_for_selector("#crop[open]"); await q.wait_for_timeout(200)
            sb = await q.locator("#crop-stage").bounding_box()
            check(f"{lang}: the crop area fits the screen", sb["x"] >= 0 and sb["x"] + sb["width"] <= vp["width"] and sb["y"] + sb["height"] <= vp["height"], sb)
            loupes = [await drag(q, i, QUAD[i]) for i in range(4)]
            check(f"{lang}: a magnifier shows while a corner is dragged", all(loupes), loupes)
            if lang == "en":
                await q.locator("#crop-svg .hit").nth(0).focus(); await q.keyboard.press("ArrowRight"); await q.keyboard.press("ArrowLeft")
            await q.screenshot(path=str(base / f"shots/crop-{lang}.png"))
            await q.click("#crop-apply"); await q.wait_for_timeout(600)
            check(f"{lang}: back on the snap dialog after Apply", await q.is_visible("#snap") and not await q.is_visible("#crop"))
            src = await q.get_attribute("#snap-prev img", "src"); im = decode(src); w, h = im.size
            print(f"  {lang}: cropped to {w}x{h}")
            check(f"{lang}: straightened to the receipt's shape", abs(w / h - 600 / 1150) < 0.06, (w, h))
            corners = [im.getpixel((x, y)) for x, y in ((6, 6), (w - 7, 6), (w - 7, h - 7), (6, h - 7))]
            check(f"{lang}: the table around the receipt is gone", all(min(px) > 200 for px in corners), corners)
            await q.click("#snap-types label:first-child"); await q.click("[data-act=snap-save]"); await q.wait_for_timeout(400)
            # crop again later, from the attached receipt's viewer, and undo it
            await q.click("#rows-transport .thumb >> nth=-1"); await q.wait_for_selector("#lb[open]")
            check(f"{lang}: the receipt viewer offers Crop", await q.is_visible("#lb-crop"))
            before = await q.get_attribute("#rows-transport .thumb >> nth=-1 >> img", "src")
            await q.click("#lb-crop"); await q.wait_for_selector("#crop[open]"); await q.wait_for_timeout(200)
            await drag(q, 0, (0, 0)); await drag(q, 2, (W0 * 0.3, H0 * 0.3))  # in the cropped photo's own scale; any smaller area will do
            await q.click("[data-act=crop-rotate]"); await q.wait_for_timeout(200)
            await q.click("#crop-apply"); await q.wait_for_timeout(600)
            after = await q.get_attribute("#rows-transport .thumb >> nth=-1 >> img", "src")
            iw, ih = decode(after).size
            check(f"{lang}: rotate turns the photo a quarter turn", (iw, ih) == (h, w), ((iw, ih), (w, h)))
            check(f"{lang}: a cropped receipt replaces the old one on the row", after != before)
            await q.click("#toast button"); await q.wait_for_timeout(400)
            check(f"{lang}: Undo puts the earlier photo back", await q.get_attribute("#rows-transport .thumb >> nth=-1 >> img", "src") == before)
            # Cancel leaves the photo as it was
            await q.click("#rows-transport .thumb >> nth=-1"); await q.click("#lb-crop"); await q.wait_for_selector("#crop[open]")
            await drag(q, 1, (100, 100)); await q.click("#crop [data-act=crop-cancel] >> nth=-1"); await q.wait_for_timeout(300)
            check(f"{lang}: Cancel changes nothing", await q.get_attribute("#rows-transport .thumb >> nth=-1 >> img", "src") == before)
            if lang == "fr": check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
