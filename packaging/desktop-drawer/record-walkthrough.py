#!/usr/bin/env python3
"""Record the walkthrough footage in a disposable Cinnamon session.

Like capture-session.py, this builds a throwaway home with synthetic files and
runs Cinnamon on its own Xvfb display. It then drives the applet (hover, submenus,
keyboard, settings, light theme) while ffmpeg records the whole 1280x960 desktop,
and writes events.json with the time of each step so the editor can caption it.
Requires Cinnamon, Xvfb, dbus-run-session, ffmpeg, python3-xlib. Run with /usr/bin/python3.
"""
import argparse, ast, json, os, shutil, signal, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UUID = 'desktop-drawer@linux-automations'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wallpaper', type=Path, required=True, help='1280x960 image shown as the desktop background')
    args = parser.parse_args()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    wallpaper = args.wallpaper.resolve()
    number = next(n for n in range(91, 120) if not Path(f'/tmp/.X11-unix/X{n}').exists() and not Path(f'/tmp/.X{n}-lock').exists())
    processes = []
    tmp = tempfile.mkdtemp(prefix='desktop-drawer-capture-')
    try:
        home = Path(tmp)
        (home / '.isolated-cinnamon').touch()
        for name in ('.config', '.local/share/cinnamon/applets', '.cache', 'runtime',
                     'Desktop/Organized Desktop/Projects/Private', 'Desktop/Organized Desktop/Reading', 'Desktop/Organized Desktop/Private'):
            (home / name).mkdir(parents=True, exist_ok=True)
        (home / 'runtime').chmod(0o700)
        (home / '.config/user-dirs.dirs').write_text('XDG_DESKTOP_DIR="$HOME/Desktop"\n')
        for name in ('Projects/Release checklist.txt', 'Projects/Talk outline.txt', 'Reading/Weekend reading.txt',
                     'Reading/Paper notes.txt', 'Welcome.txt', 'Private/HIDDEN-DEMO.txt', 'Projects/Private/SECRET-NESTED.txt'):
            (home / 'Desktop/Organized Desktop' / name).write_text('Synthetic demonstration file for Desktop Drawer.\n')
        shutil.copytree(ROOT / 'desktop/applet' / UUID, home / '.local/share/cinnamon/applets' / UUID)
        env = os.environ.copy()
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'), XDG_DATA_HOME=str(home / '.local/share'),
                   XDG_CACHE_HOME=str(home / '.cache'), XDG_RUNTIME_DIR=str(home / 'runtime'), DISPLAY=f':{number}',
                   GSETTINGS_BACKEND='keyfile', NO_AT_BRIDGE='1')
        for key in ('SESSION_MANAGER', 'DBUS_SESSION_BUS_ADDRESS', 'XAUTHORITY'):
            env.pop(key, None)
        bootstrap = home / 'start.py'
        bootstrap.write_text(f'''import json, os, subprocess
from pathlib import Path
home=Path.home()
(home/'session.json').write_text(json.dumps({{'pid':os.getpid(),'bus':os.environ['DBUS_SESSION_BUS_ADDRESS']}}))
settings=[('org.cinnamon','panels-enabled',"['1:0:bottom']"),('org.cinnamon','enabled-applets',"['panel1:left:0:{UUID}:0']"),('org.cinnamon','next-applet-id','1'),
 ('org.cinnamon.theme','name',"'Mint-Y-Dark-Aqua'"),('org.cinnamon.desktop.background','picture-uri',"'file://{wallpaper}'"),('org.cinnamon.desktop.background','picture-options',"'zoom'"),
 ('org.gnome.desktop.background','picture-uri',"'file://{wallpaper}'"),('org.gnome.desktop.background','picture-options',"'zoom'"),
 ('org.cinnamon.desktop.interface','gtk-theme',"'Mint-Y-Dark-Aqua'"),('org.cinnamon.desktop.interface','icon-theme',"'Mint-Y-Aqua'")]
for schema,key,value in settings: subprocess.run(['gsettings','set',schema,key,value],check=True)
os.execvp('cinnamon',['cinnamon','--replace','--sm-disable'])
''')
        with (output / 'session.log').open('w') as log:
            try:
                xvfb = subprocess.Popen(['Xvfb', f':{number}', '-screen', '0', '1280x960x24', '-nolisten', 'tcp'], stdout=log, stderr=log, start_new_session=True)
                processes.append(xvfb)
                for _ in range(50):
                    if Path(f'/tmp/.X11-unix/X{number}').exists(): break
                    time.sleep(.1)
                session = subprocess.Popen(['dbus-run-session', '--', sys.executable, str(bootstrap)], env=env, stdout=log, stderr=log, start_new_session=True)
                processes.append(session)
                for _ in range(150):
                    if (home / 'session.json').exists(): break
                    if session.poll() is not None: raise RuntimeError('Cinnamon session failed; see session.log')
                    time.sleep(.1)
                state = json.loads((home / 'session.json').read_text())
                # Cinnamon only tracks the wallpaper setting; csd-background paints it.
                senv = env | {'DBUS_SESSION_BUS_ADDRESS': state['bus']}
                if shutil.which('csd-background'):
                    processes.append(subprocess.Popen(['csd-background'], env=senv, stdout=log, stderr=log, start_new_session=True))
                    time.sleep(2.0)
                record(state['pid'], output)
            finally:
                for process in reversed(processes):
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGTERM)
    finally:
        # gvfs may leave a mount under the throwaway home; never let cleanup fail the run
        time.sleep(0.5)
        shutil.rmtree(tmp, ignore_errors=True)


def record(pid, output):
    from Xlib import X, XK, display
    from Xlib.ext import xtest
    proc = dict(e.decode().split('=', 1) for e in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0') if b'=' in e)
    home = Path(proc['HOME']); assert home.parent == Path('/tmp') and home.name.startswith('desktop-drawer-capture-') and (home / '.isolated-cinnamon').exists()
    env = os.environ | {'DBUS_SESSION_BUS_ADDRESS': proc['DBUS_SESSION_BUS_ADDRESS']}

    def evaluate(code):
        s = subprocess.check_output(['gdbus', 'call', '--session', '--dest', 'org.Cinnamon', '--object-path', '/org/Cinnamon', '--method', 'org.Cinnamon.Eval', code], env=env, text=True, stderr=subprocess.DEVNULL).strip()
        assert s.startswith('(true, '), s
        return json.loads(ast.literal_eval(s[7:-1]))

    def wait_for(code, check, tries=150):
        for _ in range(tries):
            try:
                r = evaluate(code)
                if check(r): return r
            except (subprocess.CalledProcessError, AssertionError): pass
            time.sleep(.1)
        raise AssertionError('Timed out: ' + code)

    get_drawer = f"imports.ui.appletManager.get_object_for_uuid('{UUID}','0')"
    wait_for(f'Boolean({get_drawer})', bool)
    evaluate(f'global.drawer={get_drawer}; true')
    time.sleep(2.5)  # let the panel and background settle
    d = display.Display(proc['DISPLAY'])
    events = []
    t0 = None

    def mark(name):
        events.append({'name': name, 't': round(time.monotonic() - t0, 3)})

    def move(x, y, steps=18, dur=0.5):
        cur = d.screen().root.query_pointer()
        sx, sy = cur.root_x, cur.root_y
        for i in range(1, steps + 1):
            u = i / steps; e = u * u * (3 - 2 * u)
            xtest.fake_input(d, X.MotionNotify, x=int(sx + (x - sx) * e), y=int(sy + (y - sy) * e)); d.sync(); time.sleep(dur / steps)

    def click():
        xtest.fake_input(d, X.ButtonPress, 1); xtest.fake_input(d, X.ButtonRelease, 1); d.sync()

    def key(name):
        code = d.keysym_to_keycode(XK.string_to_keysym(name))
        xtest.fake_input(d, X.KeyPress, code); xtest.fake_input(d, X.KeyRelease, code); d.sync()

    def item_pos(label):
        return evaluate('(()=>{let i=global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text===' + json.dumps(label) + '); let p=i.actor.get_transformed_position(); let s=i.actor.get_transformed_size(); return [p[0],p[1],s[0],s[1]]})()')

    def hover_item(label, dwell=1.6):
        x, y, w, h = item_pos(label); move(x + min(80, w / 2), y + h / 2); time.sleep(dwell)

    ap = evaluate('(()=>{let p=global.drawer.actor.get_transformed_position(); let s=global.drawer.actor.get_transformed_size(); return [p[0],p[1],s[0],s[1]]})()')
    icon = (ap[0] + ap[2] / 2, ap[1] + ap[3] / 2)
    evaluate('global.drawer.menu.close(); true')
    xtest.fake_input(d, X.MotionNotify, x=640, y=420); d.sync(); time.sleep(.5)

    mp4 = output / 'footage.mp4'
    rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '25', '-video_size', '1280x960', '-i', proc['DISPLAY'] + '+0,0', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', str(mp4)], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    t0 = time.monotonic()
    try:
        time.sleep(1.2); mark('desktop')
        move(icon[0], icon[1], dur=0.9); mark('hover-icon')
        wait_for('global.drawer.menu.isOpen', bool); time.sleep(1.4); mark('menu-open')
        hover_item('Projects', 1.8); mark('projects')
        evaluate("global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='Projects').menu.close(); true"); time.sleep(.3)
        hover_item('Reading', 1.8); mark('reading')
        evaluate("global.drawer.menu._getMenuItems().find(i=>i.label && i.label.text==='Reading').menu.close(); true"); time.sleep(.4)
        mark('keys')
        for _ in range(3):
            key('Down'); time.sleep(.55)
        key('Up'); time.sleep(.6)
        key('Escape'); time.sleep(.3); mark('escape')
        move(700, 380, dur=0.6); time.sleep(.9)
        move(icon[0], icon[1], dur=0.7); click(); mark('click-open')
        wait_for('global.drawer.menu.isOpen', bool); time.sleep(1.0)
        hover_item('Choose folder', 1.0); click(); mark('settings')
        wait_for("global.get_window_actors().some(a=>a.meta_window.get_title().includes('Desktop Drawer'))", bool, tries=80)
        time.sleep(3.0)
        evaluate("global.get_window_actors().filter(a=>a.meta_window.get_title().includes('Desktop Drawer')).forEach(a=>a.meta_window.delete(global.get_current_time())); true")
        time.sleep(.8); mark('settings-closed')
        evaluate("imports.gi.Gio.Settings.new('org.cinnamon.theme').set_string('name','Mint-Y-Aqua'); true")
        time.sleep(1.4); mark('light')
        move(640, 400, dur=0.4); move(icon[0], icon[1], dur=0.8)
        wait_for('global.drawer.menu.isOpen', bool); time.sleep(2.2); mark('light-menu')
        evaluate('global.drawer.menu.close(); true'); move(700, 420, dur=0.6); time.sleep(1.2); mark('end')
    finally:
        try:
            _, err = rec.communicate(b'q', timeout=15)
        except subprocess.TimeoutExpired:
            rec.kill(); rec.wait(); raise
        (output / 'events.json').write_text(json.dumps(events, indent=1))
        if rec.returncode: raise RuntimeError(err.decode())
    d.close()
    print('footage:', mp4, 'events:', len(events))


if __name__ == '__main__':
    main()
