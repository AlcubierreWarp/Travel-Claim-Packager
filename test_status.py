# Leave and field days in the meals section: the helper sets them (leave stops, Field stays) and the member can change
# any day, or a run of days, from a dialog opened by tapping the date. Field days and Field stays stay in step, the
# table does not move while lodging above it changes, and both layouts show each day as it is set, with no mark for
# who set it. Drafts from before version 4 move their calls into general expenses.
import sys, pathlib, asyncio, json
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]).resolve(); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
def text(f): return " ".join(p.extract_text() for p in PdfReader(str(f)).pages)
ROW = "(d) => { const b = document.querySelector(`.dday[data-date='${d}']`), r = b.closest('tr'); return { cls: r.className, tag: b.querySelector('.dd-s').textContent, b: document.getElementById(`meal-${d}-b`).checked, h: Math.round(b.getBoundingClientRect().height) } }"
FIELD = "() => [...document.querySelectorAll('#rows-stays .stay')].filter(e => e.querySelector('.stay-kind.fld')).map(e => [e.querySelector('[data-k=checkin]').value, e.querySelector('[data-k=checkout]').value])"
async def setday(q, d, st, to=None):
    await q.click(f'.dday[data-date="{d}"]'); await q.wait_for_selector("#dst[open]")
    await q.click(f"#dst .dst-opt.{st or 'duty'}")
    if to: await q.select_option("#dst-to", to)
    await q.click("[data-act=dst-apply]"); await q.wait_for_timeout(350)
async def run(q, errs, phone):
    tag = "phone" if phone else "desktop"
    await q.goto((base / "out/web-beta/index.html").as_uri()); await q.wait_for_timeout(600)
    await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
    r = await q.evaluate(ROW, "2026-11-12"); check(f"{tag}: a Field stay makes its night a field day, meals unticked", r["tag"] == "Field" and "fd" in r["cls"] and not r["b"], r)
    r = await q.evaluate(ROW, "2026-11-14"); check(f"{tag}: a leave day shows Leave under the date", r["tag"] == "Leave" and "lv" in r["cls"], r)
    h0 = (await q.evaluate(ROW, "2026-11-10"))["h"]
    await q.evaluate("document.querySelector('.dday[data-date=\"2026-11-10\"]').scrollIntoView({ block: 'center' })"); await q.wait_for_timeout(200)
    y0 = await q.evaluate("document.querySelector('.dday[data-date=\"2026-11-10\"]').getBoundingClientRect().top")
    await q.click('.dday[data-date="2026-11-10"]'); await q.wait_for_selector("#dst[open]")
    opts = await q.eval_on_selector_all("#dst-to option", "o => o.map(x => x.value)")
    check(f"{tag}: the dialog offers this day, or through any later day of the trip", opts[0] == "2026-11-10" and opts[-1] == "2026-11-15", opts)
    check(f"{tag}: the dialog starts on the day's current setting", await q.is_checked("#dst input[value='']"))
    await q.click("[data-act=dst-cancel]"); await q.wait_for_timeout(200)
    # a new Field run, away from the existing field night, adds a Field stay card above the table
    await setday(q, "2026-11-09", "field", "2026-11-10")
    fs = await q.evaluate(FIELD); r9, r10 = await q.evaluate(ROW, "2026-11-09"), await q.evaluate(ROW, "2026-11-10")
    check(f"{tag}: Field through a later day sets each day and adds one Field stay", r9["tag"] == r10["tag"] == "Field" and ["2026-11-09", "2026-11-11"] in fs and not r10["b"], (r9, r10, fs))
    y1 = await q.evaluate("document.querySelector('.dday[data-date=\"2026-11-10\"]').getBoundingClientRect().top")
    check(f"{tag}: the table stays where it was while lodging above it grows", abs(y1 - y0) <= 2, (y0, y1))
    check(f"{tag}: rows keep their height when a day changes", (await q.evaluate(ROW, "2026-11-10"))["h"] == h0, h0)
    check(f"{tag}: the toast says where the field nights went, with Undo", "section D" in await q.inner_text("#toast") and await q.inner_text("#toast button") == "Undo")
    # back to duty takes the nights out again
    await setday(q, "2026-11-09", "", "2026-11-10")
    fs = await q.evaluate(FIELD); r = await q.evaluate(ROW, "2026-11-10")
    check(f"{tag}: duty again: the nights leave lodging, meals ticked again", ["2026-11-09", "2026-11-11"] not in fs and r["tag"] == "" and r["b"], (fs, r))
    # Leave and Field are one choice
    await setday(q, "2026-11-12", "leave")
    r = await q.evaluate(ROW, "2026-11-12"); fs = await q.evaluate(FIELD)
    check(f"{tag}: Leave on a field day replaces Field and takes the night out of the Field stay", r["tag"] == "Leave" and fs == [], (r, fs))
    await q.click("#toast button"); await q.wait_for_timeout(300)
    check(f"{tag}: Undo brings the field day back", (await q.evaluate(ROW, "2026-11-12"))["tag"] == "Field" and await q.evaluate(FIELD) == [["2026-11-12", "2026-11-13"]])
    # a leave day from the itinerary can be set back to duty
    await setday(q, "2026-11-14", "")
    r = await q.evaluate(ROW, "2026-11-14"); check(f"{tag}: a leave day can be made a duty day, meals ticked", r["tag"] == "" and r["b"], r)
    # the last day of the trip has no night: Field there adds no stay past the trip
    await setday(q, "2026-11-15", "field")
    check(f"{tag}: Field on the last day, no stay past the trip", (await q.evaluate(ROW, "2026-11-15"))["tag"] == "Field" and all(x[1] <= "2026-11-15" for x in await q.evaluate(FIELD)))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        await run(q, errs, False)
        await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
        async with q.expect_download() as dl: await q.click("#build-btn")
        f = fx / "status-std.pdf"; await (await dl.value).save_as(str(f)); t = text(f)
        check("standard: a Leave / field column, no mark for who set a day", "LEAVE / FIELD" in t and "Field" in t and "*" not in t and "Changed by" not in t)
        check("standard: sections in ClaimsX order, meals last, no calls register", t.index("GENERAL EXPENSES") < t.index("CURRENCY EXCHANGE") < t.index("MEALS") and "CALLS REGISTER" not in t)
        await q.click("#menu-btn"); await q.check("#opt-pretty"); await q.keyboard.press("Escape")
        async with q.expect_download() as dl: await q.click("#build-btn")
        f = fx / "status-pretty.pdf"; await (await dl.value).save_as(str(f)); t = text(f)
        check("designed: the summary lists the field nights; claimed meals say Meal claimed", "in the field" in t and "Meal claimed" in t and "*" not in t)
        # a draft from version 1.9: calls become general expenses, opened sections follow their new letters
        old = {"app": "caf-digital-travel-itinerary", "v": 3, "state": {"v": 3, "tripRef": "Old draft", "stops": [{"city": "Home", "depDate": "2026-11-02"}, {"city": "Home", "arrDate": "2026-11-03"}],
               "general": [{"date": "2026-11-02", "desc": "Laundry", "cost": "10", "cur": "CAD", "rc": []}],
               "calls": [{"date": "2026-11-03", "location": "Ottawa", "timeDur": "0900, 5 min", "number": "613-555-0101", "person": "Orderly room", "kind": "Business", "cost": "2.50", "cur": "CAD", "rc": [], "lost": True, "lostReason": "no receipt"}],
               "touched": {"F": True, "G": True, "H": True, "E": True}}, "receipts": {}}
        d = fx / "old-draft.json"; d.write_text(json.dumps(old))
        await q.set_input_files("#file-draft", str(d)); await q.wait_for_timeout(900)
        await q.click("#menu-btn")
        async with q.expect_download() as dl: await q.click("[data-act=save-draft]")
        nd = fx / "old-draft-saved.json"; await (await dl.value).save_as(str(nd)); st = json.loads(nd.read_text())["state"]
        g = [[r["desc"], r["cost"], r["lost"]] for r in st["general"]]; tch = st["touched"]
        check("old draft: the call is now a general expense, receipt status kept", len(g) == 2 and g[1][0].startswith("Business call, Orderly room, 613-555-0101") and g[1][1] == "2.50" and g[1][2] is True, g)
        check("old draft: opened sections keep their meaning under the new letters", tch.get("E") and tch.get("F") and tch.get("G") and "H" not in tch, tch)
        check("old draft: no calls section on the page", await q.locator("#sec-H, #rows-calls").count() == 0)
        m = await b.new_context(**{k: v for k, v in p.devices["iPhone 13"].items() if k != "default_browser_type"}); r = await m.new_page(); r.on("pageerror", lambda e: errs.append(str(e)))
        await run(r, errs, True)
        check("phone: nothing wider than the screen", await r.evaluate("document.documentElement.scrollWidth") <= 390)
        print("errors:", errs); errs and fails.append("page errors")
        print("failures:", fails); await b.close()
asyncio.run(main())
