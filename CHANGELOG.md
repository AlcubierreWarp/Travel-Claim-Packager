# Changelog

Versioning: the minor number goes up by one only when the beta is promoted to production (1.1, 1.2, 1.3...). The beta shows the number the next production release will have plus its own build number, which goes up with every beta publish and starts again at 1 after a promotion, for example "Version 1.3 beta 3, built 17 Oct 2026 10:42 (production is 1.2)". The major number changes only when the owner decides a release is a major one.

## 1.10 (beta, in progress)

## 1.9 (24 Oct 2026)

- Offline file SHA-256: `3dbc034ea8af90fbc138028b3f204cc50b1841cbe35e94f44526185d8962c5d5`
- Offline copy checksums: the menu shows the SHA-256 of this version's offline file under Download offline copy, and the README lists the checksums for production and the beta, with how to check a file on Windows, macOS and Linux. An offline copy links to that list instead
- Download offline copy now hands over the published offline file itself, so its checksum matches. Only when that file cannot be read (offline before it was saved, or inside an offline copy) is a copy built on the device, and the message says its checksum will not match
- The beta now has its own published offline file, at beta/CAF_Digital_Travel_Itinerary.html
- Fixed: opening the offline file from the website could replace the installed app's saved copy with that file
- Menu made more compact: each section opens with a tinted band, description lines are gone, labels are shorter (Keep my work, Local-only notice), Get help and Send feedback share a row, and Save now sits above Keep my work
- Menu regrouped by function: Claim file (New claim, Open claim file, Save claim file, Send claim file), On this device (Keep my work, Save now, Remember my details, PIN, Forget this device), Experimental, App (Download offline copy, local-only notice, switch channel) and Help. Install app stays at the top
- New Experimental section with on/off switches for Itinerary import (on by default; off hides the import card) and Beautify export (off by default). Import is now labelled Experimental instead of Beta
- On/off switches replace the small check boxes in the menu and for yes/no choices on the page, which are easier to tap on a phone. The meals grid keeps its check boxes
- A built PDF is withdrawn as soon as anything changes what it would hold (the claim, a receipt, Beautify export, separate files or signing, the language), with "Changed since the last build. Build again for an up-to-date PDF.", so Save or Open never hands over an out-of-date file
- Add stays from itinerary: each leave stop now gets a green leave card (place, dates, nights, "no lodging to claim") where it falls among the stays, with nothing to fill in. It can be removed (with Undo), is not added twice and is not in the PDF
- Click an uploaded receipt photo (anywhere but its x) to open the crop editor
- The travel mode "No travel (same location)" is now just "No travel", in the app and the PDF
- Beautify export: the journey is centred on the page, section titles are in the claim's language only, and the week grids drop the date range under each week and show the month on each day instead
- Beautify export: PDF receipts without a page background now show on a white sheet instead of the grey panel. In the meals grid, leave days are green and labelled, and meals not claimed are plain white cells. The first page's section table is now a plain "Sections" overview, and the journey uses travel icons (plane, car, train, bus) with one short line per place
- Beautify export (experimental, in the menu): builds the same package in a designed layout. A first page with the claim at a glance (claimant, total by section, sections in claim-form order with their pages, the journey by overnight places, what is left to do), sections with lettered tiles and French or English beside, every amount in one column, meals as a day grid or by week, nil sections as small cards, a page map on the index page, labelled receipt pages and a matching footer. Turned off, PDFs are unchanged
- Crop now guesses where the receipt is when it opens (a pale sheet on a darker surface, angled or partly out of frame) and places the corners there to check and adjust. When it cannot tell, for example white paper on a white counter, it starts from the whole photo as before. Reset goes back to the whole photo
- Receipt photos can be cropped on the device: drag the four corners to the receipt's edges (a magnifier helps on phones) and the photo is straightened to that shape, with Rotate and Reset. From the Add a receipt window, or later from an attached receipt's viewer, with Undo. No new library; the single file stays about 2.3 MB
- PDF header: the line under the title now gives the trip name, the trip's start and end dates, and the TAN and trip locator when there are any. The date prepared and the receipt counts are gone from it
- PDF: every subtotal and the grand total use the same layout down the page: the label, currency and amount line up with each other and with the currency and amount columns of the summary
- PDF tables: totals and subtotals stand out as a shaded band with a rule above and no cell lines, and the grand total has a double rule below. Ordinary rows are white again (every row had been shaded by mistake)
- With Remember my details on, the file number and security marking are kept as the defaults for new claims, and a note under them says so
- The trip name no longer has an explanation under it
- Itinerary import: the beta note now says import is still under development, that results may vary and should be checked for accuracy, and to report errors with Send feedback at the bottom of the page or in the menu

## 1.8 (17 Oct 2026)

- The Switch to beta / Switch to production item moves to the bottom of the menu, under Help and Send feedback
- Currency exchanges no longer get an "outside the trip" warning when dated up to 30 days before or after it
- Statutory declarations: the wording is now shown as numbered paragraphs, the way it prints. Paragraphs 1 and 2 can each be rewritten on their own (one paragraph each, up to 400 characters), one paragraph of facts can be added after them, and the reason and standard paragraphs are locked, with links to the expense to change the facts at the source. A rewritten paragraph is flagged when the claim changes later. Long wording no longer runs off the page
- Statutory declarations: the first click on See or edit the wording after typing in an expense now opens it
- Beta: Reset the beta now also brings back the example claim, the local-only notice and the other first-run prompts. The beta keeps these preferences separately from production, so dismissing something in one no longer hides it in the other
- Signing (PKI or Ink signature) moves under the output choice as the same kind of switch, with a one-line hint. The missing-receipt note on each expense now follows the choice right away
- Package output choice is now a compact One PDF / Separate PDFs switch with a one-line hint, on desktop and phone
- Beta: the violet theme is back in light mode (a comment in the beta styles had cut off the light-mode rule); a release check now guards against it
- Beta only (stays out of production): Load test data (a full test claim using every section and feature: point of contact, connections, a leave stop, rental car and other modes, all three kinds of lodging with rations, meal remarks, an exchange before the trip, business and personal calls, image and two-page PDF receipts, four missing receipts with one edited declaration, TAN, trip locator, file number and PROTECTED B; Undo is offered) and Reset the beta (clears the beta's saved claims, details, settings, PIN and offline copy on this device; production is untouched), at the bottom of the menu under Beta testing

- The app logo replaces the TD mark in the header (greyscale in the beta), and production is re-themed in navy and blue to match the logo, in light and dark mode. The beta keeps its violet theme
- Currency exchange: the place field now asks Where exchanged (bank or exchange office, city). Its statutory declaration fits when the exchange happened: before leaving on the duty, during it (with the duty location taken from the itinerary, not the bank), or after returning
- Statutory declarations: See or edit the wording under each declaration shows paragraphs 1 and 2 as they will print, and lets the member rewrite them; edited wording is printed as typed, marked Edited, and can be reset to the built wording
- Jurat date: filled in with today's date by default (for example "this 17th day of October A.D. 2026", "ce 17 jour d'octobre 2026"), editable in the form and still editable in the PDF, or cleared to leave it for the officer
- Package output: One PDF (as before) or Separate PDFs: the worksheet, the receipts, and each statutory declaration as its own file, named for what it is (for example _1-Worksheet, _2-Receipts, _3-SD-C-2), each with its own page numbers, marking and version. The worksheet's receipt index says which file and page each receipt is in. Save each file, or Save all (one share sheet on phones)

## 1.7 (17 Oct 2026)

- Switch to beta / Switch to production in the menu (This tool), to move between the two in the same window or installed app. The claim is saved first, and each version keeps its own claims (tab-only claims included). Production shows the switch only on a device that has opened the beta, so members do not see it

## 1.6 (17 Oct 2026)

- Save now: a Save button in the header (desktop), Save now at the top of the menu (all screens) and Ctrl+S / Cmd+S. It saves at once instead of waiting for the auto-save, reads the claim back to check it was stored, and says where it is kept: on this device (checked), or in this tab only until it closes (with a one-tap Keep on this device). If the browser refuses to store it, it says so and offers Export claim file
- The PDF package shows the app version in the footer of every page (for example "CAF Digital Travel Itinerary v1.6", or "v1.7 beta 2" from the beta) and records it in the file properties, so any package can be traced to the version that built it
- Import itinerary: when an itinerary arrives in several emails, add the others in the review step (Add another email or file, Paste another email, or drop them on the window). New legs are added and highlighted; legs, hotels, fares and attachments already listed are skipped, so adding the same email twice changes nothing
- Import itinerary reads Outlook .msg emails (saved or dragged from desktop Outlook): the PDF itinerary attached to the email when there is one, otherwise the message text. Pasting the whole email (select all, copy, paste) also works. Arrivals with a terminal after the airport code ("Toronto, Canada (YYZ), Terminal 1") are now read correctly
- File number defaults to 7209-1 (Transportation and Travelling Expenses) in every file name until the member changes it. A number cleared on purpose stays cleared; claim files and remembered details from before this change get the default
- Menu regrouped under This claim, This tool, This device and Help, with standard wording: New claim (was Clear form), Import claim file (was Open draft file), Export claim file (was Save draft file), Send claim file, and Export offline app. The two Export items each say in one line what the file contains
- Export offline app (menu): saves the whole app as one .html file (about 2.3 MB, named with the version) that opens with a double-click in any browser and runs with no internet connection. It is built on the device from the page as it loaded, so it never contains the claim in progress, and it uses the strict no-network policy of the offline single file. Works on desktop, Android and the installed iPhone app (through the share sheet)
- Beta only (stays out of production): violet colour theme in light and dark mode, so the beta is easy to tell apart from production's green
- Beta only (stays out of production): Beta badge after the page title, matching the import button's tag (Bêta in French)

## 1.5 (17 Oct 2026)

- Import itinerary moved to the top of the form, in its own card above the trip name
- TAN and trip locator, filled by the import and printed under the title of the package. They appear under the trip name only when an imported itinerary (or an opened draft) has them, in smaller fields
- Import can fill in the member's name (section A and the declarant's full name) from the itinerary. On a claim with a name already entered it is offered as a replacement and is off unless ticked; a blank claim fills it by default
- Open windows (Import itinerary, Add a receipt, receipt preview) hold the screen: the form behind no longer scrolls on iPhone, and closing returns to the same place

## 1.4 (17 Oct 2026)

- File names follow Date_FileNo_Marking_Details for the PDF package and the draft file, e.g. 20261102_7209-1_PA_TD-Claim_Winnipeg-Course_Capt-Sample.pdf
- Optional file number and a security marking (UNCLASSIFIED, PROTECTED A by default, PROTECTED B, or none) in the Package section; remembered with your details
- Security marking printed at the top right and bottom right of every page of the PDF (receipts included), larger than the body text, per DND guidance to mark the top and bottom of sensitive documents; page number moves to the centre; marking also set in the PDF properties
- French: Français / English button in the header (FR / EN on phones), remembered on the device and defaulting to the browser language. The whole interface, help and feedback emails, file names and the PDF package switch language, including the statutory declaration with the French DOAD 7000-1 wording and provincial jurats, French rank names, French dates and decimal commas, and PROTÉGÉ A / PROTÉGÉ B / NON CLASSIFIÉ markings
- Beta-only layer: beta.css and a beta marker are added to the beta build only; a release check stops any promotion that would carry beta-only content into production
- Source, build tools and tests saved to the source branch (not published)
- Import itinerary (section B): reads an Amex GBT itinerary (PDF, the email saved as .eml, or pasted text) on the device and fills section B with each flight, train, bus and rental car, its dates and times, connections, and hotel stays in another city. Optional: start and finish at your residence (on by default), add the fare and GBT service fee to transportation expenses with the itinerary as the receipt (off by default, for fares you paid yourself), add hotel stays to Lodging. Shows what it found and what section B will list before anything changes; Undo afterwards. Uses pdf.js 3.11.174 (Apache-2.0), stored in the page and run only on first import, with no worker and no network access
- Import itinerary is marked Beta for users (a badge on the button and dialog, and a note asking members to check every stop, date and time and to send feedback)

## 1.3 (17 Oct 2026)

- Section rail follows the page: on phones the horizontal rail slides along as you scroll so the current section stays in view; the current section is highlighted on all screens
- Local-only notice can be hidden with its X, or by swiping it sideways on touch screens (iPhone-style red Hide action with a bin icon underneath), with Undo; Show local-only notice in the menu brings it back
- + Receipt no longer forces the camera: phones offer Take Photo, Photo Library or Files; the desktop button reads Add a receipt
- Pull to refresh in the installed app: pull down from the top and release to save the claim and load the newest version, with a message saying whether it changed
- Faster, reliable refresh: the app page is always checked with the server (GitHub lets phones reuse a copy for 10 minutes), and pull to refresh no longer waits on a full background update
- Beta only: greyscale app icon and grey theme colour, so the beta is easy to tell apart from production
- Beta build numbers: footer, menu and help emails show the beta build, build time and current production version

## 1.2 (16 Oct 2026)

- iPhone and iPad: saving or sending shares only the file, so Save to Files no longer adds a separate text file

## 1.1 (16 Oct 2026)

- Keep work on this device (optional, with PIN encryption), remember member details, auto-delete 30 days after the PDF is built
- Installable as an app on phones and desktops, works offline
- Snap a receipt from the bottom bar
- Gentler validation: required items are flagged as you go, Build shows everything outstanding
- Readable dates (Mon 02 Nov 26), phone fixes for zoom and date fields
- Choose PKI or hand signatures for the package
- Send draft file and Send PDF through the phone share sheet (phones only); .txt draft copy on Android
- Installed app on iPhone and iPad: one Save or send button that opens the share sheet (Save to Files), since iOS opens downloads in a viewer with no way to save
- Page footer with copyright, version and last updated date; Help and Send feedback emails with numbered questions and standard line breaks
- Back-to-top button
- Production and beta keep separate saved claims and offline copies; the beta installs as CAF Travel Beta
- Single-file copy (CAF_Digital_Travel_Itinerary.html) for offline use

## 1.0

- First release: itinerary, lodging, meals, expenses, receipts, DAOD 7000-1 statutory declarations, one PDF package
