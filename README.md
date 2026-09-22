# Desktop Drawer

Enjoy your wallpaper. Keep your files within reach.

I like things organised, and I like being able to see a good wallpaper. A
desktop covered in files feels like a cluttered room or a messy desk to me.
It makes it harder to settle down and focus.

But I also download a lot of files, so my desktop keeps filling up. I wanted
to tidy them away without making them harder to find. That's why I built
Desktop Drawer.

It's a small applet for Cinnamon that lets you browse a folder from your
panel. You put your files in order, and the drawer keeps them close by.
Your desktop has room for your wallpaper again, and your files are still
easy to reach.

[Download the 1.2.0 beta](https://github.com/TitasDas/desktop-drawer/releases/download/v1.2.0/desktop-drawer-1.2.0.zip)

[Installation](#install) | [Tell me how it goes](https://github.com/TitasDas/desktop-drawer/issues/new/choose)

## See how it works

![Desktop Drawer opening from the Cinnamon panel and browsing project and reading folders](docs/media/desktop-drawer-demo.gif)

Browse your folders from the panel and open files in their usual app.
The recording uses sample files in a real Cinnamon session.
[Watch the video](docs/media/desktop-drawer-demo.mp4).

Tested on Cinnamon 6.0.5 with X11. The beta needs manual installation;
[Cinnamon Spices submission](https://github.com/linuxmint/cinnamon-spices-applets/pull/9060) is under review.

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

## Using the drawer

Click the panel icon or hover over it to browse your chosen folder. Select a
file to open it, or use **Open folder** to open the folder in your file manager.
**Choose folder** opens settings, where you can also turn hover off or adjust
the delay.

Use the arrow keys to browse, **Enter** to open an item and **Escape** to close
the menu.

You organise the files yourself. Desktop Drawer does not move, rename or delete
them. It works locally and collects no usage data. Folders named `Private`
can be opened in your file manager, but their contents stay out of the drawer.
This does not lock or encrypt them.

See the [user guide](docs/USER-GUIDE.md) for screenshots, browsing limits,
troubleshooting and removal.

## Tell me how it works for you

If the drawer helps you keep things tidy, or something gets in the way,
[tell me about it](https://github.com/TitasDas/desktop-drawer/issues/new/choose).
Please include your Cinnamon version and Linux distribution when reporting a
problem. Keep personal filenames out of screenshots.

You can also try the [beta checklist](packaging/desktop-drawer/BETA-CHECKLIST.md)
or [contribute a fix or translation](CONTRIBUTING.md).

## Development

The applet uses JavaScript and Cinnamon's built-in libraries.
See [build instructions](packaging/desktop-drawer/BUILD.md),
[test coverage and limits](packaging/desktop-drawer/VALIDATION.md), and
[changes](packaging/desktop-drawer/CHANGELOG.md).

## Licence

GPL-3.0-or-later. See [COPYING.md](COPYING.md) and [LICENSE](LICENSE).
Copyright (C) 2026 TitasDas.
