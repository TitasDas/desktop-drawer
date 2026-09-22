# Desktop Drawer submission

Candidate: 1.2.0, prepared 2026-09-22. GPL-3.0-or-later. Not submitted.

## Files to submit

Build with `python3 packaging/desktop-drawer/build.py OUTPUT_DIRECTORY`.
Copy only the generated `desktop-drawer@linux-automations/` directory into the
Cinnamon Spices applets repository. It contains author metadata, a catalogue
screenshot, additional screenshots, README, and the applet under `files/`.
Do not include archives, unrelated automations or the project's Git history.

The UUID is unchanged from the local applet. The public name is Desktop Drawer
and the author is TitasDas. Runtime dependencies are Cinnamon's built-in libraries.
The icon's editable SVG, licence text and attribution are bundled.

Run the upstream check from the Spices checkout:

```bash
python3 validate-spice desktop-drawer@linux-automations
```

Build and source-reproduction instructions are in BUILD.md. The review, screenshot
provenance and test limits are in PRODUCT-REVIEW.md, SCREENSHOTS.md and VALIDATION.md.

## Release checklist

- [x] Apply the author's GPL-3.0-or-later choice to the applet and original artwork.
- [x] Improve folder context, settings discovery, hover consistency and error feedback.
- [x] Replace decorative wording and simplify the small panel icon.
- [x] Capture the actual current UI with synthetic files in dark and light themes.
- [x] Exercise keyboard navigation, settings, folder states and applet lifecycle in Cinnamon.
- [x] Exercise keyboard file and folder activation through a disposable desktop handler.
- [x] Generate the translation template from current applet, metadata and settings strings.
- [x] Verify the installation and source archives, byte-identical rebuild, and upstream submission directory.
- [ ] Ask another Mint user to follow BETA-CHECKLIST.md with their normal applications.
- [x] Inspect the applet changes and every screenshot in the final set.
- [ ] Open the one-applet pull request and respond to maintainer feedback.
- [ ] Record the published Cinnamon Spices URL after acceptance.

Other Cinnamon versions, Wayland, assistive technology and display scales still
need testing. This candidate has not been independently security-reviewed.

## Proposed pull request

Title: `Desktop Drawer: add configurable panel folder browser`

Desktop Drawer opens a chosen folder from the Cinnamon panel. Users can browse
subfolders and open files with their usual applications. The menu shows the current
folder and includes a Choose folder action; native xlet settings control the folder
and hover behaviour.

Directory reads are asynchronous, subfolders load on demand, and pending reads
are cancelled when the drawer closes. Private folder contents stay hidden at every
browsing depth. Hidden files are omitted and directory symlinks are not expanded.
The applet uses built-in Cinnamon libraries and makes no runtime downloads.

The source and original artwork are GPL-3.0-or-later. Screenshots show synthetic
files in real Cinnamon sessions. Validation covers Cinnamon 6.0.5 on X11, keyboard
navigation and activation, native settings, folder states, removal and re-addition,
regression tests, upstream structural checks and reproducible archives.
Other Cinnamon versions and Wayland remain unverified.

Update this description with any later human beta results before submitting.
