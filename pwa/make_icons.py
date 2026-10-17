# Builds the app icons from the owner's artwork (pwa/src/user-icon.png).
import sys, pathlib
from PIL import Image, ImageDraw
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
src = pathlib.Path(__file__).parent / "src/user-icon.png"
im = Image.open(src).convert("RGBA")
w, h = im.size; px = im.load()
white = lambda p: p[0] > 235 and p[1] > 235 and p[2] > 235
# 1) trim to the blue rounded square
xs = [x for x in range(w) if not white(px[x, h // 2])]; ys = [y for y in range(h) if not white(px[w // 2, y])]
box = (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1)
sq = im.crop(box); sw, sh = sq.size; side = max(sw, sh)
canvas = Image.new("RGBA", (side, side), (255, 255, 255, 255)); canvas.paste(sq, ((side - sw) // 2, (side - sh) // 2)); sq = canvas
p = sq.load(); n = side
# 2) fill the white corners with the colour at the nearest point of the blue square's edge, row by row
rows = []
for y in range(n):
    nonw = [x for x in range(n) if not white(p[x, y])]
    rows.append((nonw[0], nonw[-1]) if len(nonw) > n * 0.5 else None)
good = [y for y in range(n) if rows[y]]
for y in range(n):
    ref = y if rows[y] else min(good, key=lambda g: abs(g - y))
    l, r = rows[ref]
    lc, rc = p[min(l + 6, n - 1), ref], p[max(r - 6, 0), ref]
    for x in range(n):
        if white(p[x, y]) and (x < l + 8 or x > r - 8 or not rows[y]):
            p[x, y] = lc if x < n // 2 else rc
full = sq.convert("RGB")
full.resize((512, 512), Image.LANCZOS).save(out / "icon-512.png")
full.resize((192, 192), Image.LANCZOS).save(out / "icon-192.png")
full.resize((180, 180), Image.LANCZOS).save(out / "apple-touch-icon.png")
# 3) maskable: artwork scaled into the 80% safe circle on a matching gradient background
M = 1024; top, bot = full.getpixel((n // 2, 6)), full.getpixel((n // 2, n - 7))
bg = Image.new("RGB", (M, M)); d = ImageDraw.Draw(bg)
for y in range(M):
    t = y / (M - 1); d.line([(0, y), (M, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
s = int(M * 0.74); art = full.resize((s, s), Image.LANCZOS)
mask = Image.new("L", (s, s), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.19), fill=255)
bg.paste(art, ((M - s) // 2, (M - s) // 2), mask)
bg.resize((512, 512), Image.LANCZOS).save(out / "icon-maskable-512.png")
# preview: iPhone-style rounded mask, Android circle mask on the maskable icon, small size
prev = Image.new("RGB", (3 * 220 + 20, 240), (234, 237, 232))
def masked(img, shape):
    img = img.resize((200, 200), Image.LANCZOS); m = Image.new("L", (200, 200), 0); dd = ImageDraw.Draw(m)
    (dd.rounded_rectangle([0, 0, 199, 199], radius=45, fill=255) if shape == "round" else dd.ellipse([0, 0, 199, 199], fill=255))
    b = Image.new("RGB", (200, 200), (234, 237, 232)); b.paste(img, (0, 0), m); return b
prev.paste(masked(Image.open(out / "apple-touch-icon.png"), "round"), (10, 20))
prev.paste(masked(Image.open(out / "icon-maskable-512.png"), "circle"), (230, 20))
small = Image.open(out / "icon-192.png").resize((60, 60), Image.LANCZOS); prev.paste(small, (510, 90))
prev.save(out.parent / "icons-preview.png")
print("ok", box, "theme", '#%02x%02x%02x' % full.getpixel((6, n // 2)))
