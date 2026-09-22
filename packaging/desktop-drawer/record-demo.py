#!/usr/bin/env python3
"""Record a real menu interaction in the disposable session made by capture-session.py."""
import ast,json,os,subprocess,sys,time
from pathlib import Path
from Xlib import X,display
from Xlib.ext import xtest
pid=int(sys.argv[1]);output=Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
proc=dict(e.decode().split('=',1) for e in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0') if b'=' in e)
home=Path(proc['HOME']);assert home.parent==Path('/tmp') and home.name.startswith('desktop-drawer-capture-') and (home/'.isolated-cinnamon').exists()
env=os.environ|{'DBUS_SESSION_BUS_ADDRESS':proc['DBUS_SESSION_BUS_ADDRESS']}
def evaluate(code):
 s=subprocess.check_output(['gdbus','call','--session','--dest','org.Cinnamon','--object-path','/org/Cinnamon','--method','org.Cinnamon.Eval',code],env=env,text=True).strip()
 assert s.startswith('(true, '),s
 return json.loads(ast.literal_eval(s[7:-1]))
def move(x,y):
 xtest.fake_input(d,X.MotionNotify,x=int(x),y=int(y));d.sync()
def hover(label):
 pos=evaluate('global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='+json.dumps(label)+').actor.get_transformed_position()')
 move(pos[0]+60,pos[1]+12);time.sleep(2)
def click():
 xtest.fake_input(d,X.ButtonPress,1);xtest.fake_input(d,X.ButtonRelease,1);d.sync()
d=display.Display(proc['DISPLAY'])
evaluate("global.get_window_actors().filter(a=>a.meta_window.get_title()==='Desktop Drawer').forEach(a=>a.meta_window.minimize()); imports.gi.Gio.Settings.new('org.cinnamon.theme').set_string('name','Mint-Y-Dark-Aqua'); global.drawer.menu.close(); true")
move(700,200);time.sleep(.8)
mp4=output/'desktop-drawer-demo.mp4'
record=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','x11grab','-framerate','12','-video_size','360x460','-i',proc['DISPLAY']+'+0,300','-an','-c:v','libx264','-pix_fmt','yuv420p',str(mp4)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
 time.sleep(1);move(20,740);time.sleep(1.4)
 hover('Projects')
 evaluate("global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='Projects').menu.close(); true")
 hover('Reading')
 evaluate("global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='Reading').menu.close(); true")
 hover('Choose folder')
 move(20,740);click();time.sleep(1)
finally:
 try: _,error=record.communicate(b'q',timeout=10)
 except subprocess.TimeoutExpired: record.kill();record.wait();raise
 if record.returncode: raise RuntimeError(error.decode())
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(mp4),'-filter_complex','[0:v]split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer','-loop','0',str(output/'desktop-drawer-demo.gif')],check=True)
(output/'README.md').write_text('''# Demonstration recording

This is an actual Cinnamon 6.0.5 session on a virtual X11 display with synthetic files.
It shows opening Desktop Drawer, browsing Projects and Reading, and finding Choose folder.
The GIF is encoded from the accompanying screen-recorded MP4. No mock UI or generated frames are used.

To record it again, install ffmpeg and the capture dependencies from the build guide, then run:

```bash
/usr/bin/python3 packaging/desktop-drawer/capture-session.py --output /tmp/drawer-demo-capture --demo
```

The recorder modifies only the disposable session and writes these media files. It does not record your normal desktop.
''')
print('Recorded real Cinnamon demo:',output/'desktop-drawer-demo.gif')
d.close()
