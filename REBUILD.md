# Rebuilding the CAF Digital Travel Itinerary from scratch

This guide assumes nothing survives except this GitHub repository: no Claude account, no Claude skills or memory, no earlier workspace. Everything needed to rebuild, test, publish and keep developing the app is in the repository.

## 1. What is in the repository

| Branch | What it holds |
| --- | --- |
| `main` | The published site (GitHub Pages). Production at the root, beta in `beta/`, the offline single file, `CHANGELOG.md`, `README.md`, `THIRD_PARTY_NOTICES.md`. |
| `source` | Everything needed to build `main`: app source, French text, itinerary reader, libraries, icons, build and release scripts, tests, version files, and the documents in `docs/`. |
| `release-vX.Y` | A copy of `main` as it was when version X.Y went to production. Use these to roll back. |
| `prod-v1.0-final` | The last 1.0 production site. |

On the `source` branch:

| Path | Purpose |
| --- | --- |
| `app/app.html` | The whole app: markup, styles and script. Edit this. All text is English, passed through `T()`. |
| `app/fr.js` | French text (Government of Canada usage), keyed by the English text. |
| `app/itin.js` | Amex GBT itinerary reader (pure functions). |
| `pwa/` | Manifest, offline helper `sw.js`, icons, `beta.css` (beta-only styles), `make_icons.py` and the icon artwork in `pwa/src/`. |
| `npm/node_modules/...` | Pinned copies of pdf-lib 1.17.1 (MIT) and pdf.js 3.11.174 (Apache-2.0), with their licences. |
| `build.py` | Builds production, beta, the offline single file and the claude.ai copy into `out/`. |
| `release.py` | Publishes a beta build, promotes beta to production, saves the source branch. |
| `msgfile.py` | Writes small fictional Outlook .msg files for `test_itin.py`. |
| `serve_cached.py` | Local web server that sends GitHub's caching header, for the service worker tests. |
| `test*.py` | Playwright tests. |
| `VERSION`, `BETA_BUILD` | Current production version and beta build number. |
| `SOURCE.md` | Short orientation to the source. |
| `docs/legal-wording-for-ajag-review.md` | Statutory declaration wording drafted for the tool, with its basis, for AJAG review. Master copy. |
| `docs/skills/` | The two Claude skills that hold the working method and the app's specifics (see section 9). |

## 2. Accounts and settings

- **GitHub:** the repository `AlcubierreWarp/Travel-Claim-Packager`. If it ever has to be recreated, push both branches (`main` and `source`) and the `release-v*` branches to the new repository.
- **GitHub Pages:** Settings, Pages, "Deploy from a branch", branch `main`, folder `/ (root)`. `main` contains `.nojekyll`, so the files are served as they are. No custom domain and no build action are used.
- **Contacts written into the app:** help and feedback emails go to Thomas.Huet@forces.gc.ca. The footer reads "© 2026 Thomas Huet". Change them in `app/app.html` if needed.

The app has no server, database or analytics. Members' claims live only in their own browsers, so there is no user data to back up or restore.

## 3. Tools on your computer

- Git.
- Python 3.11 or newer (the build uses `zoneinfo` with the America/Moncton time zone; on Windows also run `pip install tzdata`).
- Python packages: `pip install playwright pillow pypdf`
- A browser for the tests: `python -m playwright install chromium`
- `pdftoppm` (poppler) is optional, for looking at PDF pages as images.
- Node.js is only needed to update the bundled libraries (section 10).

## 4. Folder layout

`release.py` uses three folders. The defaults are the paths of the original workspace; set environment variables to use your own.

| Folder | Variable | Contents |
| --- | --- | --- |
| Working copy | (wherever `release.py` is) | A plain copy of the `source` branch. You edit and build here. |
| Site clone | `TCP_REPO` | A clone of the repository with `main` checked out. |
| Source worktree | `TCP_SOURCE` | A git worktree of the same clone with `source` checked out. |

Set up once:

```
git clone https://github.com/AlcubierreWarp/Travel-Claim-Packager.git site
cd site && git worktree add ../source-branch source && cd ..
mkdir work && cp -r source-branch/. work/ && rm -rf work/.git
export TCP_REPO="$PWD/site" TCP_SOURCE="$PWD/source-branch"
export TCP_TRAILER=""            # or your own commit trailer lines
```

On Windows PowerShell use `$env:TCP_REPO = "C:\path\site"` and so on. The working copy and the source worktree must be separate folders: `release.py` copies the working copy into the source worktree, commits it and pushes it.

## 5. Build

```
cd work
python build.py .
```

It writes:

- `out/web/` production site (copied to the root of `main` on promotion)
- `out/web-beta/` beta site (copied to `beta/` on `main`)
- `out/CAF_Digital_Travel_Itinerary.html` offline single file
- `out/travel-claim-packager.html` copy for a claude.ai artifact (optional)

A clean clone of `source` rebuilds the live site exactly, apart from the date stamps. This was last confirmed on 17 Oct 2026 for production 1.5 and beta 1.6 beta 3.

## 6. Test

Run from `work`:

```
python test_beta.py .
python test.py .
python test_send.py .
python test_ios.py .
python test_names.py .
python test_notice.py .
python test_rail.py .
python test_ptr.py .
python test_fr.py .
python test_fr_more.py .
python test_modal.py .
python test_itin.py .
python test_swipe_vis.py .
python test_offline_copy.py .
python test_fileno.py .
python test_pdfver.py .
python test_savenow.py .
python test_switch.py .
python test_sdx.py .
python test_split.py .
```

Each prints `errors: []`. Tests that check privacy also print `external requests: []`, and the newer ones print `failures: []`. `test_fr.py` also prints `missing: []` (no untranslated text). Delete the `fixtures/` and `shots/` folders afterwards.

The service worker tests (`test_channels.py`, `test_offline.py`, `test_ptr_live.py`, `test_upgrade.py`) need local web servers that cache like GitHub Pages. Run them together with:

```
python test_live.py .
```

It copies the built sites into `live/`, starts `serve_cached.py` on ports 8765 to 8767, runs the four tests and stops the servers. `test_upgrade.py` starts from the production site currently in `TCP_REPO` and upgrades it to your new build, checking that a member's saved claim survives. The tests use `localhost`, because service workers do not register on 127.0.0.1.

Never put real personal data in tests or fixtures. `test_itin.py` builds fictional itineraries every time it runs.

## 7. Release

Beta:

1. Edit `work/app/app.html`. Add a French entry to `work/app/fr.js` for every new English string.
2. Build, run the tests and look at screenshots of anything visual.
3. Add a line under the "in progress" heading of `site/CHANGELOG.md`.
4. `python release.py beta "Beta X.Y build N: what changed"`

   It raises `BETA_BUILD`, builds, checks that nothing beta-only reaches production, copies the beta into `site/beta/`, commits and pushes `main`, then saves the working copy to the `source` branch. It prints a WARNING if a push did not reach GitHub.

Production ("push to production"):

1. Run all the tests.
2. In `site/CHANGELOG.md`, date the beta heading and add a new "in progress" heading for the next version.
3. `python release.py promote`

   It raises the minor version in `VERSION`, resets `BETA_BUILD` to 1, copies production, the single file and the beta into `site`, pushes `main`, creates the restore branch `release-vX.Y` and saves the source branch.
4. Optional: publish `out/travel-claim-packager.html` as a claude.ai artifact. The original artifact link belongs to the old Claude account, so a new account gets a new link.

Version labels: production shows `Version X.Y, updated DD Mon YYYY`; the beta shows `Version X.(Y+1) beta N, built ... (production is X.Y)`. The minor number goes up only on promotion; the owner decides major versions.

## 8. Roll back production

To put version X.Y back on the live site:

```
cd site
git checkout main
git checkout release-vX.Y -- .
git commit -m "Roll back to X.Y"
git push origin main
```

Then set `work/VERSION` to X.Y and copy `app/`, `pwa/` and the other source files from the `source` branch history (`git log` on the source worktree shows a "Source snapshot: X.Y" commit for each release).

## 9. Working with Claude again

The working method lives in two skill files in `docs/skills/`:

- `caf-digital-tool-builder/SKILL.md`: principles for any small CAF tool (local only, no real personal data, file naming, security markings, bilingual text, phone lessons, testing, release discipline, Tom's writing preferences).
- `caf-travel-itinerary-maintainer/SKILL.md`: this app's specifics (repository layout, release steps, beta-only differences, the itinerary import, known pitfalls).

In a new Claude account, add both as skills, or attach them at the start of a conversation and ask Claude to follow them. Then give Claude access to this repository and point it at this file.

Owner rules worth repeating:

- Changes go to the beta. Production changes only when the owner says "push to production".
- Only changes the owner calls "beta-specific" go in the beta-only layer (`pwa/beta.css`, beta build settings in `build.py`). Today these are: greyscale icons and header logo, grey launch colour, the "CAF Travel Beta" name, the beta version label, the violet colour theme and the Beta pill after the page title.
- Statutory declaration wording that is not from an official source is listed in `docs/legal-wording-for-ajag-review.md`. Update it whenever that wording changes.

## 10. Updating the bundled libraries

```
npm pack pdf-lib@1.17.1 pdfjs-dist@3.11.174
```

Unpack each `.tgz` and copy `package/dist/pdf-lib.min.js`, `package/LICENSE.md`, `package/build/pdf.min.js`, `package/build/pdf.worker.min.js` and `package/LICENSE` into the matching `npm/node_modules/...` paths. `build.py` refuses a library that contains `</script`, `<!--` or the U+FFFD character, because the page inlines them. A new pdf.js version must still offer the global `pdfjsWorker` fake-worker path (the 3.x series does); test `test_itin.py` after any change.

## 11. Things that are not in the repository

- The claude.ai artifact copy of the app and the claude.ai doc of the legal wording. Both can be recreated from the repository (`out/travel-claim-packager.html` and `docs/legal-wording-for-ajag-review.md`).
- Claude conversation history and memory. Nothing in them is needed to rebuild.
- Real itineraries or receipts. They are never kept.
