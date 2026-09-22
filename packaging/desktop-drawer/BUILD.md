# Build Desktop Drawer

This source archive contains the standalone applet, its original artwork,
release documents, test code and real Cinnamon screenshots. It does not require
the linux-automations suite or its Git history.

## Rebuild the reviewed candidate

Requirements: Python 3 and Node.js. Run from the extracted source directory:

```bash
python3 tests/desktop-drawer-test.py
python3 packaging/desktop-drawer/build.py /tmp/desktop-drawer-release
python3 packaging/desktop-drawer/verify.py /tmp/desktop-drawer-release
```

Choose an output directory that does not exist. The builder writes an installation
ZIP, source archive, checksums, release manifest and a Cinnamon Spices directory.
The verifier extracts the source, runs its regression checks and rebuilds both
archives. The rebuilt archives must be byte-for-byte identical.

The installation ZIP contains the applet source and assets under one UUID folder.
Extract it into `~/.local/share/cinnamon/applets/` on a test account, then add
Desktop Drawer through Cinnamon's Applets settings. Back up an existing directory
with the same UUID before replacing it. See BETA-CHECKLIST.md in the package.

## After changing the applet

The builder checks screenshot source hashes and refuses stale images. To refresh
screenshots and the native desktop tests, use the distribution Python interpreter:

```bash
/usr/bin/python3 packaging/desktop-drawer/capture-session.py --output packaging/desktop-drawer/screenshots
```

This needs Cinnamon, Xvfb, dbus-run-session, python3-xlib, python3-pil and
update-desktop-database. It creates a temporary home and virtual display, runs
Cinnamon on a separate session bus, captures only synthetic files, and stops its
processes afterward. It does not modify your normal Cinnamon profile. The script
currently tests the installed Mint-Y and Mint-Y-Dark-Aqua themes at 100 percent
scale. Review every generated image before publishing.

If strings changed, regenerate the template using Cinnamon's extraction tool,
gettext and the Python polib module:

```bash
python3 packaging/desktop-drawer/generate-translations.py
```

The panel PNG is rendered from `icons/desktop-vault.svg`. If that SVG changes,
regenerate `icon.png` at 128 by 128 pixels with an SVG renderer such as CairoSVG.
Keep the SVG in the release as the editable source.

## Submit to Cinnamon Spices

Copy only `desktop-drawer@linux-automations/` from the release output into the
Spices checkout, then run its `validate-spice` script. Read SUBMISSION.md for the
candidate status and proposed pull request. This source archive includes the
review checklist, but none of the development tools are required by the applet.

## Licence

GPL-3.0-or-later. See COPYING.md and LICENSE for the grant and artwork scope.
