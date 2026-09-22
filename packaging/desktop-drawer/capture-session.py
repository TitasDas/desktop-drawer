#!/usr/bin/env python3
"""Run tests and capture actual Cinnamon screens in a disposable desktop.
Requires Cinnamon, Xvfb, dbus-run-session, python3-xlib and python3-pil.
Run with /usr/bin/python3, which has the distribution's desktop bindings.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
UUID = 'desktop-drawer@linux-automations'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--demo', action='store_true', help='record a short real Cinnamon demonstration')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    number = next(n for n in range(91, 120) if not Path(f'/tmp/.X11-unix/X{n}').exists() and not Path(f'/tmp/.X{n}-lock').exists())
    processes = []
    with tempfile.TemporaryDirectory(prefix='desktop-drawer-capture-') as tmp:
        home = Path(tmp)
        (home / '.isolated-cinnamon').touch()
        for name in ('.config', '.local/share/cinnamon/applets', '.cache', 'runtime', 'Desktop/Organized Desktop/Projects/Private', 'Desktop/Organized Desktop/Reading', 'Desktop/Organized Desktop/Private', 'empty'):
            (home / name).mkdir(parents=True, exist_ok=True)
        (home / 'runtime').chmod(0o700)
        (home / '.config/user-dirs.dirs').write_text('XDG_DESKTOP_DIR="$HOME/Desktop"\n')
        for name in ('Projects/Release checklist.txt', 'Reading/Weekend reading.txt', 'Welcome.txt', 'Private/HIDDEN-DEMO.txt', 'Projects/Private/SECRET-NESTED.txt'):
            (home / 'Desktop/Organized Desktop' / name).write_text('Synthetic demonstration file for Desktop Drawer.\n')
        shutil.copytree(ROOT / 'desktop/applet' / UUID, home / '.local/share/cinnamon/applets' / UUID)
        env = os.environ.copy()
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'), XDG_DATA_HOME=str(home / '.local/share'),
                   XDG_CACHE_HOME=str(home / '.cache'), XDG_RUNTIME_DIR=str(home / 'runtime'), DISPLAY=f':{number}',
                   GSETTINGS_BACKEND='keyfile', NO_AT_BRIDGE='1')
        for key in ('SESSION_MANAGER', 'DBUS_SESSION_BUS_ADDRESS', 'XAUTHORITY'):
            env.pop(key, None)
        bootstrap = home / 'start.py'
        bootstrap.write_text('''import json, os, subprocess
from pathlib import Path
home=Path.home()
(home/'session.json').write_text(json.dumps({'pid':os.getpid(),'bus':os.environ['DBUS_SESSION_BUS_ADDRESS']}))
settings=[('org.cinnamon','panels-enabled',"['1:0:bottom']"),('org.cinnamon','enabled-applets',"['panel1:left:0:desktop-drawer@linux-automations:0']"),('org.cinnamon','next-applet-id','1'),('org.cinnamon.theme','name',"'Mint-Y-Dark-Aqua'")]
for schema,key,value in settings: subprocess.run(['gsettings','set',schema,key,value],check=True)
os.execvp('cinnamon',['cinnamon','--replace','--sm-disable'])
''')
        with (output / 'session.log').open('w') as log:
            try:
                xvfb = subprocess.Popen(['Xvfb',f':{number}','-screen','0','1100x760x24','-nolisten','tcp'],stdout=log,stderr=log,start_new_session=True)
                processes.append(xvfb)
                for _ in range(50):
                    if Path(f'/tmp/.X11-unix/X{number}').exists(): break
                    time.sleep(.1)
                session = subprocess.Popen(['dbus-run-session','--',sys.executable,str(bootstrap)],env=env,stdout=log,stderr=log,start_new_session=True)
                processes.append(session)
                for _ in range(150):
                    if (home / 'session.json').exists(): break
                    if session.poll() is not None: raise RuntimeError('Cinnamon session failed; see session.log')
                    time.sleep(.1)
                state=json.loads((home/'session.json').read_text())
                run=subprocess.run([sys.executable,str(ROOT/'packaging/desktop-drawer/smoke-session.py'),str(state['pid']),'--screenshots',str(output)],capture_output=True,text=True,timeout=120)
                (output/'test-results.txt').write_text(run.stdout+run.stderr)
                print(run.stdout+run.stderr,end='')
                run.check_returncode()
                if output == ROOT / 'packaging/desktop-drawer/screenshots':
                    shutil.copyfile(output/'drawer-dark.png', output.parent/'screenshot.png')
                if args.demo:
                    subprocess.run([sys.executable,str(ROOT/'packaging/desktop-drawer/record-demo.py'),str(state['pid']),str(ROOT/'docs/media')],check=True,timeout=90)
                print(f'Screenshots and test evidence: {output}')
            finally:
                for process in reversed(processes):
                    if process.poll() is None:
                        os.killpg(process.pid,signal.SIGTERM)
                        try: process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid,signal.SIGKILL)
                            process.wait()

if __name__ == '__main__': main()
