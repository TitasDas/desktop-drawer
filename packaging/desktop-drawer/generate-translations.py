#!/usr/bin/env python3
"""Extract applet, metadata and settings strings with Cinnamon's own tool."""
from pathlib import Path
import json
import os
import subprocess
import polib

ROOT=Path(__file__).resolve().parents[2]
UUID='desktop-drawer@linux-automations'
source=ROOT/'desktop/applet'/UUID
output=source/'po'/f'{UUID}.pot'
output.parent.mkdir(exist_ok=True)
# A fresh extraction removes obsolete UI strings from older releases.
output.unlink(missing_ok=True)
result=subprocess.run(['cinnamon-xlet-makepot','-o',str(output),'.'],cwd=source,check=True)
if not output.exists(): raise SystemExit('Translation extraction did not produce a template')
po=polib.pofile(str(output))
po.header='Desktop Drawer\nCopyright (C) 2026 TitasDas\nSPDX-License-Identifier: GPL-3.0-or-later\nDistributed under the same licence as Desktop Drawer.'
po.metadata['Project-Id-Version']='Desktop Drawer '+json.loads((source/'metadata.json').read_text())['version']
po.metadata['Report-Msgid-Bugs-To']='https://github.com/linuxmint/cinnamon-spices-applets/issues'
po.metadata['Content-Type']='text/plain; charset=UTF-8'
po.save(str(output))
print(f'Extracted {len(po)} messages to {output.relative_to(ROOT)}')
