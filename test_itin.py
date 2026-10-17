# Itinerary import: fictional Amex GBT style itineraries (no real traveller data).
# Builds a PDF, two .eml files and pasted text, imports each, and checks section B.
import sys, pathlib, asyncio, base64, quopri, json
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()
fx = base / "fixtures"; fx.mkdir(exist_ok=True); shots = base / "shots"; shots.mkdir(exist_ok=True)
YWG = "Winnipeg James Armstrong Richardson Intl Airport, Winnipeg, Canada (YWG)"
YYZ = "Toronto Lester B. Pearson Intl Airport, Toronto, Canada (YYZ)"
YOW = "Ottawa Macdonald–Cartier Intl Airport, Ottawa, Canada (YOW)"
def fl(no, a, ad, b, bd): return [("Air Canada", ""), (f"Flight # {no}", "Booking reference: TSTAC1"), ("Status: Booked", ""), ("Departing:", a), ("Date/time:", ad), ("Arriving:", b), ("Date/time:", bd), ("Duration:", "2h00m")]
TRIP_A = [("E-Ticket Itinerary Receipt And Invoice", ""), ("ITINERARY DETAILS", ""), ("Trip locator:", "QA7TST"), ("Traveller:", "Mr JOHN ALEX</td><td>VAN DER BERG</td><td>Travel Directive Module :"), ("TAN :", "TST12345"),
  ("ITINERARY SUMMARY", ""), ("Traffic Date From-to/location Supplier Times Class/room Status", ""),
  ("02 Dec 2026", "YWG - YYZ AC1234 07:45-11:05 Economy Booked"), ("02 Dec 2026", "YYZ - YOW AC1456 12:30-13:35 Economy Booked"), ("06 Dec 2026", "YOW - YWG AC1789 17:30-19:40 Economy Booked"),
  ("E-TICKET 1", ""), ("Ticket number:", "0140000000001"), ("Issuing Airline:", "Air Canada"), ("Fare amount:", "800.00 CAD"), ("Ticket amount:", "912.34 CAD")] \
  + fl("AC1234", YWG, "02 December 2026, 07:45", YYZ, "02 December 2026, 11:05") + fl("AC1456", YYZ, "02 December 2026, 12:30", YOW, "02 December 2026, 13:35") \
  + [("Enterprise Rent-A-Car", ""), ("Car rental", "Confirmation: TST999"), ("Pick-up:", YOW), ("Date/time:", "02 December 2026, 14:00"), ("Drop-off:", YOW), ("Date/time:", "06 December 2026, 15:00"),
     ("Sample Suites Kingston", ""), ("Address:", "1 Example Street, Kingston, ON, K7L 1A1, Canada"), ("Check-in:", "02 December 2026"), ("Check-out:", "06 December 2026")] \
  + fl("AC1789", YOW, "06 December 2026, 17:30", YWG, "06 December 2026, 19:40") \
  + [("SERVICE FEES", ""), ("Fee 1 Base:", "46.31 CAD"), ("Fee 1 Taxes:", "6.02 CAD HST"), ("Fee 1 Total:", "52.33 CAD"), ("GENERAL INFORMATION", ""), ("Please allow 2hrs for domestic (Canada) check-in by train or plane.", "")]
TRIP_B = [("VIA Rail Canada", ""), ("Train # 33", "Booking reference: TSTVIA"), ("Departing:", "Ottawa Station, Ottawa, Canada"), ("Date/time:", "10 December 2026, 09:25"),
  ("Arriving:", "Montreal Central Station, Montreal, Canada"), ("Date/time:", "10 December 2026, 11:20"), ("Orleans Express Bus", ""), ("Departing:", "Montreal Bus Terminal, Montreal, Canada"),
  ("Date/time:", "12 December 2026, 16:00"), ("Arriving:", "Ottawa Bus Station, Ottawa, Canada"), ("Date/time:", "12 December 2026, 18:30"), ("Ticket amount:", "120.00 CAD")]
def html(rows, img=""):
    # rows with extra cells get a table of their own so their columns are not squeezed
    tr = "".join(f"</table><table><tr><td>{a}</td><td>{b}</td></tr></table><table>" if "</td>" in b else f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>td{{padding:1px 8px;font:11px Arial}}</style></head><body>{img}<table>{tr}</table></body></html>"
def eml(parts):
    out = ["From: GBT <noreply@example.com>", "To: member@example.com", "Subject: Itinerary QA7TST", "MIME-Version: 1.0", 'Content-Type: multipart/mixed; boundary="BOUNDARY1"', "", "preamble"]
    for hdr, body in parts: out += ["--BOUNDARY1", *hdr, "", body]
    return "\r\n".join(out + ["--BOUNDARY1--", ""])
EXPECT_A = [("Residence", "", "", "2026-12-02", "", ""), ("Winnipeg airport (YWG)", "2026-12-02", "", "2026-12-02", "0745", "CAL"), ("Toronto airport (YYZ)", "2026-12-02", "1105", "2026-12-02", "1230", "CAL"),
  ("Ottawa airport (YOW)", "2026-12-02", "1335", "2026-12-02", "1400", "Rental Car"), ("Kingston", "2026-12-02", "", "2026-12-06", "", "Rental Car"),
  ("Ottawa airport (YOW)", "2026-12-06", "1500", "2026-12-06", "1730", "CAL"), ("Winnipeg airport (YWG)", "2026-12-06", "1940", "2026-12-06", "", ""), ("Residence", "2026-12-06", "", "", "", None)]
EXPECT_B = [("Residence", "", "", "2026-12-10", "", ""), ("Ottawa train station", "2026-12-10", "", "2026-12-10", "0925", "Train"), ("Montreal", "2026-12-10", "1120", "2026-12-12", "1600", "Other"),
  ("Ottawa bus station", "2026-12-12", "1830", "2026-12-12", "", ""), ("Residence", "2026-12-12", "", "", "", None)]
EXPECT_D = [("Winnipeg airport (YWG)", "", "", "2026-12-02", "0745", "CAL"), ("Ottawa", "2026-12-02", "1105", "2026-12-06", "1730", "CAL"), ("Winnipeg airport (YWG)", "2026-12-06", "1940", "", "", None)]
fails = []
def check(name, got, want):
    ok = got == want; print(("ok   " if ok else "FAIL ") + name)
    if not ok: fails.append(name); print("  got: ", json.dumps(got, ensure_ascii=False)); print("  want:", json.dumps(want, ensure_ascii=False))
STOPS = """() => [...document.querySelectorAll('#itin input.city')].map(c => { const id = c.id.slice(6, -5), v = k => { const e = document.getElementById('stops-' + id + '-' + k); return e ? e.value : null; };
  return [c.value, v('arrDate') || '', v('arrTime') || '', v('depDate') || '', v('depTime') || '', v('mode')]; })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs, reqs = [], []
        # fixtures
        mk = await b.new_page()
        for nm, rows in (("trip_a", TRIP_A), ("trip_b", TRIP_B)):
            await mk.set_content(html(rows)); await mk.pdf(path=str(fx / f"{nm}.pdf"), format="Letter")
        pdf_b = base64.encodebytes((fx / "trip_b.pdf").read_bytes()).decode()
        (fx / "trip_b.eml").write_text(eml([(["Content-Type: text/plain; charset=utf-8"], "Your itinerary is attached."),
            (['Content-Type: application/pdf; name="QA7TST.pdf"', "Content-Transfer-Encoding: base64", 'Content-Disposition: attachment; filename="QA7TST.pdf"'], pdf_b)]))
        body = quopri.encodestring(html(TRIP_A, "<img src='https://example.com/track.gif'>").encode("utf-8")).decode()
        (fx / "trip_a_html.eml").write_text(eml([(["Content-Type: text/html; charset=utf-8", "Content-Transfer-Encoding: quoted-printable"], body)]))
        (fx / "outlook.msg").write_bytes(b"\xd0\xcf\x11\xe0 not really")
        await mk.close()
        c = await b.new_context(viewport={"width": 1320, "height": 900}); q = await c.new_page()
        q.on("pageerror", lambda e: errs.append(str(e)))
        q.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
        await q.goto(url); await q.wait_for_timeout(400)
        async def imp(files=None, text=None, fare=False, res=True):
            await q.click("[data-act=imp-open]")
            if files: await q.set_input_files("#file-itin", [str(fx / f) for f in files])
            else: await q.fill("#imp-text", text); await q.click("[data-act=imp-read-text]")
            await q.wait_for_selector("#imp-review:not([hidden])", timeout=20000)
            if not res: await q.uncheck("#imp-res")
            if fare: await q.check("#imp-fare")
            return await q.inner_text("#imp-review")
        check("TAN and trip locator hidden before an import", await q.is_hidden("#trip-refs"), True)
        # A: PDF with a connection, a rental car and a hotel in another city
        prev = await imp(["trip_a.pdf"], fare=True); print(prev)
        await q.locator("#imp").screenshot(path=str(shots / "imp-preview.png"))
        n_tr = await q.eval_on_selector_all("#rows-transport .row", "e => e.length"); n_st = await q.eval_on_selector_all("#rows-stays .stay", "e => e.length")
        before = await q.evaluate(STOPS)
        check("A: existing name kept unless asked", await q.is_checked("#imp-name"), False)
        check("A: name offered as a replacement", "John Alex Van Der Berg" in prev and "Replace your name" in prev, True)
        name0 = [await q.input_value(x) for x in ("#m-sur", "#m-given", "#sd-name")]
        await q.click("#imp-apply"); await q.wait_for_timeout(300)
        check("A: name left alone", [await q.input_value(x) for x in ("#m-sur", "#m-given", "#sd-name")], name0)
        check("A: TAN and trip locator shown after import", await q.is_visible("#trip-refs"), True)
        check("A: TAN and trip locator filled", [await q.input_value("#trip-tan"), await q.input_value("#trip-loc")], ["TST12345", "QA7TST"])
        check("A: section B from PDF", await q.evaluate(STOPS), [list(x) for x in EXPECT_A])
        check("A: fare row added with the PDF as receipt", (await q.eval_on_selector_all("#rows-transport .row", "e => e.length")) - n_tr, 1)
        last = await q.inner_text("#rows-transport .row:last-child"); check("A: fare row has receipt", "trip_a.pdf" in last, True)
        tr = await q.eval_on_selector_all("#rows-transport .row:last-child input", "es => es.map(e => e.value)"); check("A: fare amount 912.34 + 52.33", "964.67" in tr, True)
        check("A: hotel stay added", (await q.eval_on_selector_all("#rows-stays .stay", "e => e.length")) - n_st >= 1, True)
        print(await q.inner_text("#toast"))
        await q.click("#toast button"); await q.wait_for_timeout(200)
        check("A: undo restores section B", await q.evaluate(STOPS), before)
        check("A: undo removes fare row", await q.eval_on_selector_all("#rows-transport .row", "e => e.length"), n_tr)
        check("A: undo clears TAN", await q.input_value("#trip-tan"), "")
        check("A: undo hides TAN and trip locator", await q.is_hidden("#trip-refs"), True)
        # A2: replacing the name only when asked
        await imp(["trip_a.pdf"]); await q.check("#imp-name"); await q.uncheck("#imp-hotels"); await q.click("#imp-apply"); await q.wait_for_timeout(300)
        # the package shows the TAN and trip locator under the title
        await q.evaluate("document.getElementById('sec-P').scrollIntoView()")
        async with q.expect_download() as dl: await q.click("#build-btn")
        d = await dl.value; await d.save_as(str(fx / "pkg.pdf"))
        from pypdf import PdfReader
        t1 = PdfReader(str(fx / "pkg.pdf")).pages[0].extract_text(); check("A2: TAN and trip locator on the PDF", "TAN: TST12345" in t1 and "Trip locator: QA7TST" in t1, True)

        check("A2: name replaced when ticked", [await q.input_value(x) for x in ("#m-sur", "#m-given", "#sd-name")], ["Van Der Berg", "John Alex", "John Alex Van Der Berg"])
        await imp(["trip_a.pdf"]); check("A2: same name not offered again", await q.locator("#imp-name").count(), 0); await q.click("#imp .snap-foot [data-act=imp-cancel]")
        # A3: a blank claim fills the name by default
        await q.click("[data-act=start-blank]") if await q.locator("#example-banner:not([hidden]) [data-act=start-blank]").count() else None
        await q.evaluate("() => { for (const id of ['m-sur','m-given','sd-name']) { const e = document.getElementById(id); e.value=''; e.dispatchEvent(new Event('input', {bubbles:true})); } }")
        await imp(["trip_a.pdf"]); check("A3: blank name filled by default", await q.is_checked("#imp-name"), True); await q.click("#imp-apply"); await q.wait_for_timeout(300)
        check("A3: name filled", await q.input_value("#m-sur"), "Van Der Berg")
        # B: .eml with the PDF attached, train out and bus back
        await imp(["trip_b.eml"]); await q.click("#imp-apply"); await q.wait_for_timeout(300)
        got = await q.evaluate(STOPS); check("B: train and bus from .eml attachment", got, [list(x) for x in EXPECT_B])
        check("B: bus shown as Other: Bus", await q.eval_on_selector_all("#itin input.mode-other", "es => es.map(e => e.value).filter(Boolean)"), ["Bus"])
        # C: .eml with only an HTML body (quoted-printable, with a remote image that must not load)
        await imp(["trip_a_html.eml"]); await q.click("#imp-apply"); await q.wait_for_timeout(300)
        check("C: section B from HTML email body", await q.evaluate(STOPS), [list(x) for x in EXPECT_A])
        # D: pasted summary table only, no residence
        txt = "ITINERARY SUMMARY\n02 Dec 2026 YWG - YOW AC1234 07:45-11:05 Economy Booked\n06 Dec 2026 YOW - YWG AC1789 17:30-19:40 Economy Booked"
        await imp(text=txt, res=False); await q.click("#imp-apply"); await q.wait_for_timeout(300)
        check("D: pasted summary rows", await q.evaluate(STOPS), [list(x) for x in EXPECT_D])
        # E: Outlook .msg is refused with a clear message
        await q.click("[data-act=imp-open]"); await q.set_input_files("#file-itin", str(fx / "outlook.msg")); await q.wait_for_selector("#imp-err:not([hidden])")
        e = await q.inner_text("#imp-err"); check("E: .msg explained", ".msg" in e, True); await q.click("#imp .snap-foot [data-act=imp-cancel]")
        # F: French
        await q.click("#lang-btn"); await q.wait_for_timeout(300)
        prev = await imp(["trip_a.pdf"]); print(prev)
        await q.locator("#imp").screenshot(path=str(shots / "imp-preview-fr.png"))
        await q.click("#imp-apply"); await q.wait_for_timeout(300)
        names = [s[0] for s in await q.evaluate(STOPS)]; print(names)
        check("F: French stop names", names[:3] + names[-3:], ["Résidence", "Aéroport de Winnipeg (YWG)", "Aéroport de Toronto (YYZ)", "Aéroport d'Ottawa (YOW)", "Aéroport de Winnipeg (YWG)", "Résidence"])
        miss = await q.evaluate("() => [...window.__i18nMissing]"); check("F: no untranslated strings", miss, [])
        await q.screenshot(path=str(shots / "imp-applied-fr.png"))
        # mobile layout of the dialog
        await q.set_viewport_size({"width": 390, "height": 844}); await imp(["trip_a.pdf"]); await q.screenshot(path=str(shots / "imp-mobile.png"))
        box = await q.locator("#imp-apply").bounding_box(); check("mobile: apply button on screen", box is not None and box["y"] + box["height"] <= 844, True)
        await q.mouse.move(195, 400); await q.mouse.wheel(0, 600); await q.wait_for_timeout(300)
        check("mobile: dialog content scrolls", (await q.evaluate("document.querySelector('#imp .snap-body').scrollTop")) > 0, True)
        check("mobile: page behind stays pinned", await q.evaluate("getComputedStyle(document.body).position"), "fixed")
        await q.click("#imp .snap-foot [data-act=imp-cancel]"); await q.locator("#sec-B").screenshot(path=str(shots / "imp-secB-mobile.png"))
        print("errors:", errs); print("external requests:", reqs); print("failures:", fails)
        await b.close()
asyncio.run(main())
