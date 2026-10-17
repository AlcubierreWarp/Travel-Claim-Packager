# Statutory declarations: currency exchange wording fits when the exchange happened, and the member
# can rewrite paragraph 1 or 2 one paragraph at a time, or add a paragraph of facts. The standard
# paragraphs stay locked, a rewrite is flagged when the claim changes later, and long wording still
# fits the declaration on one page.
import sys, pathlib, asyncio, re
from playwright.async_api import async_playwright
from pypdf import PdfReader
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
fails = []
def check(n, ok, got=None): print(("ok   " if ok else "FAIL ") + n + ("" if ok else f"  (got {got!r})")); ok or fails.append(n)
def flat(t): return re.sub(r"\s+", " ", t)
async def opened(q, rid):
    if not await q.locator(f"details.sd-edit[data-row='{rid}']").evaluate("d => d.open"): await q.locator(f"details.sd-edit[data-row='{rid}'] summary").click()
async def paras(q, rid):
    await opened(q, rid)
    return await q.eval_on_selector_all(f"details.sd-edit[data-row='{rid}'] li.sd-p", "ls => ls.map(l => l.querySelector('.sd-txt') ? l.querySelector('.sd-txt').textContent : '')")
def ys(path, page):
    out = []
    PdfReader(str(path)).pages[page].extract_text(visitor_text=lambda txt, cm, tm, fd, fs: out.append(tm[5] * cm[3] + cm[5]) if txt.strip() else None)
    return out
async def longest(q, rid, lang, fx):
    TA = f"textarea.sd-para[data-sdrow='{rid}']"
    await opened(q, rid)
    # longest wording allowed in every field, Alberta (longest jurat): still one page, nothing off the page
    L = lambda n, w: (w + " ") * (n // (len(w) + 1)) + "x" * (n % (len(w) + 1))
    for k in ("1", "2", "more"):
        await q.click(f"[data-act={'sd-add' if k == 'more' else 'sd-edit'}][data-sdrow='{rid}'][data-p='{k}']"); await q.fill(TA, L(700, "words")); await q.click(f"[data-act=sd-done][data-sdrow='{rid}']"); await q.wait_for_timeout(200)
    check("each paragraph is capped", all(len(x) <= 401 for x in (await paras(q, rid))[:3]), [len(x) for x in (await paras(q, rid))[:3]])
    await q.fill(f"#exchange-{rid}-lostReason", L(400, "lost")); await q.select_option("#sd-juris", "AB"); await q.click("#trip-ref"); await q.wait_for_timeout(300)
    await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
    async with q.expect_download() as dl: await q.click("#build-btn")
    f5 = fx / f"sd-long-{lang}.pdf"; await (await dl.value).save_as(str(f5)); rd = PdfReader(str(f5))
    sdp = [i for i, pg in enumerate(rd.pages) if ("DO SOLEMNLY DECLARE" in pg.extract_text() or "DÉCLARE SOLENNELLEMENT" in pg.extract_text()) and "lost lost" in pg.extract_text()]
    y = ys(f5, sdp[0]); body = [v for v in y if v > 24]
    print("  long declaration: pages", len(rd.pages), "SD page", sdp, "lowest body text", round(min(body)), "lowest any", round(min(y)))
    check(f"{lang}: longest wording: declaration stays on one page, above the footer", len(sdp) == 1 and min(body) >= 40 and min(y) >= 14 and ("(declarant)" in rd.pages[sdp[0]].extract_text() or "(déclarant)" in rd.pages[sdp[0]].extract_text()), (sdp, min(body), min(y)))
    for k in ("1", "2"): await q.click(f"[data-act=sd-reset][data-sdrow='{rid}'][data-p='{k}']")
    await q.click(f"[data-act=sd-del][data-sdrow='{rid}']"); await q.fill(f"#exchange-{rid}-lostReason", "Lost in transit")
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
            check(f"{lang}: the first click after typing the reason opens the wording", await q.locator(f"details.sd-edit[data-row='{rid}']").evaluate("d => d.open"))
            ps = await paras(q, rid); built = "\n\n".join(ps[:2]); print("  built:", flat(built))
            check(f"{lang}: five numbered paragraphs, standard ones locked", len(ps) == 5 and await q.locator(f"details.sd-edit[data-row='{rid}'] li.sd-p.fixed [data-act=sd-edit]").count() == 0, len(ps))
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
                ED = lambda k: f"[data-act=sd-edit][data-sdrow='{rid}'][data-p='{k}']"
                TA = f"textarea.sd-para[data-sdrow='{rid}']"
                await q.click(ED(1))
                check("edit opens one paragraph, filled with its current wording", await q.locator(TA).count() == 1 and (await q.input_value(TA)) == ps[0])
                await q.fill(TA, "1. On 1 November 2026, the day before I left on temporary duty to Winnipeg,\nI bought 360.00 US dollars at Sample Bank, Ottawa")
                check("line breaks are joined as you type", "\n" not in await q.input_value(TA), await q.input_value(TA))
                await q.keyboard.press("Enter"); await q.wait_for_timeout(300)
                ps = await paras(q, rid)
                check("Enter finishes; number dropped, one paragraph, full stop added", ps[0] == "On 1 November 2026, the day before I left on temporary duty to Winnipeg, I bought 360.00 US dollars at Sample Bank, Ottawa.", ps[0])
                check("edited tag and Your wording shown", "EDITED" in (await q.inner_text(f"#sd-items > li:has(details[data-row='{rid}']) .sd-it-h")).upper() and "YOUR WORDING" in (await q.inner_text(f"details.sd-edit[data-row='{rid}'] li[data-p='1']")).upper())
                await q.click(f"[data-act=sd-add][data-sdrow='{rid}']"); await q.fill(TA, "The bank charged a service fee of 5.00 Canadian dollars"); await q.click(f"[data-act=sd-done][data-sdrow='{rid}']"); await q.wait_for_timeout(300)
                ps = await paras(q, rid)
                check("added paragraph is 3, the reason moves to 4", len(ps) == 6 and ps[2].startswith("The bank charged") and ps[3].startswith("The original receipt"), ps)
                await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
                async with q.expect_download() as dl: await q.click("#build-btn")
                f2 = fx / "sd-edited.pdf"; await (await dl.value).save_as(str(f2)); t2 = flat(" ".join(pg.extract_text() for pg in PdfReader(str(f2)).pages))
                check("PDF prints the edited and added wording", "the day before I left on temporary duty to Winnipeg, I bought" in t2 and "3. The bank charged a service fee" in t2 and "4. The original receipt" in t2, t2[-900:])
                check("reason and closing still follow", "Lost in transit" in t2 and "Canada Evidence Act" in t2)
                await q.wait_for_timeout(700); await q.reload(); await q.wait_for_timeout(600)
                check("edited wording survives a reload", (await paras(q, rid))[0].startswith("On 1 November 2026, the day before I left"))
                # the claim changes after the rewrite: flagged, then kept or replaced
                await q.fill(f"#exchange-{rid}-date", "2026-11-03"); await q.click("#trip-ref"); await q.wait_for_timeout(300)
                await opened(q, rid)
                check("rewrite flagged when the claim changes", await q.locator(f"details.sd-edit[data-row='{rid}'] li.stale").count() == 1 and "paragraph 1: the claim changed" in await q.text_content("#checks"), await q.text_content("#checks"))
                await q.click(f"[data-act=sd-keep][data-sdrow='{rid}']"); await q.wait_for_timeout(300)
                check("Keep mine clears the flag", await q.locator("#sd-items li.stale").count() == 0 and "the claim changed" not in await q.text_content("#checks"))
                await q.fill(f"#exchange-{rid}-date", "2026-11-08"); await q.click("#trip-ref"); await q.wait_for_timeout(300); await opened(q, rid)
                await q.click(f"li.stale [data-act=sd-reset][data-sdrow='{rid}']"); await q.wait_for_timeout(300)
                ps = await paras(q, rid); print("  after:", ps[0])
                check("Use the new built wording", "after returning from temporary duty to Winnipeg" in ps[0], ps[0])
                await q.click("#toast button"); await q.wait_for_timeout(300)
                check("Undo brings the rewrite back", (await paras(q, rid))[0].startswith("On 1 November 2026, the day before"))
                await q.click(f"[data-act=sd-reset][data-sdrow='{rid}'][data-p='1']"); await q.click(f"[data-act=sd-del][data-sdrow='{rid}']"); await q.wait_for_timeout(300)
                ps = await paras(q, rid)
                check("back to the built wording and five paragraphs", len(ps) == 5 and "after returning" in ps[0] and "EDITED" not in (await q.inner_text("#sd-items")).upper(), ps)
                await q.click(f"[data-act=sd-goto][data-sdrow='{rid}'][data-p='why']"); await q.wait_for_timeout(500)
                check("Change the reason goes to the expense's reason field", await q.evaluate("document.activeElement.id") == f"exchange-{rid}-lostReason")
                # an exchange during the trip uses the itinerary for where the member was
                await q.fill(f"#exchange-{rid}-date", "2026-11-03"); await q.click("#trip-ref"); await q.wait_for_timeout(300)
                d = " ".join((await paras(q, rid))[:2]); print("  during:", flat(d))
                check("during the trip: duty location from the itinerary", "temporary duty in Winnipeg" in d and "During this duty, I exchanged" in d, d)
                await q.fill(f"#exchange-{rid}-date", "2026-11-08"); await q.click("#trip-ref"); await q.wait_for_timeout(300)
                d = " ".join((await paras(q, rid))[:2]); print("  after:", flat(d))
                check("after the trip", "after returning from temporary duty to Winnipeg" in d, d)
                await q.locator("#sec-SD").screenshot(path=str(base / "shots/sd-edit.png"))
                await longest(q, rid, lang, fx)
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
                await longest(q, rid, lang, fx)
                check("FR: no untranslated strings", await q.evaluate("() => [...window.__i18nMissing]") == [])
            await c.close()
        print("errors:", errs); print("failures:", fails); await b.close()
asyncio.run(main())
