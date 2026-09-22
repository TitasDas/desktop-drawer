# Demonstration recording

This is an actual Cinnamon 6.0.5 session on a virtual X11 display with synthetic files.
It shows opening Desktop Drawer, browsing Projects and Reading, and finding Choose folder.
The GIF is encoded from the accompanying screen-recorded MP4. No mock UI or generated frames are used.

To record it again, install ffmpeg and the capture dependencies from the build guide, then run:

```bash
/usr/bin/python3 packaging/desktop-drawer/capture-session.py --output /tmp/drawer-demo-capture --demo
```

The recorder modifies only the disposable session and writes these media files. It does not record your normal desktop.
