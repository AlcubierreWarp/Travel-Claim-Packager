# Leave and field days in the meals section: the helper sets them (leave stops, Field stays), the member can change
# any day, Field days and Field stays stay in step, a second day set the same way offers the days in between, changed
# days are marked in both layouts, and drafts from before version 4 move their calls into general expenses.
import sys, pathlib, asyncio, json
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]).resolve(); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
def text(f): return " ".join(p.extract_text() for p in PdfReader(str(f)).pages)
ROW = "(d) => { const r = document.querySelector(`#meal-${d}-b`).closest('tr'); return { cls: r.className, on: [...r.querySelectorAll('td.st .dst.on')].map(b => b.dataset.st), man: !!r.querySelector('td.st .dst-auto'), b: document.getElementById(`meal-${d}-b`).checked } }"
FIELD = "() => [...document.querySelectorAll('#rows-stays .stay')].filter(e => e.querySelector('.stay-kind.fld')).map(e => [e.querySelector('[data-k=checkin]').value, e.querySelector('[data-k=checkout]').value])"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        c = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True); q = await c.new_page()
        q.on("pageerror", lambda e: errs.append(str(e)))
        await q.goto((base / "out/web-beta/index.html").as_uri()); await q.wait_for_timeout(600)
        await q.click("#menu-btn"); await q.click("#beta-testdata"); await q.wait_for_timeout(1500)
        r = await q.evaluate(ROW, "2026-11-12"); check("a Field stay makes its night a field day, meals unticked", r["on"] == ["field"] and "fd" in r["cls"] and not r["b"] and not r["man"], r)
        r = await q.evaluate(ROW, "2026-11-14"); check("a day changed by hand shows Leave and the way back", r["on"] == ["leave"] and r["man"], r)
        # Field on a duty day adds a Field stay for that night
        await q.click('#sec-EM td.st [data-act=day-st][data-date="2026-11-10"][data-st=field]'); await q.wait_for_timeout(200)
        r = await q.evaluate(ROW, "2026-11-10"); fs = await q.evaluate(FIELD)
        check("Field on 10 Nov: a field day, not marked as changed (lodging backs it)", r["on"] == ["field"] and not r["man"] and not r["b"], r)
        check("Field on 10 Nov: a Field stay for that night in lodging", ["2026-11-10", "2026-11-11"] in fs, fs)
        check("the toast says where the field nights went", "section D" in await q.inner_text("#toast"))
        # tapping it again takes the night back out
        await q.click('#sec-EM td.st [data-act=day-st][data-date="2026-11-10"][data-st=field]'); await q.wait_for_timeout(200)
        fs = await q.evaluate(FIELD); r = await q.evaluate(ROW, "2026-11-10")
        check("Field off again: the night leaves lodging, the day is a duty day with meals ticked", ["2026-11-10", "2026-11-11"] not in fs and r["on"] == [] and r["b"], (fs, r))
        # Leave and Field are one choice
        await q.click('#sec-EM td.st [data-act=day-st][data-date="2026-11-12"][data-st=leave]'); await q.wait_for_timeout(200)
        r = await q.evaluate(ROW, "2026-11-12"); fs = await q.evaluate(FIELD)
        check("Leave on a field day replaces Field and takes the night out of the Field stay", r["on"] == ["leave"] and r["man"] and fs == [], (r, fs))
        await q.click('#sec-EM td.st [data-act=day-auto][data-date="2026-11-12"]'); await q.wait_for_timeout(200)
        r = await q.evaluate(ROW, "2026-11-12"); check("the way back to automatic: no longer marked, a duty day again", r["on"] == [] and not r["man"], r)
        await q.click("#toast button"); await q.wait_for_timeout(200)
        r = await q.evaluate(ROW, "2026-11-12"); check("Undo brings the day back as it was", r["on"] == ["leave"] and r["man"], r)
        # a second day set the same way offers the days in between
        await q.click('#sec-EM td.st [data-act=day-st][data-date="2026-11-09"][data-st=field]'); await q.wait_for_timeout(150)
        await q.click('#sec-EM td.st [data-act=day-st][data-date="2026-11-11"][data-st=field]'); await q.wait_for_timeout(200)
        btn = await q.inner_text("#toast button"); check("a second Field day offers the day between", "10 Nov" in btn, btn)
        await q.click("#toast button"); await q.wait_for_timeout(200)
        fs = await q.evaluate(FIELD); st = [(await q.evaluate(ROW, d))["on"] for d in ("2026-11-09", "2026-11-10", "2026-11-11")]
        check("filling the gap: three field days in one Field stay", st == [["field"]] * 3 and ["2026-11-09", "2026-11-12"] in fs, (st, fs))
        # the last day of the trip has no night, so Field there is a change by the member
        await q.click('#sec-EM td.st [data-act=day-st][data-date="2026-11-15"][data-st=field]'); await q.wait_for_timeout(200)
        r = await q.evaluate(ROW, "2026-11-15"); check("Field on the last day: kept as a change, no stay past the trip", r["on"] == ["field"] and r["man"] and all(x[1] <= "2026-11-15" for x in await q.evaluate(FIELD)), r)
        # both layouts show the status and the asterisk
        await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
        async with q.expect_download() as dl: await q.click("#build-btn")
        f = fx / "status-std.pdf"; await (await dl.value).save_as(str(f)); t = text(f)
        check("standard: a Leave / field column with the changed days marked", "LEAVE / FIELD" in t and "Field*" in t and "Leave*" in t and "Changed by the member" in t)
        check("standard: sections in ClaimsX order, meals last, no calls register", t.index("GENERAL EXPENSES") < t.index("CURRENCY EXCHANGE") < t.index("MEALS") and "CALLS REGISTER" not in t)
        await q.click("#menu-btn"); await q.check("#opt-pretty"); await q.keyboard.press("Escape")
        async with q.expect_download() as dl: await q.click("#build-btn")
        f = fx / "status-pretty.pdf"; await (await dl.value).save_as(str(f)); t = text(f)
        check("designed: the summary lists the field nights and the changed days", "nights in the field" in t and "Days you changed by hand" in t)
        check("designed: meals show Field* and Leave*", "Field*" in t and "Leave*" in t)
        # a draft from version 1.9: calls become general expenses, opened sections follow their new letters
        old = {"app": "caf-digital-travel-itinerary", "v": 3, "state": {"v": 3, "tripRef": "Old draft", "stops": [{"city": "Home", "depDate": "2026-11-02"}, {"city": "Home", "arrDate": "2026-11-03"}],
               "general": [{"date": "2026-11-02", "desc": "Laundry", "cost": "10", "cur": "CAD", "rc": []}],
               "calls": [{"date": "2026-11-03", "location": "Ottawa", "timeDur": "0900, 5 min", "number": "613-555-0101", "person": "Orderly room", "kind": "Business", "cost": "2.50", "cur": "CAD", "rc": [], "lost": True, "lostReason": "no receipt"}],
               "touched": {"F": True, "G": True, "H": True, "E": True}}, "receipts": {}}
        d = fx / "old-draft.json"; d.write_text(json.dumps(old))
        await q.click("#menu-btn"); await q.keyboard.press("Escape"); await q.set_input_files("#file-draft", str(d)); await q.wait_for_timeout(900)
        await q.click("#menu-btn")
        async with q.expect_download() as dl: await q.click("[data-act=save-draft]")
        nd = fx / "old-draft-saved.json"; await (await dl.value).save_as(str(nd)); st = json.loads(nd.read_text())["state"]
        g = [[r["desc"], r["cost"], r["lost"]] for r in st["general"]]; tch = st["touched"]
        check("old draft: the call is now a general expense, receipt status kept", len(g) == 2 and g[1][0].startswith("Business call, Orderly room, 613-555-0101") and g[1][1] == "2.50" and g[1][2] is True, g)
        check("old draft: opened sections keep their meaning under the new letters", tch.get("E") and tch.get("F") and tch.get("G") and "H" not in tch, tch)
        check("old draft: no calls section on the page", await q.locator("#sec-H, #rows-calls").count() == 0)
        print("errors:", errs); errs and fails.append("page errors")
        print("failures:", fails); await b.close()
asyncio.run(main())
