#!/usr/bin/env python3
"""Refresh the local manifest and build a distributable ZIP with no dependencies."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-only', action='store_true')
    args = parser.parse_args()
    skill = ROOT/'mdt-research'
    inventory = {p.relative_to(skill).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(skill.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    version = next(line.split('"')[1] for line in (skill/'SKILL.md').read_text(encoding='utf-8').splitlines() if line.strip().startswith('version:'))
    manifest = dict(skill='mdt-research', version=version, built_date='2026-10-07', skill_files_sha256=inventory)
    (ROOT/'package-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(f'Manifest: {len(inventory)} skill files, version {version}')
    if args.manifest_only: return
    output=ROOT/'dist'; output.mkdir(exist_ok=True)
    archive_path=output/f'mdt-research-kit-v{version}.zip'
    allowed=['mdt-research','scripts','tests','.github']
    root_files=['install.py','package-manifest.json','LICENSE','README.md','README.en.md','安装与使用.md','示例评议.md','验证记录.md','.gitignore']
    files=[ROOT/f for f in root_files if (ROOT/f).is_file()]
    for directory in allowed:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files): archive.write(path,'mdt-research-kit/'+path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for path, checksum in inventory.items():
            assert hashlib.sha256(archive.read('mdt-research-kit/mdt-research/'+path)).hexdigest()==checksum
    checksum=hashlib.sha256(archive_path.read_bytes()).hexdigest()
    (output/'SHA256SUMS').write_text(checksum+'  '+archive_path.name+'\n',encoding='utf-8')
    print('Built '+str(archive_path))


if __name__=='__main__': main()
