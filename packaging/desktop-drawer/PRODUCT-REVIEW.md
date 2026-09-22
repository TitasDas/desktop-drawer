# Desktop Drawer review

The applet has one job: browse a chosen folder from the Cinnamon panel and
open files in their usual applications. It leaves file organisation to the user.

## Findings addressed

- Regular files named `Private` now keep their filename and file icon. Only
  directories use the private-folder action.
- Short Unicode filenames remain intact. Long labels shorten at character
  boundaries.
- File and folder actions share one menu-item constructor.
- Directory read limits have named constants.
- The front page keeps the product story, demo, installation and basic controls.
  Detailed screenshots and troubleshooting live in the user guide.

## Design

Keep the native Cinnamon menus and settings. The applet is small enough to stay
in one file. Asynchronous directory reads, lazy submenus and cancellation protect
desktop responsiveness; they are part of the core implementation.

The review used the [Cinnamon Spices review guidance](https://github.com/linuxmint/cinnamon-spices-applets/blob/master/.github/copilot-instructions.md).
The applet uses native file launching, has no shell commands or runtime code
downloads, and does not write into its installation directory.

## Verification

Regression tests cover filtering, private directories, Unicode labels, read
limits, cancellation and opening errors. The disposable Cinnamon session covers
mouse and keyboard use, native settings, file launching and removal. Screenshots
and the demo were captured again after the changes.

See [VALIDATION.md](VALIDATION.md) for the environment and test limits. A test by
another Mint user is still recommended before submission. This review is not an
independent security audit.
