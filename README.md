# Travel Claim Packager

A single-page tool that helps CAF members prepare a temporary duty travel claim. It is built around the JMC Travel Itinerary Worksheet.

Enter the itinerary, lodging, meals and expenses, attach receipt photos or PDFs, and the tool builds one PDF for the Orderly Room. The PDF contains the worksheet in form order, totals by currency, a receipt index, every receipt labelled with its reference, and a DAOD 7000-1 statutory declaration for any receipt marked lost. Signature fields can be signed with a PKI certificate in Adobe Acrobat.

## Privacy

Everything runs in the browser. The page has no server component, makes no network requests (a Content Security Policy in the page blocks them), and stores nothing outside the open browser tab. Use **Save draft** to keep work in progress as a file on your own device.

## Use

Open the published page, or download `index.html` and open it in a browser. The page opens with a fictional example claim; choose **Start a blank claim** to begin your own.

## Status

Prototype for testing and feedback. It is not an official DND/CAF application and does not calculate entitlements. Check all claims against current CFTDTI and Orderly Room direction.

## Third-party code

pdf-lib (MIT License) is bundled inside `index.html`. See `THIRD_PARTY_NOTICES.md`.
