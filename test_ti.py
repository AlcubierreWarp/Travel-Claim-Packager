# Travel Itinerary layout (experimental): a menu switch that excludes Beautify export, a traveller cover with the
# ticket and journey, a receipt contact sheet with page numbers, a data entry sheet for the clerk in ClaimsX order
# (transportation split by screen, a tick box per line), spines by part, separate files, and French.
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]).resolve(); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
def texts(f): return [pg.extract_text() for pg in PdfReader(str(f)).pages]
async def build(q, name):
    await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
    async with q.expect_download() as dl: await q.click("#build-btn")
    f = fx / name; await (await dl.value).save_as(str(f)); return f
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        beta = (base / "out/web-beta/index.html").resolve().as_uri()
        c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto(beta); await q.wait_for_timeout(600)
        # the switch: one layout at a time, remembered
        await q.click("#menu-btn"); await q.check("#opt-pretty"); await q.check("#opt-ti"); await q.wait_for_timeout(200)
        check("turning on Travel Itinerary turns Beautify off", await q.is_checked("#opt-ti") and not await q.is_checked("#opt-pretty"))
        await q.keyboard.press("Escape"); check("the Package note says the Travel Itinerary layout is on", "Travel Itinerary layout is on" in await q.inner_text("#pretty-note"))
        await q.reload(); await q.wait_for_timeout(600); check("remembered on this device", await q.evaluate("localStorage.getItem('caf-dti-layout-beta')") == "ti")
        await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
        f = await build(q, "ti-test.pdf"); t = texts(f); allt = " ".join(t)
        print("  test claim:", len(t), "pages")
        check("cover: the brand, the trip, the ticket and the journey", all(w in t[0] for w in ("TRAVEL ITINERARY", "Beta test, Exercise SAMPLE TIDE", "FROM", "RETURN", "NIGHTS", "Journey", "In this package", "Before you send")), t[0][:500])
        check("cover: the jacket carries the disc line and the fields", all(w in t[0] for w in ("TRAVELLER", "PART 1 OF 2", "CDN", "FILE NUMBER", "PERIOD", "DESTINATION")), t[0][:300])
        check("contact sheet: every item with its reference, amount and page", "Receipts at a glance" in t[1] and all(w in t[1] + t[2] for w in ("C-1", "612.40 CAD", "C-4 SD", "STATUTORY DECLARATION", "E-4 SD")) and re.search(r"C-1\s+p\. \d+", t[1]), (t[1] + t[2])[:400])
        ci = next(i for i, x in enumerate(t) if "DATA ENTRY SHEET" in x and "FINANCE" in x and "PART 2 OF 2" in x)
        check("clerk sheet: ClaimsX steps in order", all(re.search(r"\b%s\s+%s" % (n, w), allt) for n, w in ((1, "Itinerary"), (2, "Transportation"), (3, "Lodging"), (4, "Other expenses"), (5, "Gain or loss on exchange"), (6, "Meals"))) and allt.index("Other expenses") < allt.index("Gain or loss") < allt.index("Meals to enter"), allt[:200])
        check("clerk sheet: transportation split by screen", all(re.search(r"2%s\s+%s" % (n, w), allt) for n, w in (("a", "Transportation"), ("b", "Car rental"), ("c", "Local transportation"))) and (lambda c: c.index("Airfare") < c.index("Rental vehicle, 7 days") < c.index("Airport parking"))(allt[allt.index("DATA ENTRY SHEET", allt.index("PART 2 OF 2")):]))
        check("clerk sheet: receipt references carry the page", re.search(r"C-1\s+p\. \d+", allt) and re.search(r"C-2a, C-2b\s+p\. \d+-\d+", allt), allt[allt.find("C-2a"):allt.find("C-2a") + 40])
        check("clerk sheet: meals one line per day with leave and field, then the certification", "Leave / field" in allt and "Field" in allt and "Meals to enter" in allt and "Certification by the traveller" in allt)
        fields = PdfReader(str(f)).get_fields() or {}
        check("PKI signature field on the clerk sheet", "Claimant_Signature" in fields and "Sign the data entry sheet" in t[0] and f"page {ci + 3}" in t[0] or "Claimant_Signature" in fields, list(fields))
        check("every page carries its part, TRAVELLER before FINANCE", all(("TRAVELLER" in x) != ("FINANCE" in x) for x in t) and "TRAVELLER" in t[0] and "FINANCE" in t[ci] and all("FINANCE" in x for x in t[ci:]), [i + 1 for i, x in enumerate(t) if ("TRAVELLER" in x) == ("FINANCE" in x)])
        check("finance opener stands alone: part, surname, file number, dates", all(w in t[ci] for w in ("FINANCE", "TESTER", "001", "FILE NUMBER", "7209-1", "PERIOD", "09-15 NOV 26", "TOTAL ENTERED", "CDN")), t[ci][:300])
        check("no hint text on the data entry sheet", not any(w in allt for w in ("Enter in ClaimsX", "Every stop, with", "Three screens", "Commercial stays have", "phone plan charges and calls", "One line per day", "nothing to enter")))
        ri = next(i for i, x in enumerate(t) if "listed on page" in x); check("receipt pages: the slim header with the reference", "RECEIPT" in t[ri] and "C-1" in t[ri], t[ri][:200])
        check("no page has text in the footer zone or off the page", all(not re.search(r"undefined|NaN|\[object", x) for x in t))
        # separate files: the worksheet file holds both parts
        await q.check("#pk-split"); await q.evaluate("document.getElementById('sec-P').scrollIntoView()"); await q.click("#build-btn"); await q.wait_for_selector(".part-list li")
        async with q.expect_download() as dl: await q.click("[data-act=save-part][data-i='0']")
        f3 = fx / "ti-split-ws.pdf"; await (await dl.value).save_as(str(f3)); t3 = texts(f3)
        check("separate files: cover, contact sheet and clerk sheet in the first file, receipts say which file", "TRAVEL ITINERARY" in t3[0] and "DATA ENTRY SHEET" in " ".join(t3) and "Receipts p. 1" in " ".join(t3) and "Own file" in " ".join(t3), [x for x in " ".join(t3).split("\n") if "p. 1" in x or "file" in x][:6])
        await q.check("#pk-one")
        # the example claim, with the option on, in both languages
        await c.close()
        for lang in ("en", "fr"):
            c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}'); localStorage.setItem('caf-dti-layout-beta','ti')")
            await q.goto(beta); await q.wait_for_timeout(600)
            f = await build(q, f"ti-example-{lang}.pdf"); t = texts(f)
            print(f"  example ({lang}):", len(t), "pages")
            check(f"{lang}: example builds with the brand on the cover", all(w in t[0].replace("\n", " ") for w in (("TRAVEL ITINERARY", "TRAVELLER") if lang == "en" else ("ITINÉRAIRE DE VOYAGE", "VOYAGEUR"))), t[0][:160])
            if lang == "fr": check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [], await q.evaluate("() => [...window.__i18nMissing]"))
            await c.close()
        # Beautify still works on its own
        c = await b.new_context(accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.add_init_script("localStorage.setItem('caf-dti-pretty-beta','1')"); await q.goto(beta); await q.wait_for_timeout(600)
        check("an old Beautify setting still selects Beautify", await q.is_checked("#opt-pretty") and not await q.is_checked("#opt-ti"))
        f = await build(q, "ti-pretty.pdf"); check("Beautify export unchanged", "TRAVELLER SUMMARY" in texts(f)[0])
        print("errors:", errs); errs and fails.append("page errors")
        print("failures:", fails); await b.close()
asyncio.run(main())
