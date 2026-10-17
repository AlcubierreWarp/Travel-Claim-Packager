---
name: "caf-digital-tool-builder"
description: "Use when Tom wants to build or improve a small browser-only digital tool for CAF/DND members (forms, claim packagers, calculators, checklists), new or existing."
---

# Building CAF digital tools with Tom

Tom (LCol, CAF) builds small tools that save CAF members admin time. These principles come from building the CAF Digital Travel Itinerary together. Apply them to any new tool unless he says otherwise.

## Working with Tom
- Direct analysis, no hedging. Final text has no em dashes and no "It's not X, it's Y" reversals.
- If he says "before doing any coding", answer the question or give options only; build nothing.
- State platform limits plainly (e.g. a mailto link cannot attach files; iOS installed apps cannot download) and offer the best workaround.
- Start work in the first reply when the request is clear. Ask only when the answer changes what gets built.
- Finish with a short summary: what changed, the version label, anything he must do on his phone. Do not recap steps.
- Changes go to beta by default. Promote to production only when he says "push to production".

## Non-negotiables
1. **Local only.** Nothing the member types or attaches leaves the browser. Page CSP: `default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; ...`. The hosted build may add only `'self'` for img, worker and manifest. No analytics, no external fonts in the offline copy, no CDNs at runtime (inline pinned libraries).
2. **No real personal data** in examples, tests, fixtures or screenshots. Use a generic fictional member (e.g. Capt Jordan Lee Sample) and generated dummy receipts. If Tom uploads a real form, use it for structure only and delete copies.
3. **Storage is opt-in.** Default: current tab only (sessionStorage). Optional "Keep my work on this device" (IndexedDB), optional PIN (AES-GCM, PBKDF2-SHA256 250k), auto-delete after a set period. Always offer draft file export/import (JSON) to move work between devices.
4. **No PRI or service number in file names.** File names travel through email subjects and search results.

## Deliverables
- One self-contained HTML app (all script, styles and libraries inline). When inlining pdf-lib, escape U+FFFD or artifact publishing is refused.
- Hosted build for GitHub Pages: manifest, icons, network-first service worker.
  - Navigations are fetched with `cache: 'no-cache'` (GitHub Pages sets max-age=600).
  - Cache names are per scope so beta and production do not wipe each other.
- Offline single-file copy in the repo.
- Optional claude.ai artifact copy with the downloads capability.
- **Production** at the repo root, **beta** at `/beta/`. They share an origin, so give each its own IndexedDB name and cache.
- Keep the source, build script, tests and version files on a `source` branch (not published). Never leave source only in a scratchpad.

## Versioning and release
- Production shows `Version X.Y, updated DD Mon YYYY`. The minor number goes up only on promotion. Tom decides major bumps.
- Beta shows `Version X.(Y+1) beta N, built DD Mon YYYY HH:MM (production is X.Y)`. N goes up on every beta publish and resets to 1 after a promotion.
- The label appears in the footer, the menu and help/feedback emails. Record the version in saved files and PDF metadata.
- Keep a CHANGELOG.md with "in progress" for the beta and a dated entry per release.
- Release script steps:
  1. Build.
  2. Run the channel check: no beta markers in production, production icon in colour.
  3. Copy the build and commit with the attribution lines from the system reminder.
  4. Push and confirm the remote matches HEAD.
  5. Snapshot the source branch.
  6. On promotion only: create a `release-vX.Y` branch (tag pushes are blocked by the proxy) and republish the artifact.
- **Beta-only layer** (beta.css, `data-channel="beta"`, grey icons, "Beta" app name, grey theme): use it only when Tom asks for something "beta-specific", meaning tools or visuals that make testing and telling the beta apart easier. Everything else goes in the main app. Confirm with him if unclear.

## CAF conventions
- **Ranks:** dropdowns with Civilian first, then Army/RCAF, then Navy, using current RCN ranks (S3, S2, S1; the canada.ca list is out of date). No abbreviations in legal text.
- **Dates:** show "Mon 02 Nov 26" in the UI and PDF. Use YYYYMMDD in file names. Use "N/A", not "n/a".
- **File names:** `Date_FileNo_Marking_Details`, e.g. `20261102_7209-1_PA_TD-Claim_Trip-Name_Capt-Sample.pdf`. The file number is optional (DSCDS, e.g. 7209-1 Transportation and Travelling Expenses). Marking options are UNCLAS, PA (default), PB or none. Apply the pattern to every output.
- **Marking on PDFs:** print the security marking top right on every page of generated PDFs, receipts included.
- **Statutory declarations:** follow DAOD 7000-1 structure (venue heading, declarant, DO SOLEMNLY DECLARE, numbered paragraphs, Canada Evidence Act closing) with per-province jurats.
- **Signatures:** offer PKI signature fields (default) or hand signature and date lines. Browser PKI signing is not realistic; signing stays in Adobe.

## Phone and iPhone lessons
- Inputs are 16px on touch screens (stops iOS focus zoom). Use `touch-action: manipulation`. Date inputs need an iOS-only appearance fix.
- Installed iOS apps ignore download links. Save through the share sheet (Save to Files), share files only (iOS saves any text as a second file), and no auto-save after async work (the share sheet needs a fresh tap). Show a single "Save or send" button there.
- Android Chrome will not share .json; fall back to a .txt copy and accept both on import.
- Do not use `capture` on file inputs; let the phone offer Camera, Photos or Files.
- mailto bodies use CRLF (`%0D%0A`) line breaks and numbered prompts (Gmail on iOS flattens bare LF).
- Pull to refresh in standalone mode needs its own implementation:
  - Save state, cap the wait, then `location.reload()`.
  - Never await `registration.update()`.
  - Toast "Updated to" or "Already up to date".
- Sideways swipes need `touch-action: pan-y`. Always keep a visible button too (X), with Undo and a way to restore the item from the menu.
- Help and Send feedback buttons open prefilled mailto emails with device, browser and version, plus a note not to include the PRI or receipts.

## Testing (Playwright, Chromium preinstalled)
- Test desktop, iPhone 13 and Pixel 7 emulation, in light and dark.
- Assert zero page errors and zero external requests every run.
- Stub `navigator.share`, `canShare` and `navigator.standalone` to test the share and installed-app paths.
- Test the service worker on `localhost` (not 127.0.0.1) with a server sending `Cache-Control: max-age=600`.
- Before promoting a storage or service-worker change, test the upgrade path: old production with kept data, then the new build.
- Look at screenshots of anything visual before publishing. Delete test fixtures afterwards.