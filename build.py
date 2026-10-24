import sys, re, pathlib
base = pathlib.Path(sys.argv[1])
src = (base / "app/app.html").read_text()
src = src.replace("/*I18N_FR*/", (base / "app/fr.js").read_text().strip())  # French text, see app/fr.js
src = src.replace("/*ITIN*/", (base / "app/itin.js").read_text().strip())  # itinerary reader, see app/itin.js
# Policy of the offline single file: no network access at all. The app also uses it for "Download offline copy".
OFFLINE_CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
       "img-src data: blob:; font-src 'none'; connect-src 'none'; media-src 'none'; "
       "object-src 'none'; frame-src 'none'; worker-src 'none'; base-uri 'none'; form-action 'none'")
src = src.replace("__OFFLINE_CSP__", OFFLINE_CSP)
# Versions: production shows VERSION; beta shows the next minor and its own build number (BETA_BUILD),
# which release.py raises on every beta publish and resets when the beta is promoted.
import datetime, zoneinfo
VERSION = (base / "VERSION").read_text().strip()
_maj, _min = VERSION.split(".")
BETA_VERSION = f"{_maj}.{int(_min) + 1}"
BETA_BUILD = int((base / "BETA_BUILD").read_text().strip() or 0)
_now = datetime.datetime.now(zoneinfo.ZoneInfo("America/Moncton"))
PROD_LABEL = f"Version {VERSION}, updated {_now.strftime('%d %b %Y')}"
BETA_LABEL = f"Version {BETA_VERSION} beta {BETA_BUILD}, built {_now.strftime('%d %b %Y %H:%M')} (production is {VERSION})"
src_beta = src.replace("__APP_VERSION__", f"{BETA_VERSION}-beta.{BETA_BUILD}").replace("__APP_LABEL__", BETA_LABEL).replace("__APP_CHANNEL__", "beta")
# Header logo: the app icon, inlined (the page may not load files). Greyscale in the beta, like its icons.
import base64, io
from PIL import Image as _Img
def _logo(grey):
    im = _Img.open(base / "pwa/icons/icon-192.png").convert("RGBA").resize((96, 96), _Img.LANCZOS)
    if grey: im = _Img.merge("RGBA", (*[im.convert("L")] * 3, im.split()[3]))
    b = io.BytesIO(); im.save(b, format="PNG", optimize=True); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
src_beta = src_beta.replace("__LOGO__", _logo(True))
src = src.replace("__LOGO__", _logo(False))
# Beta-only code and markup (between BETA-ONLY markers) never reaches production or its offline copy
src = re.sub(r"/\*BETA-ONLY\*/.*?/\*/BETA-ONLY\*/", "", src, flags=re.S)
src = re.sub(r"<!--BETA-ONLY-->.*?<!--/BETA-ONLY-->", "", src, flags=re.S)
src = src.replace("__APP_VERSION__", VERSION).replace("__APP_LABEL__", PROD_LABEL).replace("__APP_CHANNEL__", "production")
pdflib = (base / "npm/node_modules/pdf-lib/dist/pdf-lib.min.js").read_text().replace("\ufffd", "\\ufffd")
assert "</script" not in pdflib.lower()
# pdf.js (Apache-2.0) reads itinerary PDFs. It is stored as inert text and only run on first import.
pdfjs = {k: (base / f"npm/node_modules/pdfjs-dist/build/{f}").read_text() for k, f in (("/*PDFJS*/", "pdf.min.js"), ("/*PDFJSW*/", "pdf.worker.min.js"))}
for v in pdfjs.values(): assert "</script" not in v.lower() and "<!--" not in v and "\ufffd" not in v
def libs(t):
    t = t.replace("/*PDFLIB*/", "\n" + pdflib + "\n")
    for k, v in pdfjs.items(): t = t.replace(k, v)
    return t
inl = libs(src)

# Artifact version: page content only (the host adds the document skeleton)
(base / "out").mkdir(exist_ok=True)
(base / "out/travel-claim-packager.html").write_text(inl.replace("__OFFLINE_SHA__", ""))

# Standalone version: full document, no web fonts, strict policy that blocks all network access
head, body = inl.split("<!--BODY-->", 1)
head = re.sub(r"<!--FONTS-->.*?<!--/FONTS-->", "", head, flags=re.S)
csp = OFFLINE_CSP
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n'
       '<!-- CAF Digital Travel Itinerary. Runs entirely in the browser. This page cannot make network requests. -->\n'
       + head + "</head>\n<body>\n" + body + "\n</body>\n</html>\n")
doc = doc.replace("__OFFLINE_SHA__", "")
(base / "out/CAF_Digital_Travel_Itinerary.html").write_text(doc)
import hashlib
sha_prod = hashlib.sha256(doc.encode()).hexdigest()
print("ok", len(inl), len(doc), "sha256", sha_prod[:12])

# Hosted web build (GitHub Pages or a unit server): same page, installable as an app.
# The policy differs from the single file only in letting the page load its own manifest, icons and
# offline helper, and read its own published offline file, from the same site. Nothing outside the site.
import hashlib, shutil
web = base / "out/web"; web.mkdir(parents=True, exist_ok=True)
csp_web = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
           "img-src 'self' data: blob:; font-src 'none'; connect-src 'self'; media-src 'none'; "
           "object-src 'none'; frame-src 'none'; worker-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'")
pwa_head = ('<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="favicon.ico" sizes="any">\n'
            '<link rel="icon" href="favicon-32x32.png" type="image/png" sizes="32x32">\n'
            '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<meta name="theme-color" content="#052748">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-title" content="CAF Travel">\n')
webdoc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
          '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
          f'<meta http-equiv="Content-Security-Policy" content="{csp_web}">\n' + pwa_head +
          '<!-- CAF Digital Travel Itinerary. Runs entirely in the browser. The page itself cannot make network requests. -->\n'
          + head + "</head>\n<body>\n" + body + "\n</body>\n</html>\n").replace("__OFFLINE_SHA__", sha_prod)
(web / "index.html").write_text(webdoc)
# the published offline file sits next to the page, so Download offline copy hands over these exact bytes
shutil.copy(base / "out/CAF_Digital_Travel_Itinerary.html", web / "CAF_Digital_Travel_Itinerary.html")
ver = hashlib.sha256(webdoc.encode()).hexdigest()[:10]
(web / "sw.js").write_text((base / "pwa/sw.js").read_text().replace("__VERSION__", ver))
shutil.copy(base / "pwa/manifest.webmanifest", web / "manifest.webmanifest")
for f in (base / "pwa/icons").iterdir(): shutil.copy(f, web / f.name)  # owner-supplied icon set
print("web ok", ver)

# Beta channel: same page with the next version number and its own app name, so an installed
# beta is easy to tell apart from production on a home screen.
import json
webb = base / "out/web-beta"; shutil.rmtree(webb, ignore_errors=True); shutil.copytree(web, webb)
binl = libs(src_beta)
bhead, bbody = binl.split("<!--BODY-->", 1)
bhead = re.sub(r"<!--FONTS-->.*?<!--/FONTS-->", "", bhead, flags=re.S)
beta_css = (base / "pwa/beta.css").read_text()
bhead = bhead + '<style id="beta-only">\n' + beta_css + '\n</style>\n'
# beta offline file: the beta page with the strict no-network policy, like the production one
bsingle = ('<!doctype html>\n<html lang="en" data-channel="beta">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           f'<meta http-equiv="Content-Security-Policy" content="{OFFLINE_CSP}">\n'
           '<!-- CAF Digital Travel Itinerary (beta). Runs entirely in the browser. This page cannot make network requests. -->\n'
           + bhead + "</head>\n<body>\n" + bbody + "\n</body>\n</html>\n").replace("__OFFLINE_SHA__", "")
(webb / "CAF_Digital_Travel_Itinerary.html").write_text(bsingle)
sha_beta = hashlib.sha256(bsingle.encode()).hexdigest()
bdoc = ('<!doctype html>\n<html lang="en" data-channel="beta">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f'<meta http-equiv="Content-Security-Policy" content="{csp_web}">\n' + pwa_head.replace('content="CAF Travel"', 'content="CAF Travel Beta"').replace('content="#052748"', 'content="#2b2b2b"') +
        '<!-- CAF Digital Travel Itinerary (beta). Runs entirely in the browser. The page itself cannot make network requests. -->\n'
        + bhead + "</head>\n<body>\n" + bbody + "\n</body>\n</html>\n").replace("__OFFLINE_SHA__", sha_beta)
(webb / "index.html").write_text(bdoc)
bver = hashlib.sha256(bdoc.encode()).hexdigest()[:10]
(webb / "sw.js").write_text((base / "pwa/sw.js").read_text().replace("__VERSION__", bver))
# Beta icons in greyscale so the beta is easy to tell apart on a home screen
from PIL import Image
for f in (base / "pwa/icons").iterdir():
    im = Image.open(f).convert("RGBA"); r, g, b, a = im.split()
    grey = Image.merge("RGBA", (*[im.convert("L")] * 3, a))
    if f.suffix == ".ico": grey.save(webb / f.name, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    else: grey.save(webb / f.name, format="PNG", optimize=True)
m = json.loads((base / "pwa/manifest.webmanifest").read_text())
m["name"] = "CAF Digital Travel Itinerary (Beta)"; m["short_name"] = "CAF Travel Beta"
m["theme_color"] = m["background_color"] = "#2b2b2b"
(webb / "manifest.webmanifest").write_text(json.dumps(m, indent=2) + "\n")
(base / "out/checksums.json").write_text(json.dumps({"production": {"label": PROD_LABEL, "sha256": sha_prod}, "beta": {"label": BETA_LABEL, "sha256": sha_beta}}, indent=2) + "\n")
print("beta ok |", PROD_LABEL, "|", BETA_LABEL, "|", bver)
