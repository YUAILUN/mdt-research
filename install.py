#!/usr/bin/env python3
"""Install the bundled skill for Codex, Antigravity, and Claude Code (Python 3.9+, no network)."""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

KIT = Path(__file__).resolve().parent
NAME = 'mdt-research'


def inventory(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink():
            raise ValueError('不自动安装或覆盖包含符号链接的目录：' + str(path))
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def destinations(args):
    groups = {'both': ['codex', 'antigravity'],
              'all': ['codex', 'antigravity', 'claude-code']}
    targets = groups.get(args.target, [args.target])
    if args.workspace:
        if args.codex_root or args.antigravity_root or args.claude_root:
            raise ValueError('--workspace 不能与全局目录覆盖选项一起使用。')
        workspace = args.workspace.expanduser().resolve()
        return list(dict.fromkeys(workspace / ('.claude' if target == 'claude-code' else '.agents') / 'skills' / NAME for target in targets))
    home = args.home_dir.expanduser().resolve()
    roots = {
        'codex': args.codex_root or home / '.agents' / 'skills',
        'antigravity': args.antigravity_root or home / '.gemini' / 'config' / 'skills',
        'antigravity-cli': args.antigravity_root or home / '.gemini' / 'antigravity-cli' / 'skills',
        'claude-code': args.claude_root or home / '.claude' / 'skills',
    }
    return list(dict.fromkeys(roots[target].expanduser().resolve() / NAME for target in targets))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['codex', 'antigravity', 'antigravity-cli', 'claude-code', 'both', 'all'], default='both')
    parser.add_argument('--workspace', type=Path, help='项目安装：Codex/Antigravity 用 .agents/skills，Claude Code 用 .claude/skills')
    parser.add_argument('--codex-root', type=Path, help='覆盖 Codex 全局 skills 根目录')
    parser.add_argument('--antigravity-root', type=Path, help='覆盖 Antigravity 全局 skills 根目录；旧 IDE 可用 ~/.gemini/antigravity/skills')
    parser.add_argument('--claude-root', type=Path, help='覆盖 Claude Code 全局 skills 根目录')
    parser.add_argument('--home-dir', type=Path, default=Path.home(), help='为隔离测试或另一用户指定主目录')
    parser.add_argument('--dry-run', action='store_true', help='只检查并显示目标，不写入目录')
    parser.add_argument('--replace', action='store_true', help='新版本替换已有不同内容，旧目录先保留为备份')
    args = parser.parse_args()
    try:
        source = KIT / NAME
        if not (source / 'SKILL.md').is_file():
            raise ValueError('未找到随包的 SKILL.md；请完整解压安装包。')
        expected = json.loads((KIT / 'package-manifest.json').read_text(encoding='utf-8'))['skill_files_sha256']
        if inventory(source) != expected:
            raise ValueError('源文件与安装包清单不一致。请使用完整安装包；修改 skill 后应手动复制。')
        targets = destinations(args)
        plan = []
        for dest in targets:
            if dest == source.resolve() or source.resolve().is_relative_to(dest) or dest.is_relative_to(source.resolve()):
                raise ValueError('安装目标与源目录重叠：' + str(dest))
            if dest.is_symlink() or (dest.exists() and not dest.is_dir()):
                raise ValueError('目标不是可安全替换的普通目录：' + str(dest))
            same = dest.exists() and inventory(dest) == expected
            if dest.exists() and not same and not args.replace:
                raise ValueError('已有不同版本：' + str(dest) + '；要保留备份后更新，请加 --replace。')
            plan.append((dest, same))
        for dest, same in plan:
            if same:
                print('已安装相同内容：' + str(dest))
                continue
            if args.dry_run:
                print('计划安装：' + str(dest) + ('（现有内容将保留备份）' if dest.exists() else ''))
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix='.mdt-install-', dir=dest.parent))
            backup = None
            try:
                shutil.copytree(source, staging, dirs_exist_ok=True)
                if inventory(staging) != expected:
                    raise ValueError('复制后校验失败。')
                if dest.exists():
                    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                    # Backup is a sibling of skills/, so hosts will not discover a duplicate skill.
                    backup_root = dest.parent.parent / 'skill-backups'
                    backup_root.mkdir(parents=True, exist_ok=True)
                    backup = backup_root / f'{NAME}.{stamp}.{uuid.uuid4().hex[:8]}'
                    os.replace(dest, backup)
                os.replace(staging, dest)
                print('已安装：' + str(dest))
                if backup: print('旧版本备份：' + str(backup))
            except Exception:
                if backup and backup.exists() and not dest.exists():
                    os.replace(backup, dest)
                raise
            finally:
                if staging.exists(): shutil.rmtree(staging)
        if not args.dry_run:
            print('在新聊天中调用 mdt-research；未显示时重新加载或重启宿主。')
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print('安装未完成：' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
