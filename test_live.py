# Service worker tests against local servers that cache like GitHub Pages (max-age=600).
# python test_live.py .   Stages the built sites under live/, starts the servers, runs the four tests, stops the servers.
# test_upgrade starts from the live production site in TCP_REPO (the main branch clone) and upgrades it to out/web.
import sys, os, subprocess, shutil, pathlib, time
base = pathlib.Path(sys.argv[1]).resolve(); live = base / "live"; shutil.rmtree(live, ignore_errors=True)
repo = pathlib.Path(os.environ.get("TCP_REPO", "/home/claude/travel-claim-packager"))
def site(dst, prod):
    shutil.copytree(prod, dst, ignore=shutil.ignore_patterns(".git", "beta", "*.md", "CAF_Digital_Travel_Itinerary.html"))
    shutil.copytree(base / "out/web-beta", dst / "beta")
site(live / "s1/Travel-Claim-Packager", base / "out/web")   # test_channels, port 8765
site(live / "s2", base / "out/web")                         # test_offline and test_ptr_live, port 8766
site(live / "s3/Travel-Claim-Packager", repo)               # test_upgrade, port 8767
procs = [subprocess.Popen([sys.executable, str(base / "serve_cached.py"), str(live / d), str(port)]) for d, port in (("s1", 8765), ("s2", 8766), ("s3", 8767))]
time.sleep(1)
try:
    for t in ("test_channels.py", "test_offline.py", "test_ptr_live.py", "test_upgrade.py"):
        print("===", t, flush=True)
        r = subprocess.run([sys.executable, str(base / t), str(base)], cwd=base, capture_output=True, text=True, timeout=240)
        print(r.stdout.strip()); r.returncode and print("FAILED:", r.stderr.strip()[-1500:])
finally:
    for p in procs: p.terminate()
    shutil.rmtree(live, ignore_errors=True)
