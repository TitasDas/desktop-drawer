# Desktop Drawer

**Keep your everyday files one click away in the Cinnamon panel.**

Choose a folder, browse its subfolders, and open files in the applications you
already use. Desktop Drawer works locally, with no account or extra runtime downloads.

[Download the 1.2.0 beta](https://github.com/TitasDas/desktop-drawer/releases/download/v1.2.0/desktop-drawer-1.2.0.zip)

[Installation](#install) | [Report a problem](https://github.com/TitasDas/desktop-drawer/issues/new/choose)

This is a beta release. Tested on Linux Mint with Cinnamon 6.0.5 and X11.
It is not yet available through Cinnamon Spices.

## See it in action

![Actual recording of opening Desktop Drawer and browsing project and reading folders](docs/media/desktop-drawer-demo.gif)

Hover over the panel icon, open Projects or Reading, and use **Choose folder**
to make the drawer your own. The recording uses real Cinnamon and demo files.
[Watch or download the MP4](docs/media/desktop-drawer-demo.mp4).

## Make a folder easy to reach

- Keep project files, notes or reading material near your work.
- Browse with hover, click or the keyboard.
- See which folder is open and change it directly from the menu.
- Keep filenames inside folders named Private out of the drawer.

<table>
<tr><th>Dark theme</th><th>Light theme</th></tr>
<tr>
<td><img src="packaging/desktop-drawer/screenshots/drawer-dark.png" alt="Desktop Drawer in a dark Cinnamon theme, browsing a project folder" width="265"></td>
<td><img src="packaging/desktop-drawer/screenshots/drawer-light.png" alt="The same Desktop Drawer menu in a light Cinnamon theme" width="265"></td>
</tr>
</table>

## Install

1. [Download desktop-drawer-1.2.0.zip](https://github.com/TitasDas/desktop-drawer/releases/download/v1.2.0/desktop-drawer-1.2.0.zip).
2. Open your Home folder. Press **Ctrl+H** to show hidden folders, then open
   `.local/share/cinnamon/applets`. Create any missing folders.
3. Extract the ZIP there. The resulting path should be
   `~/.local/share/cinnamon/applets/desktop-drawer@linux-automations/applet.js`.
4. Open Cinnamon **System Settings**, then **Applets**. Find **Desktop Drawer**
   in the installed applets list and add it to your panel.
5. Open the drawer and select **Choose folder**. Pick your notes, current project
   or another folder you use often.

If you already have a folder named `desktop-drawer@linux-automations`, remove
its applet from the panel and back up that folder before replacing it. Add it
back after extraction. This keeps the upgrade from mixing old and new files.

If you leave the folder unset, the drawer uses `Organized Desktop` inside your
Desktop folder when present, otherwise your Desktop folder.

## Set it up your way

![Native Cinnamon settings for choosing a folder and adjusting hover behaviour](packaging/desktop-drawer/screenshots/settings.png)

Turn **Open menus on hover** off if you prefer clicking. Adjust how long the
pointer must rest over the panel icon before the drawer opens.

| Control | What it does |
|---|---|
| Click the panel icon | Open or close the drawer |
| Hover over the icon | Open after the configured delay, when enabled |
| Right and Left arrows | Open and close subfolders in left-to-right layouts |
| Enter | Open the selected file or folder |
| Escape | Close the drawer |
| Open folder | See the whole folder in your file manager |

## Private folders and your files

Folders named `Private`, ignoring capitalisation, are shown as **Open Private
folder**. Their contents stay out of the drawer, including inside subfolders.
They still open in your file manager. This is a display convenience, not a lock
or encryption.

Desktop Drawer does not move, rename, edit or delete your files. It does not
collect usage data. Cinnamon stores your chosen folder and preferences locally.
A network-mounted folder can use that filesystem's network connection.

The drawer shows up to 30 visible entries per folder and three folder levels.
Hidden files are omitted and directory symlinks are not expanded. For larger
folders, **Open folder** gives you the complete listing.

## When something goes wrong

If a folder was moved or a drive disconnected, **Choose folder** remains available.
If a file cannot open, the applet points you to its default application.

<table>
<tr><th>Folder unavailable</th><th>File could not open</th></tr>
<tr>
<td><img src="packaging/desktop-drawer/screenshots/folder-unavailable.png" alt="An unavailable folder with a Choose folder recovery action" width="238"></td>
<td><img src="packaging/desktop-drawer/screenshots/opening-error.png" alt="A notification explaining that the item could not open and suggesting checking its default application" width="420"></td>
</tr>
</table>

See the [user guide](docs/USER-GUIDE.md) for empty folders, limits and removal.
To uninstall, remove the applet from your panel, then delete its directory from
`~/.local/share/cinnamon/applets/`. Your browsed files stay untouched.

## Help test the beta

Try the [short beta checklist](packaging/desktop-drawer/BETA-CHECKLIST.md) and
[report what happened](https://github.com/TitasDas/desktop-drawer/issues/new/choose).
Include your Cinnamon version and Linux distribution. Use demo filenames in screenshots.

Automated checks cover menu interactions, keyboard activation, settings, folder
states and package rebuilds. Other Cinnamon versions, Wayland, assistive technology
and different display scales still need testing. See the
[validation record](packaging/desktop-drawer/VALIDATION.md) for the scope and limits.

## For contributors

The applet is plain JavaScript using Cinnamon's built-in libraries.
[Build instructions](packaging/desktop-drawer/BUILD.md),
[contribution guide](CONTRIBUTING.md), and
[release notes](packaging/desktop-drawer/CHANGELOG.md) are included.
The repository contains only Desktop Drawer, not the larger automation suite.

## Licence

GPL-3.0-or-later. See [COPYING.md](COPYING.md) and [LICENSE](LICENSE).
Copyright (C) 2026 TitasDas.
