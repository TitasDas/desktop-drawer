#!/usr/bin/env python3
"""Verify a release, then rebuild its source archive to check reproducibility."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import zipfile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('release',type=Path)
args=parser.parse_args()
release=args.release.resolve()
manifest=json.loads((release/'release-manifest.json').read_text())
version=manifest['version'];uuid=manifest['uuid']
for name,expected in manifest['artifacts'].items():
    assert Path(name).name==name
    assert hashlib.sha256((release/name).read_bytes()).hexdigest()==expected,name
with zipfile.ZipFile(release/f'desktop-drawer-{version}.zip') as archive:
    assert archive.testzip() is None
    files={}
    for name in archive.namelist():
        path=Path(name)
        assert not path.is_absolute() and '..' not in path.parts and path.parts[0]==uuid
        assert '.git' not in path.parts and path.suffix not in ('.mo','.pyc')
        relative=path.relative_to(uuid).as_posix()
        data=archive.read(name)
        assert data==(release/uuid/'files'/uuid/relative).read_bytes(),name
        files[relative]=hashlib.sha256(data).hexdigest()
    assert files==manifest['runtime_sha256']
    assert b'GPL-3.0-or-later' in archive.read(uuid+'/COPYING.md')
    assert b'GNU GENERAL PUBLIC LICENSE' in archive.read(uuid+'/LICENSE')
print('PASS: archive integrity, paths, full licence, checksum and submission/source equality')
with tempfile.TemporaryDirectory(prefix='drawer-package-verification-') as tmp:
    root=Path(tmp)
    with tarfile.open(release/f'desktop-drawer-{version}-source.tar.gz') as archive:
        for member in archive.getmembers():
            path=Path(member.name)
            assert member.isfile() and not path.is_absolute() and '..' not in path.parts
            assert '.git' not in path.parts and path.parts[0]==f'desktop-drawer-{version}'
        archive.extractall(root)
    source=root/f'desktop-drawer-{version}'
    subprocess.run([sys.executable,'tests/desktop-drawer-test.py'],cwd=source,check=True)
    rebuilt=root/'rebuilt'
    subprocess.run([sys.executable,'packaging/desktop-drawer/build.py',str(rebuilt)],cwd=source,check=True)
    for name in manifest['artifacts']:
        assert (release/name).read_bytes()==(rebuilt/name).read_bytes(),f'Not reproducible: {name}'
print('PASS: extracted source tests and byte-identical rebuilt ZIP and source archive')
