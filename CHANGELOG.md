# Changelog

Versioning: the minor number goes up by one only when the beta is promoted to production (1.1, 1.2, 1.3...). The beta shows the number the next production release will have plus its own build number, which goes up with every beta publish and starts again at 1 after a promotion, for example "Version 1.3 beta 3, built 17 Oct 2026 10:42 (production is 1.2)". The major number changes only when the owner decides a release is a major one.

## 1.10 (beta, in progress)

- From finance clerk feedback: the worksheet sections follow the order a clerk enters them in ClaimsX: A Personal information, B Itinerary, C Transportation (rental vehicles included), D Lodging, E General expenses, F Currency exchange, G Meals last. The form on the page uses the same order and letters, in both layouts
- Calls register removed: phone plan charges and calls are general expenses (section E), with Phone plan charges, Business call and Personal call offered as descriptions and Phone charges in Add a receipt. Drafts from earlier versions move their calls into section E, keeping receipts and missing-receipt declarations
- Leave and field days: tap a date in the meals section to open a short dialog: a duty day, leave, or in the field, for that day only or through a later day of the trip. Each date shows Leave or Field under it, with the row tinted, and rows never change height, so the page does not move. Leave still comes from leave stops in section B and field nights from section D until the member changes a day. Changing a day puts its meals back to their defaults (leave and field days unticked)
- Field stays in lodging (section D): a new Field option, like Quarters, that asks only where you were in the field, with no cost or receipt. Each night of a Field stay makes that day a field day. Setting a day to Field in the meals section adds (or extends) a Field stay for that night, and setting it back takes the night out, so the two always agree
- When a day change adds or removes a Field stay in section D, the meals table stays where it was on the screen
- Both layouts show leave and field days with the meals, so the FSA can see field nights for Land Duty Allowance. The package shows each day as set, with no mark for whether the member or the app set it. In the designed layout a leave or field day is a band of colour down its column, and claimed meals read Meal claimed instead of a check mark
- Beautify export: the first page is now a claimant summary for the member (what to do before sending, total entered, things to look over such as field nights, leave days and open checks, what was entered, and the page map). It opens with a navy band across the top of the page that says it is for the claimant and not part of the claim, which starts on page 2. The worksheet opens with its own title, so the claim is complete without the summary page. The index and certification follow the summary of amounts when they fit
- Standard layout cleaned up to look more like current CAF forms: a form header with the file number, trip dates, TAN and trip locator in labelled boxes, section bars with the letter in a white tab, section A in labelled boxes, lighter table lines, and the certification in its own box. The meals keep their X marks
- Travel Itinerary layout (experimental, off by default, in the menu beside Beautify export; one or the other): a package designed for its two readers. Part 1, for the traveller: a cover branded Travel Itinerary with the trip, a ticket strip (from, to, depart, return, days, nights, stops), the journey, what is in the package with the total entered, the steps before sending and things to look over, then every receipt at a glance on a contact sheet with its reference, amount and page. Part 2, for the finance clerk: a data entry sheet in ClaimsX order (itinerary, transportation split into the three ClaimsX screens by description, lodging, other expenses, gain or loss on exchange, meals one line per day) with a tick box on every line, receipt references that carry the page, the total entered and the traveller's certification. Then the receipts and declarations with a slim header. A coloured spine on the left of every page says which part it belongs to
- The PDF calls itself what it is, a travel itinerary for the clerk to enter in ClaimsX, not the claim: titles read Temporary duty travel itinerary, the first page of the designed layout is the Traveller summary, the signature line is the traveller's, and file names use TD-Itinerary (Itineraire-ST in French) in place of TD-Claim
- Travel Itinerary layout redesign: two parts, TRAVELLER and FINANCE (the receipts and declarations belong to Finance). Each part opens with a full-width band in its colour with the part name in large stencil capitals over a red rule, and later pages carry the part name as a solid block beside the security marking. The left spine is replaced by a thumb tab on the right edge (clear of staples, duotangs and binder holes), set higher for Traveller and lower for Finance, with the page within the part. The first two letters of the surname appear as colour-coded filing blocks under the tab on each part's first page, so a stack of packages sorts by surname at a glance. The Finance first page stands alone: rank and given names, the surname in large capitals, trip, PRI and telephone, and a plate with the file number, dates and total. The explanatory hints on the data entry sheet are gone, and a nil step reads NIL
- Travel Itinerary layout, second pass: each part opens as a WWII-style file jacket in place of the stencil band. A buff cover with a folder tab (Part 1 of 2, Traveller; Part 2 of 2, Finance), typed headings and fields in a typewriter face, a maple leaf with Canadian Armed Forces, and the part stamped across it in red. The traveller's identity is set like a Canadian identity disc: a green octagonal No. 1 disc with the last three of the service number, the red round No. 2 with a maple leaf, the surname as large as the line allows, and the disc's stamped line (number, rank, surname and initials, CDN). Typed fields along the foot: file number, period, destination and TAN on the traveller's cover; file number, period, total entered and telephone on the Finance page. The top left of each opener stays clear for the official signature block. The app logo, the colour-coded surname blocks and the cover's What comes next box are gone. Colours are navy for Traveller and olive for Finance
- Travel Itinerary layout, third pass (designed on a canvas first): each part opens with one buff band from the top of the page, holding the security marking and clear space for the official signature block, the identity disc in the part's colour (navy for Traveller, olive for Finance) with the last three of the service number, the surname, a typed line and the disc's stamped line, a small TRAVELLER or FINANCE stamp, and one line of typed fields. The folder tab and the Canadian Armed Forces line are gone. The traveller's cover is now the traveller's copy: the route on one line, the trip day by day (travel legs, nights with each stay and a dashed gap where a night has no lodging, meals claimed as filled pips with rations and leave or field days shown, expenses as reference chips), a Before you send checklist with tick boxes, the enclosures with their pages, and a receipt tape listing every line going to Finance with the total, counts and when it was built (one line per section when the trip is too long to list)
- Travel Itinerary layout: the small TRAVELLER or FINANCE stamp now sits beside the security marking at the top right of the band, so a long surname uses the full width
- Statutory declaration: the telephone call wording and matter line are no longer used (missing phone receipts use the general expense wording). The AJAG review list is updated

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
