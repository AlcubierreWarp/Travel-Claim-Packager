# CAF Digital Travel Itinerary: source

This branch holds the source, build tools and tests. GitHub Pages publishes `main` (the built site), not this branch.

- `app/app.html`: the whole app. Edit this. All text is written in English and passed through `T()`.
- `app/fr.js`: French text (Government of Canada usage), keyed by the English. Every new or changed English string needs an entry here; `test_fr.py` fails on any untranslated string.
- `pwa/`: manifest, offline helper (`sw.js`), icons, and `beta.css` (beta-only styles, never in production).
- Beta-only rule: only changes the owner asks for as "beta-specific" (tools or visuals that make testing and telling the beta apart easier) go in the beta-only layer. Everything else goes in `app/app.html` and reaches production when the beta is promoted. If unclear, confirm with the owner.
- `build.py`: builds `out/web` (production), `out/web-beta` (beta), the single-file copy and the claude.ai copy. Production shows `VERSION`; the beta shows the next minor plus `BETA_BUILD`.
- `release.py beta "message"`: next beta build to `/beta/`. `release.py promote`: beta becomes production. Both check that nothing beta-only reaches production, then save this branch.
- `test*.py`: Playwright tests (`python3 test_beta.py .` etc.).
- pdf-lib 1.17.1 (MIT) is in `npm/node_modules/pdf-lib/dist/`.
- `app/itin.js`: itinerary reader (Amex GBT layout). Pure functions, text lines in, segments and stops out; `test_itin.py` checks it with fictional itineraries built on the fly. Never commit a real itinerary.
- pdf.js 3.11.174 (Apache-2.0) is in `npm/node_modules/pdfjs-dist/build/` (`pdf.min.js`, `pdf.worker.min.js`). build.py stores both in the page as inert text; the app runs them on first import, on the page, with no worker.

To rebuild elsewhere: clone this branch, `pip install playwright pillow pypdf`, then `python3 build.py .`.

## Legal wording

Some statutory declaration sentences (English and French) were drafted for the tool rather than taken from DAOD 7000-1 or the Canada Evidence Act. They are listed, with their basis, in the doc "Statutory Declaration Wording for AJAG Review" (https://claude.ai/artifact/BqVDd7XQjyfp5DYipR8sgQ), pending AJAG review. Update that doc whenever `sdParagraphs`, `sdParagraphsFr`, `drawDeclaration` or the jurat tables change, and apply any AJAG changes in both languages.
