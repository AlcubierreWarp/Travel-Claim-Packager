# Statutory declarations: currency exchange wording fits when the exchange happened, and the member
# can edit the facts of any declaration (printed as typed) or go back to the built wording.
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
def flat(t): return re.sub(r"\s+", " ", t)
async def opened(q, rid):
    if not await q.is_visible(f"textarea[data-sdrow='{rid}']"): await q.locator(f"details.sd-edit[data-row='{rid}'] summary").click()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for lang in ("en", "fr"):
            c = await b.new_context(viewport={"width": 1320, "height": 900}, accept_downloads=True); q = await c.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
            await q.add_init_script(f"localStorage.setItem('caf-dti-lang','{lang}')")
            await q.goto((base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()); await q.wait_for_timeout(500)
            # an exchange the day before the trip, receipt lost
            await q.click("#sec-G [data-act=add][data-sec=exchange]"); await q.wait_for_timeout(200)
            rid = await q.eval_on_selector("#rows-exchange .row:last-child", "e => e.dataset.row")
            check(f"{lang}: exchange asks where it was exchanged", ("Where exchanged" if lang == "en" else "Lieu de l'échange") in await q.evaluate("document.getElementById('sec-G').textContent"))
            await q.fill(f"#exchange-{rid}-date", "2026-11-01"); await q.fill(f"#exchange-{rid}-location", "Sample Bank, Ottawa")
            await q.fill(f"#exchange-{rid}-soldAmt", "500"); await q.fill(f"#exchange-{rid}-boughtAmt", "360"); await q.fill(f"#exchange-{rid}-boughtCur", "USD"); await q.fill(f"#exchange-{rid}-charge", "5")
            await q.click(f"#rows-exchange .row:last-child [data-act=lose]"); await q.wait_for_timeout(200)
            await q.fill(f"#exchange-{rid}-lostReason", "Lost in transit" if lang == "en" else "Perdu en transit"); await q.wait_for_timeout(300)
            await q.locator(f"details.sd-edit[data-row='{rid}'] summary").click()
            built = await q.input_value(f"textarea[data-sdrow='{rid}']"); print("  built:", flat(built))
            if lang == "en":
                check("before the trip: no 'during this duty'", "before leaving on temporary duty" in built and "During this duty" not in built, built)
                check("bank used as where, not as the duty location", "at Sample Bank, Ottawa" in built and "temporary duty in Sample Bank" not in built, built)
            else:
                check("FR before the trip", "avant de partir en service temporaire" in built and "auprès de Sample Bank" in built, built)
            await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
            async with q.expect_download() as dl: await q.click("#build-btn")
            f = fx / f"sd-{lang}.pdf"; await (await dl.value).save_as(str(f)); txt = flat(" ".join(pg.extract_text() for pg in PdfReader(str(f)).pages))
            check(f"{lang}: PDF has the built wording", flat(built.split("\n\n")[0])[:60] in txt)
            import datetime
            t = datetime.date.today(); fields = PdfReader(str(f)).get_fields() or {}
            day = [v.get("/V") for k, v in fields.items() if k.endswith("_Day")]; mon = [v.get("/V") for k, v in fields.items() if k.endswith("_Month")]; yy = [v.get("/V") for k, v in fields.items() if k.endswith("_Year")]
            print("  jurat date fields:", day[:1], mon[:1], yy[:1])
            if lang == "en": check("jurat date is today, as editable fields", day and all(d == f"{t.day}{'th' if 11 <= t.day % 100 <= 13 else {1:'st',2:'nd',3:'rd'}.get(t.day % 10, 'th')}" for d in day) and all(m == t.strftime("%B") for m in mon) and all(y == t.strftime("%y") for y in yy), (day, mon, yy))
            else: check("FR jurat date is today", day and all(d == ("1er" if t.day == 1 else str(t.day)) for d in day) and all(m.endswith(["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"][t.month - 1]) for m in mon), (day, mon))
            check(f"{lang}: form shows today's date", await q.input_value("#sd-date") == t.isoformat(), await q.input_value("#sd-date"))
            if lang == "en":
                own = "On 1 November 2026, the day before I left on temporary duty to Winnipeg, I bought 360.00 US dollars at Sample Bank, Ottawa.\n\nThe bank charged a service fee of 5.00 Canadian dollars."
                await opened(q, rid); await q.fill(f"textarea[data-sdrow='{rid}']", own); await q.click("#trip-ref"); await q.wait_for_timeout(300)
                check("edited tag shown", "Edited" in await q.inner_text("#sd-items"))
                async with q.expect_download() as dl: await q.click("#build-btn")
                f2 = fx / "sd-edited.pdf"; await (await dl.value).save_as(str(f2)); t2 = flat(" ".join(pg.extract_text() for pg in PdfReader(str(f2)).pages))
                check("PDF prints the edited wording", "the day before I left on temporary duty to Winnipeg" in t2 and "The bank charged a service fee" in t2)
                check("reason and closing still follow", "Lost in transit" in t2 and "Canada Evidence Act" in t2)
                await q.wait_for_timeout(700); await q.reload(); await q.wait_for_timeout(600)
                await opened(q, rid)
                check("edited wording survives a reload", "the day before I left" in await q.input_value(f"textarea[data-sdrow='{rid}']"))
                await q.click(f"[data-act=sd-reset][data-sdrow='{rid}']"); await q.wait_for_timeout(300)
                await opened(q, rid)
                check("reset goes back to the built wording", "before leaving on temporary duty" in await q.input_value(f"textarea[data-sdrow='{rid}']") and "Edited" not in await q.inner_text("#sd-items"))
                # an exchange during the trip uses the itinerary for where the member was
                await q.fill(f"#exchange-{rid}-date", "2026-11-03"); await q.click("#trip-ref"); await q.wait_for_timeout(300)
                await opened(q, rid)
                d = await q.input_value(f"textarea[data-sdrow='{rid}']"); print("  during:", flat(d))
                check("during the trip: duty location from the itinerary", "temporary duty in Winnipeg" in d and "During this duty, I exchanged" in d, d)
                await q.fill(f"#exchange-{rid}-date", "2026-11-08"); await q.click("#trip-ref"); await q.wait_for_timeout(300)
                await opened(q, rid)
                d = await q.input_value(f"textarea[data-sdrow='{rid}']"); print("  after:", flat(d))
                check("after the trip", "after returning from temporary duty to Winnipeg" in d, d)
                await q.locator("#sec-SD").screenshot(path=str(base / "shots/sd-edit.png"))
                # a changed date is kept; a cleared date leaves blanks for the officer
                await q.fill("#sd-date", "2026-11-20"); await q.wait_for_timeout(300)
                check("jurat preview follows the changed date", "20th day of November A.D. 2026" in await q.inner_text("#sd-jurat"), await q.inner_text("#sd-jurat"))
                async with q.expect_download() as dl: await q.click("#build-btn")
                f3 = fx / "sd-date.pdf"; await (await dl.value).save_as(str(f3)); fl = PdfReader(str(f3)).get_fields()
                check("PDF uses the changed date", [v.get("/V") for k, v in fl.items() if k.endswith("_Day")][:1] == ["20th"])
                await q.fill("#sd-date", ""); await q.wait_for_timeout(300)
                check("cleared date: blank lines in the preview", "this ____ day of" in await q.inner_text("#sd-jurat"))
                async with q.expect_download() as dl: await q.click("#build-btn")
                f4 = fx / "sd-nodate.pdf"; await (await dl.value).save_as(str(f4)); fl = PdfReader(str(f4)).get_fields()
                check("cleared date: empty fields in the PDF", all(not v.get("/V") for k, v in fl.items() if k.endswith(("_Day", "_Month", "_Year"))))
            else:
                check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [])
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
