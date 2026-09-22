#!/usr/bin/env python3
"""Check release metadata and run behaviour tests without touching the desktop."""
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
APPLET = ROOT / 'desktop/applet/desktop-drawer@linux-automations'
metadata = json.loads((APPLET / 'metadata.json').read_text())
assert metadata['uuid'] == APPLET.name
assert metadata['max-instances'] == 1
assert not {'icon', 'dangerous', 'last-edited'} & metadata.keys()
schema = json.loads((APPLET / 'settings-schema.json').read_text())
assert schema['folder']['select-dir'] is True
assert schema['open-on-hover']['default'] is True
ET.parse(APPLET / 'icons/desktop-vault.svg')
subprocess.run(['node', str(ROOT / 'tests/desktop-drawer-behaviour.js')], check=True)
print('PASS: Desktop Drawer release metadata, settings and SVG')
