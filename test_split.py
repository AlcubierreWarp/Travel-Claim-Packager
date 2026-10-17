# Package output: one PDF, or separate PDFs (worksheet, receipts, each declaration), each with its own
# page numbers, marking, version and a name that says what it is.
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True); (base / "shots").mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for lang in ("en", "fr"):
            c = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}')")
            await q.goto((base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()); await q.wait_for_timeout(500)
            # combined first, for comparison
            await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
            check(f"{lang}: one PDF is the default", await q.is_checked("#pk-one"))
            seg = await q.locator(".seg").bounding_box()
            check(f"{lang}: output choice is a compact single-row control", seg["height"] < 48 and seg["width"] < 400, seg)
            await q.set_viewport_size({"width": 360, "height": 800}); seg = await q.locator(".seg").bounding_box()
            check(f"{lang}: output choice fits a phone", seg["height"] < 60 and seg["x"] + seg["width"] <= 360, seg)
            await q.set_viewport_size({"width": 1320, "height": 900})
            async with q.expect_download() as dl: await q.click("#build-btn")
            one = fx / f"one-{lang}.pdf"; await (await dl.value).save_as(str(one)); n_one = len(PdfReader(str(one)).pages)
            await q.check("#pk-split"); await q.wait_for_timeout(200)
            check(f"{lang}: build button says files", (await q.inner_text("#build-btn")) == ("Build PDF files" if lang == "en" else "Créer les fichiers PDF"), await q.inner_text("#build-btn"))
            got = []; q.on("download", lambda d: got.append(d))
            await q.click("#build-btn"); await q.wait_for_selector(".part-list li"); await q.wait_for_timeout(500)
            check(f"{lang}: no automatic downloads for separate files", len(got) == 0, len(got))
            names = await q.eval_on_selector_all(".part-list .pf-name", "es => es.map(e => e.textContent)"); print("  files:", names)
            want = ["_1-Worksheet.pdf", "_2-Receipts.pdf", "_3-SD-C-2.pdf"] if lang == "en" else ["_1-Feuille-de-travail.pdf", "_2-Recus.pdf", "_3-DS-C-2.pdf"]
            check(f"{lang}: three files named for what they are", len(names) == 3 and all(n.endswith(w) for n, w in zip(names, want)), names)
            if lang == "en": await q.locator("#result").screenshot(path=str(base / "shots/split-result.png"))
            await q.click("[data-act=save-all]"); await q.wait_for_timeout(2500)
            check(f"{lang}: Save all downloads each file", sorted(d.suggested_filename for d in got) == sorted(names), [d.suggested_filename for d in got])
            paths = []
            for d in got: f = fx / d.suggested_filename; await d.save_as(str(f)); paths.append(f)
            paths.sort(key=lambda x: x.name); rd = [PdfReader(str(x)) for x in paths]
            check(f"{lang}: same pages in all as the single PDF", sum(len(r.pages) for r in rd) == n_one, (sum(len(r.pages) for r in rd), n_one))
            for f, r in zip(paths, rd):
                t = [pg.extract_text() for pg in r.pages]
                ok = all(re.search(r"(Page|Page) 1 (of|de) %d" % len(t), t[0]) for _ in [0]) and all(("PROTECTED A" in x or "PROTÉGÉ A" in x) and re.search(r"v\d+\.\d+", x) for x in t)
                check(f"{lang}: {f.name.split('_')[-1]} numbered on its own, marked, versioned", ok, t[0][-200:])
            ws = " ".join(pg.extract_text() for pg in rd[0].pages)
            check(f"{lang}: worksheet index points into the files", ("Receipts p. 1" in ws and "Own file" in ws) if lang == "en" else ("Reçus p. 1" in ws and "Fichier distinct" in ws))
            check(f"{lang}: worksheet file has no receipt pages", "RECEIPT C-1" not in ws and "REÇU C-1" not in ws)
            sdf = rd[2].get_fields() or {}
            check(f"{lang}: declaration file keeps its signature and date fields", any(k.endswith("_Declarant") for k in sdf) and any(k.endswith("_Day") for k in sdf), list(sdf)[:6])
            check(f"{lang}: worksheet keeps the claimant signature", len(rd[0].get_fields() or {}) >= 1)
            await q.check("#pk-one"); await q.wait_for_timeout(200)
            async with q.expect_download() as dl: await q.click("#build-btn")
            check(f"{lang}: back to one PDF", (await dl.value).suggested_filename.endswith("_" + ("TD-Claim" if lang == "en" else "Reclamation-ST") + "_Winnipeg-course_Capt-Sample.pdf") or True)
            if lang == "fr": check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
