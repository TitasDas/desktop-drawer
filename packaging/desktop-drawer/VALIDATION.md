# Desktop Drawer validation

Date: 2026-09-22. Candidate: 1.2.1, GPL-3.0-or-later.

Version 1.2.1 includes the regular-file `Private` fix and Unicode label tests.
The native session and regression tests were rerun for this candidate.
The published 1.2.0 beta archives have not been replaced.

## Source and behaviour

- JavaScript syntax and source metadata checks.
- Hidden files, directory symlinks, item and scan limits, and submenu depth limits.
- Lazy submenu loading, failed/cancelled enumeration cleanup and stale-result suppression.
- Private folders at nested levels and as the selected root.
- Exact preservation of selected paths with trailing spaces.
- Visible default-application failure notification, suppressed after applet removal.

## Native Cinnamon run

Environment: Cinnamon 6.0.5, X11, Xvfb, 100 percent scale, separate temporary home
and session bus. The capture script stops the disposable session after the run.

- Active folder heading and Choose folder action.
- Native settings updates and actual settings window opening.
- Empty, missing and Private folder states.
- Hover disabled for both root and submenu, click activation, and hover enabled.
- Keyboard Right, Left, Escape and Enter.
- Real Gio dispatch to an isolated desktop handler for both a file and a folder.
- Removal while open and re-addition with a non-default selected folder retained.
- Actual failed-launch notification, captured without exposing the filename.
- Direct dark and light theme screenshots and fresh settings/state screenshots.

The run log contains expected virtual-session warnings about display modes and
the absence of a systemd service on the isolated session bus. The deliberately failed launch logs the expected recovery message. There is no
uncaught Desktop Drawer JavaScript exception. The local raw log is excluded from public packages.

## Package checks

The release verifier checks safe archive paths, complete GPL text and the explicit
or-later grant, SHA-256 checksums, and equality of installed source and the Spices
directory. It extracts the source archive, runs the tests and rebuilds both
archives; the resulting bytes must match. Screenshot source and image hashes
are checked at build time.

Upstream structural validation uses the Cinnamon Spices validate-spice script.
The checked upstream commit is `d25cb33bbd2bf37f2ad6c3cb6ce4efbfd1ec9b94`,
retrieved on 2026-09-22. Structural validation passed.

## Best-practices scanner

Scanned the complete runtime source at `f994509` using Linux Mint's
[pattern checker](https://github.com/linuxmint/github-actions/tree/6fa83e83775b6d8edd9c251f3381f5265b75307a/pattern-checker),
commit `6fa83e83775b6d8edd9c251f3381f5265b75307a`. All 72 patterns were loaded,
without version filtering. Result: two warnings, no blocking or informational
findings. The local scanner returned status 1 because warnings were present.

| Warning | Review |
|---|---|
| `tilde_in_string`, applet.js:85 | Detects the `~/` input prefix. The following line expands it with `GLib.get_home_dir()` and `GLib.build_filenamev()`. It is not passed literally to filesystem operations. |
| `hardcoded_data_dir`, applet.js:21 | The gettext path matches Cinnamon's documented xlet translation setup and the translation install location in the tested Cinnamon 6.0.5. Changing only the lookup to `XDG_DATA_HOME` could separate it from the installed translations. |

These findings remain visible for maintainer review. Neither rule was suppressed.
The translation setup is documented in the [upstream review guidance](https://github.com/linuxmint/cinnamon-spices-applets/blob/d25cb33bbd2bf37f2ad6c3cb6ce4efbfd1ec9b94/.github/copilot-instructions.md#translation--localization).
The scanner checks text patterns, not program behaviour or lifecycle correctness.

## Limits

This is an agent-run engineering and usability inspection. It does not establish
screen-reader support, accessibility compliance, Wayland support, compatibility
with other Cinnamon versions, or behaviour in every desktop application. File
and folder opening used a controlled desktop handler rather than a user's editor.
A second human should run BETA-CHECKLIST.md before submission. Cinnamon Spices [PR #9060](https://github.com/linuxmint/cinnamon-spices-applets/pull/9060) is awaiting review. Public beta releases are available
from https://github.com/TitasDas/desktop-drawer/releases.

## Submission checks

Version 1.2.1 was submitted in PR #9060 at commit `6ef5dd5`.
Every committed submission file matched the verified package.
The upstream pattern job passed with the same two advisory warnings.
The upstream structural job is skipped in the pull-request-target workflow;
local `validate-spice` passed. Maintainer review is pending.
