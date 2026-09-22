# Contributing

Thanks for helping improve Desktop Drawer. I built it to make my own desktop
easier to manage, and I'd like it to work well for you too.

You can help by reporting a bug, trying it on another Cinnamon version,
translating it or contributing a fix. Start with an issue describing what you
were trying to do, what got in the way and your desktop setup.

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

## Cinnamon best-practices scan

Linux Mint's [pattern checker](https://github.com/linuxmint/github-actions/tree/6fa83e83775b6d8edd9c251f3381f5265b75307a/pattern-checker)
can run locally without a GitHub token. From this repository's root, the commands
below scan a snapshot of the complete applet. Tests and packaging scripts run
outside Cinnamon and are excluded from this runtime check.

```bash
scan_work=$(mktemp -d)
git clone https://github.com/linuxmint/github-actions.git "$scan_work/scanner"
git -C "$scan_work/scanner" checkout 6fa83e83775b6d8edd9c251f3381f5265b75307a
python3 -m venv "$scan_work/venv"
"$scan_work/venv/bin/pip" install pyyaml
mkdir "$scan_work/source"
cp -R desktop/applet/desktop-drawer@linux-automations "$scan_work/source/"
git -C "$scan_work/source" init
git -C "$scan_work/source" add .
git -C "$scan_work/source" -c user.name='Local check' -c user.email='check@localhost' commit -m 'Full applet scan'
(cd "$scan_work/source" && env -u GITHUB_ACTIONS "$scan_work/venv/bin/python" "$scan_work/scanner/pattern-checker/pr_scanner.py" HEAD)
```

The scanner is pinned so results are repeatable. Update the pin and review new
rules before a Spices submission. With no Cinnamon version filter, it checks all
loaded patterns, including advice for newer versions.

The local command exits with status 1 for any finding, including advisory ones.
Review the output; see [the recorded findings](packaging/desktop-drawer/VALIDATION.md#best-practices-scanner).
A clean scan would not replace code review or desktop tests.

## Scope

Keep the applet self-contained and use native Cinnamon menus and settings.
Avoid synchronous filesystem work on the desktop thread. Cancel pending work on
close and removal. Preserve the Private-folder behaviour and do not log personal paths.

Keep a pull request focused on one user problem, describe the behaviour change,
and include relevant tests. For interface changes, attach screenshots with demo data.
Contributions are distributed under the project's GPL-3.0-or-later licence.
