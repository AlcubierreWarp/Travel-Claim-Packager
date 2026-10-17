# CAF Digital Travel Itinerary

A single-page tool that helps CAF members prepare a temporary duty travel claim.

Enter the trip itinerary, lodging, meals and expenses, attach receipt photos or PDFs, and the tool builds one PDF for the Orderly Room. The PDF contains the itinerary worksheet, totals by currency, a receipt index, every receipt labelled with its reference, and a DAOD 7000-1 statutory declaration for any receipt marked lost. Signature fields can be signed with a PKI certificate in Adobe Acrobat.

Leave taken during a trip can be recorded in the itinerary. Leave days stay on the trip record, but their meals are not claimed by default and no lodging is required for them.

## Privacy

Everything runs in the browser. The page has no server component and makes no network requests (a Content Security Policy in the page blocks them). Nothing you type or attach is uploaded.

By default a claim lasts only as long as the browser tab. In the menu you can choose **Keep my work on this device**, which stores the claim in this browser only, optionally encrypted with a PIN, and deletes it 30 days after the PDF is built. Use **Save draft file** to move a claim to another device.

## Use

- **Website:** open the published page. On a phone, use **Install app** in the menu (or Add to Home Screen on iPhone) to use it like an app, including offline.
- **Single file:** download `CAF_Digital_Travel_Itinerary.html` and open it in any browser. It works with no internet connection and cannot make network requests at all.

The page opens with a fictional example claim; choose **Start a blank claim** to begin your own.

## Beta

The next version is tested at `/beta/`. It keeps its own saved claims and offline copy, separate from the main site, and installs as **CAF Travel Beta**.

## Status

Unofficial prototype for testing and feedback. It is not an official DND/CAF application and does not calculate entitlements. Check all claims against current CFTDTI and Orderly Room direction.

## Versions

The version number is shown at the bottom of the page and in help emails. See `CHANGELOG.md`.

## Source and rebuilding

This branch (`main`) is the published site. The source, build and release scripts, tests and documentation are on the `source` branch. To rebuild or keep developing the app from nothing but this repository, follow `REBUILD.md` on that branch. Each production release also has a restore branch, `release-vX.Y`.

## Third-party code

pdf-lib (MIT License) and pdf.js (Apache License 2.0) are bundled inside `index.html` and `CAF_Digital_Travel_Itinerary.html`. See `THIRD_PARTY_NOTICES.md`.
