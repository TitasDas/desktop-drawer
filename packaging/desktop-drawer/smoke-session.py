#!/usr/bin/env python3
"""Test a marked disposable Cinnamon session and optionally capture its screens."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from Xlib import X, XK, display
from Xlib.ext import xtest
from PIL import Image

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('pid',type=int)
parser.add_argument('--screenshots',type=Path)
args=parser.parse_args()
proc=dict(entry.decode().split('=',1) for entry in Path(f'/proc/{args.pid}/environ').read_bytes().split(b'\0') if b'=' in entry)
home=Path(proc['HOME'])
assert home.parent==Path('/tmp') and home.name.startswith('desktop-drawer-capture-')
assert (home/'.isolated-cinnamon').exists()
assert proc['DISPLAY'] != os.environ.get('DISPLAY')
env=os.environ | {'DBUS_SESSION_BUS_ADDRESS':proc['DBUS_SESSION_BUS_ADDRESS']}
UUID='desktop-drawer@linux-automations'


def evaluate(code):
    out=subprocess.check_output(['gdbus','call','--session','--dest','org.Cinnamon','--object-path','/org/Cinnamon','--method','org.Cinnamon.Eval',code],env=env,text=True,stderr=subprocess.DEVNULL).strip()
    assert out.startswith('(true, '),out
    return json.loads(ast.literal_eval(out[7:-1]))

def wait_for(code, check):
    for _ in range(100):
        try:
            result=evaluate(code)
            if check(result): return result
        except (subprocess.CalledProcessError, AssertionError): pass
        time.sleep(.1)
    raise AssertionError(f'Timed out: {code}')

def configure(**values):
    # Emulate Cinnamon's separate settings process, in the disposable profile only.
    settings=home/'.config/cinnamon/spices'/UUID/(UUID+'.json')
    data=json.loads(settings.read_text())
    for key,value in values.items(): data[key]['value']=value
    settings.write_text(json.dumps(data))
    time.sleep(.2)

labels="global.drawer.menu._getMenuItems().map(i=>i.label ? i.label.text : '')"
get_drawer=f"imports.ui.appletManager.get_object_for_uuid('{UUID}','0')"
wait_for(f'Boolean({get_drawer})',bool)
evaluate(f'global.drawer={get_drawer}; true')
d=display.Display(proc['DISPLAY'])

def key(name):
    code=d.keysym_to_keycode(XK.string_to_keysym(name))
    xtest.fake_input(d,X.KeyPress,code);xtest.fake_input(d,X.KeyRelease,code);d.sync()

def move(x,y):
    xtest.fake_input(d,X.MotionNotify,x=x,y=y);d.sync()

def open_drawer():
    evaluate('global.drawer._openDrawer(); true')
    return wait_for(labels,lambda x:'Choose folder' in x)

manifest={}
def screenshot(name,code=None):
    if not args.screenshots: return
    time.sleep(.35)
    if code:
        x,y,w,h=evaluate(code)
        x,y=max(0,int(x)-12),max(0,int(y)-12)
        w,h=min(1100-x,int(w)+24),min(760-y,int(h)+24)
    else:
        x,y,w,h=evaluate('(()=>{let a=global.drawer.menu.actor;let p=a.get_transformed_position();let s=a.get_transformed_size();return [p[0],p[1],s[0],s[1]]})()')
        x,y=max(0,int(x)-12),max(0,int(y)-12)
        w,h=min(1100-x,int(w)+36),760-y
    pixels=d.screen().root.get_image(x,y,w,h,X.ZPixmap,0xffffffff)
    path=args.screenshots/(name+'.png')
    Image.frombytes('RGB',(w,h),pixels.data,'raw','BGRX').save(path)
    manifest[name]={'file':path.name,'pixels':[w,h],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

value=open_drawer()
assert 'Organized Desktop' in value and 'Open folder' in value
assert all('—' not in x and '…' not in x for x in value)
projects="global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='Projects')"
evaluate(projects+'.menu.open(true); true')
nested=projects+".menu._getMenuItems().map(i=>i.label ? i.label.text : '')"
value=wait_for(nested,lambda x:'Release checklist.txt' in x)
assert 'Open Private folder' in value and not any('SECRET' in x for x in value)
screenshot('drawer-dark')
print('PASS: native folder heading, actions, plain copy and nested Private hiding',flush=True)

for suffix,expected,name in [('missing','Cannot read this folder.','folder-unavailable'),('empty','No files to show.','folder-empty'),('Desktop/Organized Desktop/Private','Private folder contents are hidden.','private-folder')]:
    configure(folder=str(home/suffix))
    value=open_drawer()
    assert expected in value,value
    assert not any('HIDDEN-DEMO' in x for x in value)
    screenshot(name)
print('PASS: missing, empty and Private root states retain Choose folder',flush=True)

# Filenames with trailing whitespace must survive folder selection unchanged.
space=home/'Folder with trailing space '
space.mkdir();(space/'Visible.txt').write_text('demo')
configure(folder=str(space))
assert 'Visible.txt' in open_drawer()
print('PASS: selected folder paths preserve trailing spaces',flush=True)

configure(**{'folder':'','open-on-hover':False})
move(600,300);move(20,740);time.sleep(.5)
assert evaluate('global.drawer.menu.isOpen') is False
xtest.fake_input(d,X.ButtonPress,1);xtest.fake_input(d,X.ButtonRelease,1);d.sync()
wait_for('global.drawer.menu.isOpen',bool)
wait_for(labels,lambda x:'Projects' in x)
# Move onto Projects. Hover disabled must apply to its submenu too.
x,y=evaluate(projects+'.actor.get_transformed_position()')
move(int(x)+35,int(y)+10);time.sleep(.4)
assert evaluate(projects+'.menu.isOpen') is False
# Keyboard navigation opens the submenu and can return to the top menu.
evaluate(projects+'.actor.grab_key_focus(); true')
key('Right');wait_for(projects+'.menu.isOpen',bool)
key('Left');wait_for(projects+'.menu.isOpen',lambda x:x is False)
key('Escape');wait_for('global.drawer.menu.isOpen',lambda x:x is False)
configure(**{'open-on-hover':True})
move(600,300);move(20,740)
wait_for('global.drawer.menu.isOpen',bool)
wait_for(labels,lambda x:'Projects' in x)
print('PASS: hover off for root and submenus, click, keyboard Right, Left and Escape and hover on',flush=True)

# Check native Gio application dispatch with an isolated test handler.
handler=home/'record-open.py'
handler.write_text('from pathlib import Path\nimport sys\nwith (Path.home()/"opened.txt").open("a") as f: f.write(sys.argv[1]+"\\n")\n')
apps=home/'.local/share/applications';apps.mkdir(exist_ok=True)
(apps/'drawer-test.desktop').write_text('[Desktop Entry]\nType=Application\nName=Drawer test handler\nExec=/usr/bin/python3 '+str(handler)+' %u\nMimeType=text/plain;inode/directory;\nNoDisplay=true\n')
(home/'.config/mimeapps.list').write_text('[Default Applications]\ntext/plain=drawer-test.desktop;\ninode/directory=drawer-test.desktop;\n')
subprocess.run(['update-desktop-database',str(apps)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
fixture=home/'Desktop/Organized Desktop/Welcome.txt'
for target in [fixture, fixture.parent]:
    open_drawer()
    label='Welcome.txt' if target == fixture else 'Open folder'
    evaluate('global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='+json.dumps(label)+').actor.grab_key_focus(); true')
    key('Return')
    for _ in range(50):
        if (home/'opened.txt').exists() and (str(target) in (home/'opened.txt').read_text() or target.as_uri() in (home/'opened.txt').read_text()): break
        time.sleep(.1)
    else: raise AssertionError('Default handler did not receive '+str(target))
print('PASS: keyboard Enter launches a file and a folder through Gio (isolated test handler)',flush=True)

# A real failed launch should surface the applet's recovery notification.
evaluate('global.drawer._openPath('+json.dumps(str(home/'does-not-exist.txt'))+'); true')
notification="imports.ui.main.messageTray._notification"
wait_for(notification+" && "+notification+".title",lambda x:x=='Could not open this item')
screenshot('opening-error',"(()=>{let a=imports.ui.main.messageTray._notification.actor;let p=a.get_transformed_position();let s=a.get_transformed_size();return [p[0],p[1],s[0],s[1]]})()")
evaluate(notification+'.destroy(); true')
print('PASS: a real failed launch displays recovery guidance without a filename',flush=True)

# Exercise removal with a non-default folder, then verify retained settings.
configure(folder=str(home/'Desktop/Organized Desktop/Reading'))
open_drawer()
evaluate("global.settings.set_strv('enabled-applets',[]); true")
wait_for(get_drawer+' === null',bool)
evaluate(f"global.settings.set_strv('enabled-applets',['panel1:left:0:{UUID}:0']); true")
wait_for('Boolean('+get_drawer+')',bool)
evaluate('global.drawer='+get_drawer+'; true')
assert 'Weekend reading.txt' in open_drawer()
assert evaluate('global.drawer.folder') == str(home/'Desktop/Organized Desktop/Reading')
print('PASS: remove and re-add retain the selected folder and clean up menus',flush=True)
configure(folder='')

# Actual Cinnamon theme swap, without image recolouring.
evaluate("imports.gi.Gio.Settings.new('org.cinnamon.theme').set_string('name','Mint-Y'); true")
time.sleep(.6)
open_drawer();evaluate(projects+'.menu.open(true); true')
wait_for(nested,lambda x:'Release checklist.txt' in x)
screenshot('drawer-light')

# Open settings through the shipped Choose folder action.
move(700,200)
evaluate("global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='Choose folder').activate(); true")
windows="global.get_window_actors().map(a=>a.meta_window.get_title())"
wait_for(windows,lambda x:any('Desktop Drawer' in t for t in x))
evaluate("global.drawer.menu.close(); global.get_window_actors().find(a=>a.meta_window.get_title().includes('Desktop Drawer')).meta_window.move_resize_frame(true,150,120,800,460); true")
screenshot('settings',"(()=>{let w=global.get_window_actors().find(a=>a.meta_window.get_title().includes('Desktop Drawer')).meta_window;let r=w.get_frame_rect();return [r.x,r.y,r.width,r.height]})()")
print('PASS: Choose folder opens the real Cinnamon settings window',flush=True)
if args.screenshots:
    source=Path(__file__).resolve().parents[2]/'desktop/applet'/UUID
    manifest={'version':json.loads((source/'metadata.json').read_text())['version'],
              'cinnamon':subprocess.check_output(['cinnamon','--version'],text=True).strip(),
              'capture':'Actual Cinnamon X11 on Xvfb. Synthetic files. No image generation or compositing.',
              'source_sha256':{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file() and p.suffix in ('.js','.json','.css','.svg')},
              'screenshots':manifest}
    (args.screenshots/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
d.close()
