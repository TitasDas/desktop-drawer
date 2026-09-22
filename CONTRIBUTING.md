# Contributing

Bug reports, testing on other Cinnamon versions, translations and small fixes are welcome.
Start with an issue that describes the user problem and your environment.

## Run checks

From the repository root, with Python 3 and Node.js:

```bash
python3 tests/desktop-drawer-test.py
node --check desktop/applet/desktop-drawer@linux-automations/applet.js
python3 packaging/desktop-drawer/build.py /tmp/drawer-release
python3 packaging/desktop-drawer/verify.py /tmp/drawer-release
```

Use an output directory that does not exist. See the build guide for desktop test
and translation dependencies. Changes to applet code, settings or artwork require
fresh screenshots; the builder checks their source hashes.

## Scope

Keep the applet self-contained and use native Cinnamon menus and settings.
Avoid synchronous filesystem work on the desktop thread. Cancel pending work on
close and removal. Preserve the Private-folder behaviour and do not log personal paths.

Keep a pull request focused on one user problem, describe the behaviour change,
and include relevant tests. For interface changes, attach screenshots with demo data.
Contributions are distributed under the project's GPL-3.0-or-later licence.
