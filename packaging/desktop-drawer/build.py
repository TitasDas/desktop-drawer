#!/usr/bin/env python3
"""Build licensed, reproducible Desktop Drawer packages from reviewed inputs."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile
import zipfile

ROOT=Path(__file__).resolve().parents[2]
UUID='desktop-drawer@linux-automations'
SOURCE=ROOT/'desktop/applet'/UUID
MATERIAL=ROOT/'packaging/desktop-drawer'
DOCS=('README.md','BETA-CHECKLIST.md','CHANGELOG.md')
TOOLS=('build.py','verify.py','capture-session.py','smoke-session.py','generate-translations.py','record-demo.py')
REVIEW=('SUBMISSION.md','VALIDATION.md','PRODUCT-REVIEW.md','BUILD.md','SCREENSHOTS.md')

def digest(data): return hashlib.sha256(data).hexdigest()

def file_bytes(path):
    if path.is_symlink() or not path.is_file(): raise ValueError(f'Expected a regular file: {path}')
    return path.read_bytes()

def inputs():
    runtime={}
    for name in ('applet.js','metadata.json','settings-schema.json','stylesheet.css','icon.png','LICENSE','COPYING.md'):
        runtime[name]=file_bytes(SOURCE/name)
    for folder in ('icons','po'):
        for path in sorted((SOURCE/folder).rglob('*')):
            if path.is_file():
                if path.suffix not in ('.svg','.pot','.po'): raise ValueError(f'Unexpected source asset: {path}')
                runtime[path.relative_to(SOURCE).as_posix()]=file_bytes(path)
    if b'GPL-3.0-or-later' not in runtime['COPYING.md'] or b'GNU GENERAL PUBLIC LICENSE' not in runtime['LICENSE']:
        raise ValueError('Full GPL text and explicit or-later grant are required')
    version=json.loads(runtime['metadata.json'])['version']
    evidence=json.loads(file_bytes(MATERIAL/'screenshots/manifest.json'))
    if evidence['version']!=version: raise ValueError('Capture screenshots for this version before building')
    core={name:digest(data) for name,data in runtime.items() if Path(name).suffix in ('.js','.json','.css','.svg')}
    if core!=evidence['source_sha256']: raise ValueError('Screenshots do not match the current applet source')
    images={}
    for image in evidence['screenshots'].values():
        name=image['file']
        if Path(name).name!=name: raise ValueError('Invalid screenshot filename')
        data=file_bytes(MATERIAL/'screenshots'/name)
        if digest(data)!=image['sha256']: raise ValueError(f'Screenshot changed after capture: {name}')
        images[name]=data
    if file_bytes(MATERIAL/'screenshot.png') != images['drawer-dark.png']:
        raise ValueError('Catalogue image differs from the captured dark screenshot')
    for name in DOCS: runtime[name]=file_bytes(MATERIAL/name)
    runtime['screenshot.png']=images['drawer-dark.png']
    return runtime,images,version

def write_zip(path,files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(files.items()):
            item=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
            item.create_system=3
            item.external_attr=0o100644<<16
            item.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(item,data)

def write_tar(path,files):
    with path.open('wb') as stream, gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w',format=tarfile.PAX_FORMAT) as archive:
            for name,data in sorted(files.items()):
                entry=tarfile.TarInfo(name)
                entry.size=len(data);entry.mode=0o644;entry.mtime=0
                archive.addfile(entry,io.BytesIO(data))

def build(destination):
    runtime,images,version=inputs()
    if destination.exists(): raise ValueError('Use a new output directory; release files are never overwritten')
    # Preflight every source-package input before writing an artifact.
    source_files={f'desktop/applet/{UUID}/{name}':data for name,data in runtime.items()
                  if name not in DOCS and name!='screenshot.png'}
    for name in (*DOCS,*TOOLS,*REVIEW):
        source_files[f'packaging/desktop-drawer/{name}']=file_bytes(MATERIAL/name)
    for name in ('desktop-drawer-test.py','desktop-drawer-behaviour.js'):
        source_files[f'tests/{name}']=file_bytes(ROOT/'tests'/name)
    for name,data in images.items(): source_files[f'packaging/desktop-drawer/screenshots/{name}']=data
    for name in ('manifest.json','test-results.txt'):
        source_files[f'packaging/desktop-drawer/screenshots/{name}']=file_bytes(MATERIAL/'screenshots'/name)
    source_files['packaging/desktop-drawer/screenshot.png']=images['drawer-dark.png']
    source_files['README.md']=file_bytes(MATERIAL/'BUILD.md')
    source_files['LICENSE']=runtime['LICENSE']
    source_files['COPYING.md']=runtime['COPYING.md']
    destination.mkdir(parents=True)
    spice=destination/UUID
    for name,data in runtime.items():
        path=spice/'files'/UUID/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    (spice/'README.md').write_bytes(runtime['README.md'])
    (spice/'info.json').write_text(json.dumps({'author':'TitasDas'},indent=2)+'\n')
    (spice/'screenshot.png').write_bytes(images['drawer-dark.png'])
    for name,data in images.items():
        path=spice/'screenshots'/name;path.parent.mkdir(exist_ok=True);path.write_bytes(data)
    bundle=destination/f'desktop-drawer-{version}.zip'
    source=destination/f'desktop-drawer-{version}-source.tar.gz'
    write_zip(bundle,{f'{UUID}/{name}':data for name,data in runtime.items()})
    write_tar(source,{f'desktop-drawer-{version}/{name}':data for name,data in source_files.items()})
    checksums=''.join(f'{digest(p.read_bytes())}  {p.name}\n' for p in (bundle,source))
    (destination/'SHA256SUMS').write_text(checksums)
    for p in (bundle,source): p.with_name(p.name+'.sha256').write_text(f'{digest(p.read_bytes())}  {p.name}\n')
    (destination/'release-manifest.json').write_text(json.dumps({
        'version':version,'licence':'GPL-3.0-or-later','uuid':UUID,
        'runtime_sha256':{n:digest(data) for n,data in sorted(runtime.items())},
        'artifacts':{p.name:digest(p.read_bytes()) for p in (bundle,source)}},indent=2)+'\n')
    print(f'Spices submission: {spice}\nInstallation ZIP: {bundle}\nSource archive: {source}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    try: build(args.destination.resolve())
    except (OSError,ValueError,KeyError) as error: parser.exit(1,f'Build failed: {error}\n')
