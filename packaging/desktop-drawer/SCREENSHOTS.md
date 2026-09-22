# Desktop Drawer screenshots

These are direct captures of Desktop Drawer 1.2.0 running on Cinnamon 6.0.5
with X11 in a virtual display. They show synthetic folders and files. No image
generation, compositing or retouching was used.

- `screenshots/drawer-dark.png`: open project folder in Mint-Y-Dark-Aqua.
- `screenshots/drawer-light.png`: the same folder in Mint-Y.
- `screenshots/opening-error.png`: the real notification after a failed launch.
- `screenshots/settings.png`: the native Cinnamon settings window.
- `screenshots/folder-empty.png`: an empty folder with a visible recovery action.
- `screenshots/folder-unavailable.png`: a missing folder with Choose folder available.
- `screenshots/private-folder.png`: Private selected as the root, with contents hidden.

The catalogue image `screenshot.png` is copied from drawer-dark.png during the
build. `screenshots/manifest.json` records the image hashes and applet source
hashes. The builder refuses to package images captured against different source.

Use the capture-session.py command in BUILD.md to refresh the set. The images
show the operating system's actual theme and controls. They are not a claim
that other themes, scaling levels or Cinnamon versions have been tested.
