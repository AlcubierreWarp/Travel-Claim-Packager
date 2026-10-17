"""Publish the app.  python3 release.py beta "message"   -> next beta build to /beta/
                    python3 release.py promote            -> beta becomes production, beta resets
Run from the scratchpad. Tests are run separately before this."""
import sys, subprocess, shutil, pathlib, datetime, zoneinfo
S = pathlib.Path(__file__).parent; R = pathlib.Path("/home/claude/travel-claim-packager")
ATTR = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01JZskSQKPTttDoeBBcK7dyi"
def sh(*a, cwd=R): return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout
def build(): print(sh("python3", "build.py", ".", cwd=S).strip().splitlines()[-1])
def check():
    """Stop if anything beta-only reached production, or the beta lost its markers."""
    from PIL import Image
    prod = (S / "out/web/index.html").read_text(); beta = (S / "out/web-beta/index.html").read_text()
    single = (S / "out/CAF_Digital_Travel_Itinerary.html").read_text(); art = (S / "out/travel-claim-packager.html").read_text()
    for name, doc in (("production", prod), ("single file", single), ("artifact", art)):
        import re
        bad = [m for m in ('data-channel="beta"', 'id="beta-only"', "CAF Travel Beta", "APP_CHANNEL = 'beta'") if m in doc]
        if re.search(r"APP_VERSION = '[^']*beta", doc) or re.search(r"Version [0-9.]+ beta", doc): bad.append("beta version label")
        assert not bad, f"beta-only content in {name}: {bad}"
    assert "Beta" not in (S / "out/web/manifest.webmanifest").read_text(), "beta name in production manifest"
    im = Image.open(S / "out/web/icon-192.png").convert("RGB").resize((24, 24))
    assert max(max(p) - min(p) for p in zip(*[iter(im.tobytes())] * 3)) > 40, "production icon is not in colour"
    for m in ('data-channel="beta"', 'id="beta-only"', "APP_CHANNEL = 'beta'"):
        assert m in beta, f"beta build is missing {m}"
    print("channel check ok")
def copy_beta():
    shutil.rmtree(R / "beta", ignore_errors=True); shutil.copytree(S / "out/web-beta", R / "beta")
def push(msg):
    sh("git", "add", "-A"); sh("git", "commit", "-q", "-m", msg + ATTR)
    subprocess.run(["git", "push", "-q", "origin", "main"], cwd=R, capture_output=True)
    print(sh("git", "log", "--oneline", "-1").strip())
SRC = pathlib.Path("/home/claude/tcp-source")
KEEP = ["app/app.html", "app/fr.js", "build.py", "release.py", "VERSION", "BETA_BUILD", "pwa", "npm/node_modules/pdf-lib/dist/pdf-lib.min.js", "app/itin.js", "npm/node_modules/pdfjs-dist/build/pdf.min.js", "npm/node_modules/pdfjs-dist/build/pdf.worker.min.js", "npm/node_modules/pdfjs-dist/LICENSE", "SOURCE.md"] + sorted(p.name for p in S.glob("test*.py"))
def save_source():
    """Snapshot the source, build tools and tests to the 'source' branch (not published by GitHub Pages)."""
    if not SRC.exists():
        subprocess.run(["git", "worktree", "add", "-f", str(SRC), "source"], cwd=R, capture_output=True)
    for k in KEEP:
        src = S / k; dst = SRC / k
        if not src.exists(): continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir(): shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
        else: shutil.copy(src, dst)
    sh("git", "add", "-A", cwd=SRC)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=SRC).returncode:
        sh("git", "commit", "-q", "-m", "Source snapshot: " + (S / "VERSION").read_text().strip() + " / beta " + (S / "BETA_BUILD").read_text().strip() + ATTR, cwd=SRC)
    subprocess.run(["git", "push", "-q", "origin", "source"], cwd=SRC, capture_output=True)
    print("source saved:", sh("git", "log", "--oneline", "-1", cwd=SRC).strip())
mode = sys.argv[1]
if mode == "beta":
    n = int((S / "BETA_BUILD").read_text().strip() or 0) + 1; (S / "BETA_BUILD").write_text(f"{n}\n")
    build(); check(); copy_beta(); push(sys.argv[2] if len(sys.argv) > 2 else f"Beta build {n}"); save_source()
elif mode == "check":
    build(); check()
elif mode == "source":
    save_source()
elif mode == "promote":
    maj, mi = (S / "VERSION").read_text().strip().split("."); new = f"{maj}.{int(mi) + 1}"
    (S / "VERSION").write_text(new + "\n"); (S / "BETA_BUILD").write_text("1\n")
    build(); check()
    for f in (S / "out/web").iterdir(): shutil.copy(f, R / f.name)
    shutil.copy(S / "out/CAF_Digital_Travel_Itinerary.html", R / "CAF_Digital_Travel_Itinerary.html")
    shutil.copy(S / "out/CAF_Digital_Travel_Itinerary.html", "/home/claude/CAF_Digital_Travel_Itinerary.html")
    copy_beta(); push(f"Release {new} to production")
    sh("git", "branch", "-f", f"release-v{new}", "HEAD"); subprocess.run(["git", "push", "-q", "origin", f"release-v{new}"], cwd=R, capture_output=True)
    save_source()
    print("remember: republish the artifact from out/travel-claim-packager.html")
