# Walkthrough video

The 33-second walkthrough on implantintelligence.com/p/desktop-drawer, and the teaser GIF in the README, come from a real Cinnamon session on a virtual display. Nothing in the drawer footage is mocked; only the opening clutter is drawn.

```bash
python3 -c "from PIL import Image; im=Image.open('/usr/share/backgrounds/linuxmint-virginia/dmirlea_romania.jpg'); w,h=im.size; cw=h*4//3; x=max(0,min(int(w*0.66-cw*0.62),w-cw)); im.crop((x,0,x+cw,h)).resize((1280,960)).save('wallpaper.png')"
/usr/bin/python3 ../record-walkthrough.py --output rec --wallpaper "$PWD/wallpaper.png"   # Xvfb + Cinnamon, ~40 s
python3 compose.py            # intro, trimmed footage with captions, outro; writes frames/, captions, chapters
./encode.sh Wallpaper.mp3 6   # soundtrack and whooshes, MP4, poster, teaser.gif
```

Requirements: Cinnamon, Xvfb, dbus-run-session, ffmpeg, python3-xlib, Pillow. The recorder writes `events.json` with the time of each step (hover, submenus, keyboard, settings, light theme) and the editor cuts and captions by those names, so timing changes in the applet do not break the edit.

The disposable session has no session manager, so `csd-background` cannot paint the wallpaper; the desktop records as exact black and the editor keys that to the same wallpaper image. Music is "Wallpaper" by Kevin MacLeod (CC BY 4.0), from incompetech.com (`mp3-royaltyfree/Wallpaper.mp3`). Fonts: Bricolage Grotesque and Work Sans, both OFL; set `WALKTHROUGH_FONTS` to their directory.

The backdrop is "Romania" by Daniel Mirlea (https://danielmirlea.com), shipped with Linux Mint 21.3 under the Unsplash License. Captions use the shared style in `captions.py`: a soft transparent scrim with large type, kept to the right of the drawer menu.

## Narration

`narration.json` holds the spoken script, one line per scene. `narrate.py` voices it with Kokoro-82M (Apache 2.0, runs on CPU: `pip install torch --index-url https://download.pytorch.org/whl/cpu kokoro soundfile`), and `mix.py` stretches nothing itself: render with `NARRATION_LENS=<key>-lens.json` so each scene holds long enough for its line, then run `mix.py <key>` to lay the voice in, duck the music under it with a sidechain compressor, and write captions and a transcript that follow the narration. Paths in `mix.py` point at the working folder used to build the published video; adjust them to yours. The video pages label the narration as a synthetic voice.
