# Walkthrough video

The 33-second walkthrough on implantintelligence.com/p/desktop-drawer, and the teaser GIF in the README, come from a real Cinnamon session on a virtual display. Nothing in the drawer footage is mocked; only the opening clutter is drawn.

```bash
python3 make-wallpaper.py wallpaper.png
/usr/bin/python3 ../record-walkthrough.py --output rec --wallpaper "$PWD/wallpaper.png"   # Xvfb + Cinnamon, ~40 s
python3 compose.py            # intro, trimmed footage with captions, outro; writes frames/, captions, chapters
./encode.sh Wallpaper.mp3 6   # soundtrack and whooshes, MP4, poster, teaser.gif
```

Requirements: Cinnamon, Xvfb, dbus-run-session, ffmpeg, python3-xlib, Pillow. The recorder writes `events.json` with the time of each step (hover, submenus, keyboard, settings, light theme) and the editor cuts and captions by those names, so timing changes in the applet do not break the edit.

The disposable session has no session manager, so `csd-background` cannot paint the wallpaper; the desktop records as exact black and the editor keys that to the same wallpaper image. Music is "Wallpaper" by Kevin MacLeod (CC BY 4.0), from incompetech.com (`mp3-royaltyfree/Wallpaper.mp3`). Fonts: Bricolage Grotesque and Work Sans, both OFL; set `WALKTHROUGH_FONTS` to their directory.
