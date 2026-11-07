"""A claim file from someone else must not run code or break the page.
Opens hostile and malformed drafts, then checks nothing ran, nothing crashed and good data survived.
Also checks amounts with thousands separators and impossible dates.  python3 test_draft_safety.py ."""
import sys, json, pathlib, asyncio, base64
from playwright.async_api import async_playwright
base = pathlib.Path(sys.argv[1]); fx = base / "fixtures"; fx.mkdir(exist_ok=True)
url = (base / "out/CAF_Digital_Travel_Itinerary.html").resolve().as_uri()
PNG = "data:image/png;base64," + base64.b64encode(bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")).decode()
X = 'window.__pwned = (window.__pwned || 0) + 1'
hostile = {"app": "caf-digital-travel-itinerary", "v": 3, "state": {
    "member": {"pri": "A00 000 001", "rank": "Capt", "surname": "Tester", "given": 42, "tel": None},
    "stops": [{"id": 'a" autofocus onfocus="' + X + '" x="', "city": "Fredericton", "depDate": "2026-11-02", "depTime": "0800", "mode": "CAL"},
              {"id": "b2", "city": "Winnipeg", "arrDate": "2026-11-05"}],
    "transport": [{"id": 'r1"><img src=x onerror="' + X + '">', "date": "2026-11-02", "desc": "Taxi <b>bold</b>", "cost": "1,234.50", "cur": "CAD", "rc": ["k1", 'bad"id']},
                  {"id": "r2", "date": "2026-02-30", "desc": "Impossible date", "cost": 7, "cur": "CAD", "rc": ["k2"]}],
    "lodging": {"stays": [], "leave": [{"id": 'l"><img src=x onerror="' + X + '">', "city": "Leave town", "checkin": "2026-11-03", "checkout": "2026-11-04"}]},
    "sd": {"juris": "XX"}, "marking": "<script>", "fileNo": 7209},
    "receipts": {
        "k1": {"name": "ok.png", "kind": "img", "dataUrl": PNG, "pages": 1},
        "k2": {"name": "evil.png", "kind": "img", "dataUrl": 'x" onerror="' + X, "pages": "2<img src=x onerror=" + X + ">"},
        'bad"id': {"name": "x", "kind": "img", "dataUrl": PNG}}}
(fx / "hostile.json").write_text(json.dumps(hostile))
(fx / "junk.json").write_text(json.dumps({"app": "caf-digital-travel-itinerary", "state": {"stops": "nope", "member": [], "transport": [None, 5, "x"], "lodging": {"stays": [None]}}, "receipts": []}))

async def main():
    fails = []
    def check(name, ok):
        print(("ok  " if ok else "FAIL"), name)
        if not ok: fails.append(name)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1320, "height": 900})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(url); await pg.wait_for_timeout(700)
        await pg.set_input_files("#file-draft", str(fx / "hostile.json")); await pg.wait_for_timeout(900)
        await pg.focus("#m-sur"); await pg.keyboard.press("Tab"); await pg.wait_for_timeout(300)
        check("hostile draft opened", "Opened draft" in await pg.inner_text("#toast"))
        check("no injected code ran", (await pg.evaluate("window.__pwned || 0")) == 0)
        check("no injected elements", (await pg.evaluate("document.querySelectorAll('img[src=x]').length")) == 0)
        check("good receipt kept", (await pg.evaluate("document.querySelectorAll('#rows-transport .chip').length")) == 1)
        check("surname kept", await pg.input_value("#m-sur") == "Tester")
        check("number in a text field becomes text", await pg.input_value("#m-given") == "42")
        check("desc shown as text", "Taxi <b>bold</b>" in await pg.evaluate("[...document.querySelectorAll('#rows-transport input')].map(i => i.value).join('|')"))
        tots = await pg.inner_text("#tots")
        check("1,234.50 counts as 1234.50 (total 1241.50 with the 7)", "1241.50" in tots.replace(",", ""))
        checks = await pg.inner_text("#checks")
        check("impossible date 2026-02-30 treated as no date", "C-2 has no date" in checks)
        check("unknown jurisdiction cleared (no crash)", not errs)
        # junk draft: nothing crashes
        await pg.set_input_files("#file-draft", str(fx / "junk.json")); await pg.wait_for_timeout(900)
        check("junk draft opens without errors", not errs)
        await b.close()
    # amounts as typed, read by the app's own num() (taken from app/app.html and run in Node)
    import re, subprocess
    src = (base / "app/app.html").read_text(); m = re.search(r"\nconst num = v => \{.*?\n\};", src, re.S)
    cases = {"12": 12, "12.5": 12.5, "12,50": 12.5, "1,234": 1234, "1,234.56": 1234.56, "1 234,56": 1234.56, "1.234,56": 1234.56,
             "12.500": 12.5, "$ 45.00": 45, "-3.10": -3.1, "12abc": None, "1.2.3": None, "": None}
    js = m.group(0) + "\nconsole.log(JSON.stringify(" + json.dumps(list(cases)) + ".map(v => { const n = num(v); return isNaN(n) ? null : n; })))"
    got = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
    for (v, want), g in zip(cases.items(), got): check(f"amount {v!r} reads as {want}", g == want)
    print("errors:", errs); print("failures:", fails)
asyncio.run(main())
