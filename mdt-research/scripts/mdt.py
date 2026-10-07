#!/usr/bin/env python3
"""List review roles, read method cards, and assemble offline prompt packets (Python 3.9+)."""

import argparse
import json
import sys
import unicodedata
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold())
                   if c.isalnum())


def resolve_names(names, roles):
    selected = []
    for name in names:
        key = normalized(name)
        matches = [p for p in roles if key in {
            normalized(x) for x in [p['slug'], p['name'], *p['aliases']]}]
        if len(matches) != 1:
            raise ValueError('无法唯一匹配职能：' + name + '；用 list 查看精确 slug。')
        if matches[0]['slug'] not in [p['slug'] for p in selected]:
            selected.append(matches[0])
    return selected


def read_card(role):
    path = SKILL / role['path']
    if not path.resolve().is_relative_to(SKILL.resolve()):
        raise ValueError('方法卡路径超出 skill 目录。')
    return path.read_text(encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    ls = sub.add_parser('list', help='列出职能、类别与推理焦点')
    ls.add_argument('--category', choices=['domain', 'evidence', 'design', 'data', 'translation', 'governance'])
    ls.add_argument('--json', action='store_true', help='机器可读的名单')
    show = sub.add_parser('show', help='读取指定职能卡片；接受 slug、全名与中文别名')
    show.add_argument('members', nargs='+')
    panel = sub.add_parser('panel', help='生成提示包；不调用模型、不访问网络')
    group = panel.add_mutually_exclusive_group(required=True)
    group.add_argument('--members', nargs='+', help='明确指定成员与顺序')
    group.add_argument('--preset', choices=['default', 'quick', 'biomed', 'ai', 'engineering', 'deep'])
    panel.add_argument('--question', required=True, help='原始问题')
    panel.add_argument('--rounds', type=int, choices=[1, 2], default=1)
    panel.add_argument('--offline', action='store_true', help='明确禁止检索，依用户材料工作')
    panel.add_argument('--output', type=Path, help='保存提示包；已有文件不会覆盖')
    args = parser.parse_args()
    try:
        data = json.loads((SKILL / 'references/catalog.json').read_text(encoding='utf-8'))
        roles = data['roles']
        if args.command == 'list':
            selected = [p for p in roles if not args.category or p['category'] == args.category]
            if args.json:
                print(json.dumps(selected, ensure_ascii=False, indent=2))
            else:
                print('\n'.join(f"{p['slug']} | {p['chinese']} · {p['name']} | {p['category_label']} | {p['focus']}" for p in selected))
            return 0
        if args.command == 'show':
            print('\n\n---\n\n'.join(read_card(p) for p in resolve_names(args.members, roles)))
            return 0
        if not args.question.strip():
            raise ValueError('研究问题不能为空。')
        names = args.members if args.members else data['presets'][args.preset]
        selected = resolve_names(names, roles)
        parts = ['# MDT 研究评议提示包',
                 '本文件是本地组装的指令与角色参考，尚未执行模型评议或核验研究事实。',
                 '## 任务参数',
                 f'职能：{len(selected)} 个；轮次：{args.rounds}；离线：{args.offline}。',
                 '本次任务的职能名单与参数优先于技能默认规模。读完参考后执行评议。',
                 '## 用户问题', args.question,
                 '## 本次名单', '\n'.join(f"- {p['slug']} · {p['chinese']} · {p['name']}" for p in selected),
                 '## 工作流', (SKILL/'SKILL.md').read_text(encoding='utf-8')]
        parts += ['## 角色参考（按本次顺序）']
        parts += [read_card(p) for p in selected]
        output = '\n\n'.join(parts) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as handle:
                handle.write(output)
            print('提示包已保存：' + str(args.output.resolve()))
        else:
            print(output)
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print('错误：' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
