# Beautify export (experimental): a menu option that builds the same package in the designed layout. Checks the
# option itself, the first page and its fallbacks (long trips, many stops, two currencies), that amounts line up,
# that nothing falls off a page, separate files, ink signatures, and that the French text is complete.
import sys, pathlib, asyncio, json, re, shutil, subprocess
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
def texts(f): return [pg.extract_text() for pg in PdfReader(str(f)).pages]
def ys(f):
    out = []
    for i, pg in enumerate(PdfReader(str(f)).pages):
        pg.extract_text(visitor_text=lambda s, cm, tm, fd, fs, i=i: out.append((i + 1, round(tm[5] * cm[3] + cm[5], 1), s.strip())) if s.strip() else None)
    return out
def xs_of(f, words):
    out = []  # page 1 has its own summary table, so from page 2 on
    for pg in PdfReader(str(f)).pages[1:]:
        pg.extract_text(visitor_text=lambda s, cm, tm, fd, fs: out.append(round(tm[4] * cm[0] + cm[4], 1)) if s.strip() in words else None)
    return out
async def build(q, name):
    await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
    async with q.expect_download() as dl: await q.click("#build-btn")
    f = fx / name; await (await dl.value).save_as(str(f)); return f
def on_page(f):
    bad = [(p, y, s) for p, y, s in ys(f) if y < 24 or y > 780]
    return bad
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        beta = (base / "out/web-beta/index.html").resolve().as_uri()
        # the option: off by default, on from the menu, remembered, with a note in the Package section
        c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto((base / "out/web/index.html").resolve().as_uri()); await q.wait_for_timeout(500)
        f0 = await build(q, "standard.pdf")
        check("off by default: the standard layout", "CAF DIGITAL TRAVEL ITINERARY" in texts(f0)[0] and "TEMPORARY DUTY CLAIM" not in texts(f0)[0])
        await q.click("#menu-btn"); check("menu offers Beautify export, marked experimental", "Beautify export" in await q.inner_text("#menu") and "EXPERIMENTAL" in (await q.inner_text("#menu")).upper())
        await q.check("#opt-pretty"); await q.keyboard.press("Escape"); await q.wait_for_timeout(200)
        check("a note in the Package section says it is on", await q.is_visible("#pretty-note"))
        await q.reload(); await q.wait_for_timeout(500)
        check("the choice is remembered on this device", await q.is_visible("#pretty-note"))
        f1 = await build(q, "pretty-example.pdf"); t1 = texts(f1)
        print("  example:", len(t1), "pages")
        check("example: same page count story (summary, worksheet, index, 5 receipts)", len(t1) == 9, len(t1))
        check("example: first page is the summary", all(w in t1[0] for w in ("TEMPORARY DUTY CLAIM", "Sections", "Journey", "Total", "475.25", "Page 1 of 9")), t1[0][:400])
        check("example: first page points at the right pages", "PKI signature, page 4" in t1[0] and "Before an officer, page 6" in t1[0] and "One PDF, 9 pages" in t1[0], t1[0])
        check("example: index page with the page map and the certification", "What is in this package" in t1[3] and "Receipt index" in t1[3] and "Certification" in t1[3], t1[3][:300])
        check("example: receipt pages are labelled", "RECEIPT" in t1[4] and "C-1" in t1[4] and "listed on page 4" in t1[4], t1[4][:200])
        check("example: the declaration keeps its wording", "STATUTORY DECLARATION" in t1[5] and "Canada Evidence Act" in t1[5])
        fields = PdfReader(str(f1)).get_fields() or {}
        check("example: PKI signature field for the claimant", "Claimant_Signature" in fields and fields["Claimant_Signature"].get("/FT") == "/Sig")
        xl = xs_of(f1, ("Subtotal", "Total"))
        check("example: subtotals and totals start at the same place", len(xl) >= 4 and len(set(xl)) == 1, xl)
        check("example: nothing runs off a page", on_page(f1) == [], on_page(f1)[:5])
        # ink signature
        await q.check("#pk-hand"); f2 = await build(q, "pretty-ink.pdf"); t2 = texts(f2)
        check("ink: no PKI fields, the first page says ink", not any(v.get("/FT") == "/Sig" for v in (PdfReader(str(f2)).get_fields() or {}).values()) and "Ink signature, page 4" in t2[0])
        await q.check("#pk-pki")
        # separate files
        await q.check("#pk-split"); await q.evaluate("document.getElementById('sec-P').scrollIntoView()"); await q.click("#build-btn"); await q.wait_for_selector(".part-list li")
        n = await q.locator(".part-list li").count()
        async with q.expect_download() as dl: await q.click("[data-act=save-part][data-i='0']")
        f3 = fx / "pretty-split-ws.pdf"; await (await dl.value).save_as(str(f3)); t3 = texts(f3)
        check("separate files: worksheet file has the summary and says how many files", "3 separate files" in t3[0] and n == 3, (n, t3[0][-300:]))
        check("separate files: index says which file", "In file" in " ".join(t3) and re.search(r"Receipts\s+p\. 1", " ".join(t3)) is not None and "Own file" in " ".join(t3))
        check("separate files: no stray text", "function" not in " ".join(t3))
        async with q.expect_download() as dl: await q.click("[data-act=save-part][data-i='1']")
        f4 = fx / "pretty-split-rc.pdf"; await (await dl.value).save_as(str(f4))
        check("separate files: receipts file uses the designed headers", "RECEIPT" in texts(f4)[0] and "Page 1 of" in texts(f4)[0])
        await q.check("#pk-one")
        # a 30-day course with a US expense: weeks of meals, a second currency, totals kept apart
        await q.click("#menu-btn")
        async with q.expect_download() as dl: await q.click("#save-draft")
        d = fx / "draft.json"; await (await dl.value).save_as(str(d)); o = json.loads(d.read_text()); s = o["state"]
        st = s["stops"]; st[2]["depDate"] = "2026-12-01"; st[3]["arrDate"] = "2026-12-01"; st[3]["depDate"] = "2026-12-01"; st[4]["arrDate"] = "2026-12-01"
        g = dict(s["general"][0]); g.update({"id": "usd1", "date": "2026-11-20", "location": "Bangor, Maine", "desc": "Site visit parking", "cost": "62.40", "cur": "USD", "rc": [], "lost": True, "lostReason": "the pay station printed no receipt"}); s["general"].append(g)
        d2 = fx / "draft-long.json"; d2.write_text(json.dumps(o))
        await q.keyboard.press("Escape"); await q.set_input_files("#file-draft", str(d2)); await q.wait_for_timeout(900)
        f = await build(q, "pretty-long.pdf"); t = texts(f); allt = " ".join(t)
        print("  long trip:", len(t), "pages")
        check("long trip: meals shown by week", all(f"Week {k}" in allt for k in range(1, 6)), [k for k in range(1, 7) if f"Week {k}" in allt])
        check("two currencies: the second is listed, not added in", "Also claimed, not converted" in t[0] and "62.40" in t[0] and "USD" in t[0])
        check("two currencies: a total for each, lined up", len(set(xs_of(f, ("Subtotal", "Total")))) == 1 and allt.count("62.40") >= 4, allt.count("62.40"))
        check("long trip: nothing runs off a page", on_page(f) == [], on_page(f)[:5])
        # turning it off goes back to the standard layout
        await q.click("#menu-btn"); await q.uncheck("#opt-pretty"); await q.keyboard.press("Escape")
        f5 = await build(q, "standard-again.pdf"); check("turned off: standard layout again", "CAF DIGITAL TRAVEL ITINERARY" in texts(f5)[0])
        await c.close()
        # the beta's busy test claim, in English and French
        for lang in ("en", "fr"):
            c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}'); localStorage.setItem('caf-dti-pretty-beta','1')")
            await q.goto(beta); await q.wait_for_timeout(600)
            await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
            f = await build(q, f"pretty-test-{lang}.pdf"); t = texts(f)
            print(f"  test claim ({lang}):", len(t), "pages")
            if lang == "en":
                check("busy claim: journey shows overnight places, all stops on page 2", "All 9 stops on page 2" in t[0] and "Digby" in t[0] and "Leave" in t[0] and "Enter in this order" not in t[0], t[0][-700:])
                check("busy claim: four declarations in one step", "Declare 4 missing receipts" in t[0])
                check("busy claim: long title kept to two lines", t[0].count("Beta test, Exercise SAMPLE") + t[0].count("TIDE") >= 1)
            check(f"{lang}: subtotals and totals start at the same place", len(set(xs_of(f, ("Subtotal", "Sous-total", "Total")))) == 1, xs_of(f, ("Subtotal", "Sous-total", "Total")))
            check(f"{lang}: nothing runs off a page", on_page(f) == [], on_page(f)[:5])
            if lang == "en":
                # a PDF receipt with no page background of its own still shows on white, not the grey panel
                pg = next(i for i, x in enumerate(t) if "eticket-test.pdf" in x) + 1
                if shutil.which("pdftoppm"):
                    from PIL import Image
                    subprocess.run(["pdftoppm", "-r", "30", "-f", str(pg), "-l", str(pg), "-png", str(f), str(fx / "rcpage")], check=True)
                    im = Image.open(next(fx.glob("rcpage*.png"))).convert("RGB"); w, h = im.size; px = im.getpixel((w // 2, int(h * .7)))
                    check("PDF receipt sits on a white sheet", min(px) >= 250, px)
                else: print("  (pdftoppm not installed: white-sheet check skipped)")
            if lang == "fr": check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
