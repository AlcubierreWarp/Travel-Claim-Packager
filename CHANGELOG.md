# Changelog

Versioning: the minor number goes up by one only when the beta is promoted to production (1.1, 1.2, 1.3...). The beta shows the number the next production release will have plus its own build number, which goes up with every beta publish and starts again at 1 after a promotion, for example "Version 1.3 beta 3, built 17 Oct 2026 10:42 (production is 1.2)". The major number changes only when the owner decides a release is a major one.

## 1.4 (beta, in progress)

- File names follow Date_FileNo_Marking_Details for the PDF package and the draft file, e.g. 20261102_7209-1_PB_TD-Claim_Winnipeg-Course_Capt-Sample.pdf
- Optional file number and a security marking (PROTECTED B by default, PROTECTED A or none) in the Package section; remembered with your details
- The security marking is printed at the top right of every page of the PDF

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
