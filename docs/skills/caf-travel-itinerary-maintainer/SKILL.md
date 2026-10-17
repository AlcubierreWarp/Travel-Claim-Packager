---
name: "caf-travel-itinerary-maintainer"
description: "Use when Tom asks to change, fix, release or push the CAF Digital Travel Itinerary (Travel-Claim-Packager) beta or production, or says 'push to production'."
---

# Maintaining the CAF Digital Travel Itinerary

A browser-only tool: CAF members enter a TD itinerary, lodging, meals and expenses, attach receipts, and get one PDF package for the Orderly Room. Follow the caf-digital-tool-builder skill for principles. This skill covers the specifics of this app.

## Where things are
- **Repo:** `AlcubierreWarp/Travel-Claim-Packager` (GitHub Pages).
  - `main`: the published site. Production is at the root, beta at `/beta/`.
  - `source`: app source, build and release scripts, tests, `VERSION`, `BETA_BUILD`. Read `SOURCE.md` there first.
  - `release-vX.Y` and `prod-v1.0-final`: restore points.
- **Artifact copy:** https://claude.ai/artifact/4UWaqjKN31YZgLJN9t3s82. Republish it from `out/travel-claim-packager.html` on every promotion, with a `Version X.Y` label.
- **Legal wording for AJAG review:** `docs/legal-wording-for-ajag-review.md` on the source branch (master copy; the claude.ai doc https://claude.ai/artifact/BqVDd7XQjyfp5DYipR8sgQ mirrors it). Update it whenever declaration wording changes.
- **Contacts:** help and feedback emails go to Thomas.Huet@forces.gc.ca. The footer reads "(c) 2026 Thomas Huet". Tom built the tool on his own time and equipment.

## Starting over from nothing
If the Claude account or workspace is gone, follow `REBUILD.md` on the `source` branch. It covers the GitHub Pages setup, local tools, folder layout, building, testing, releasing and restoring a release. Copies of this skill and caf-digital-tool-builder are in `docs/skills/`.

## Resuming in a new session
1. Attach the repo (add_repo with push access) and clone it to `/home/claude/travel-claim-packager`. Other locations work if you set `TCP_REPO` and `TCP_SOURCE` (see `REBUILD.md`).
2. In the clone, add the source branch as a worktree: `git worktree add /home/claude/tcp-source source`.
3. Copy the source branch contents into a separate working folder (the scratchpad). `release.py` treats its own folder as the source and syncs it to `/home/claude/tcp-source`, so the two must differ. Check the paths at the top of `release.py`.
4. Run `pip install --break-system-packages playwright pillow pypdf` if missing. Then `python3 build.py .`.
5. Run the tests: `python3 test_beta.py .`, plus test_send, test_ios, test_names, test_notice, test_rail, test_ptr, test_fr, test_fr_more, test_modal and test_itin as relevant. Expect `errors: []`, `external requests: []` and `failures: []`. For service worker or storage changes also run `python3 test_live.py .` (local servers, upgrade check). Delete the `fixtures/` and `shots/` folders afterwards.

## Making a change
1. Edit `app/app.html`. Every new English string needs an entry in `app/fr.js` (test_fr fails otherwise). Put a change in `pwa/beta.css` (beta only) only if Tom calls it "beta-specific".
2. Build, test, and look at screenshots for visual changes.
3. Add a line under the "in progress" beta heading in `CHANGELOG.md` (in the repo clone).
4. Publish with `python3 release.py beta "Beta X.Y build N: summary"`. It bumps BETA_BUILD, runs the channel check, commits, pushes and saves the source branch.
5. Confirm the push: `git rev-parse HEAD` must equal `git ls-remote origin main` (release.py also prints a WARNING when a push fails).
6. Tell Tom the new label (e.g. 1.4 beta 5). He refreshes the installed beta app with pull to refresh.

## Push to production
1. Run all tests.
2. In the changelog, date the beta entry and add a new "in progress" heading for the next minor.
3. Run `python3 release.py promote`. It bumps VERSION, resets BETA_BUILD to 1, copies the production build, single file and beta, then pushes. It also creates `release-vX.Y` and saves the source branch.
4. Republish the artifact.
5. If declaration wording changed, update `docs/legal-wording-for-ajag-review.md` and the claude.ai doc.
6. Tell Tom what is in the release. Installed apps update on their next online open.

## Current beta-specific differences (keep unless Tom says otherwise)
- Greyscale icons, favicon and header logo (build.py inlines the logo; production's is in colour on a navy and blue theme).
- Grey launch and theme colour (#2b2b2b).
- "CAF Travel Beta" app name.
- Beta build label.
- `data-channel="beta"` marker.
- `pwa/beta.css`: violet colour theme (light and dark) in place of production's green, overriding the same `:root` tokens. Status colours (ok, warn, bad) are unchanged.
- `pwa/beta.css`: a Beta pill after the page title (Bêta in French), matching the import button's tag.
- Menu bottom (Beta testing, beta only): Load test data and Reset the beta, as code between `/*BETA-ONLY*/` and `<!--BETA-ONLY-->` markers that build.py strips from production. Put any future beta-specific script or markup inside those markers.

## Itinerary import (Amex GBT)
- Reader in `app/itin.js` (pure functions, inlined by build.py). pdf.js 3.11.174 is stored in the page as inert text and run on first import, no worker, no network.
- Fills section B, TAN and trip locator (shown only after an import), optional fare row, hotel stays, and the member's name (replacing an existing name only when ticked).
- Labelled Beta for users in both channels until Tom says otherwise.
- Never keep a real itinerary in the workspace or repo after use; tests build fictional ones.

## Statutory declarations
- Paragraphs come from `sdParts()`: 1 and 2 built (`sdParagraphs`/`sdParagraphsFr`) unless the member rewrote them (`sdP1`/`sdP2`, with the built text they replaced in `sdB1`/`sdB2` to flag later changes), an optional `sdMore` paragraph, then the reason and the two standard paragraphs (locked).
- Each editable paragraph is one paragraph (line breaks joined, typed numbers dropped), capped at 400 characters; the reason is capped at 200. `drawDeclaration` shrinks the paragraph text (to 7.5 pt at most) so the declaration stays on one page; `test_sdx.py` checks the longest case in both languages.

## Gotchas
- Production and beta share an origin.
  - IndexedDB: `caf-dti-main` for production, `caf-dti` for beta.
  - Caches are named per scope.
  - localStorage is shared, so the beta suffixes its preference keys with `-beta` (`CH` in app.html: first-run seen, notice hidden, language, which falls back to production's). Reset the beta clears only those. Any new localStorage key must use `+ CH`.
- The installed iOS app keeps its home screen icon and storage. Reinstalling deletes kept claims, so tell Tom to save a draft file first.
- `test_beta.py` reads the production IndexedDB name (`caf-dti-main`).
- Do not pkill patterns that match your own shell. Kill test servers by PID.