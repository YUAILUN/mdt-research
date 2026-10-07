"""Functional tests in isolated directories; no network or host installation."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'mdt-research'
TOOL=SKILL/'scripts/mdt.py'


def digest(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.home=self.base/'home'
        self.data=json.loads((SKILL/'references/catalog.json').read_text(encoding='utf-8'))

    def run_script(self,script,*args,expected=0):
        result=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],text=True,capture_output=True,encoding='utf-8')
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        return result

    def install(self,*args,expected=0):
        return self.run_script(ROOT/'install.py','--home-dir',self.home,*args,expected=expected)

    def test_roles_and_all_cards(self):
        roles=self.data['roles']
        self.assertEqual(self.data['count'],12)
        self.assertEqual(len(roles),12)
        self.assertEqual(len({role['slug'] for role in roles}),12)
        for role in roles:
            self.assertTrue((SKILL/role['path']).is_file())
        self.assertEqual(len(self.data['presets']['deep']),12)
        self.assertEqual(set(self.data['presets']['deep']),{role['slug'] for role in roles})
        self.assertEqual(len(self.data['presets']['default']),6)

    def test_local_markdown_links(self):
        for path in SKILL.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if not link.startswith(('https://','http://','#')):
                    self.assertTrue((path.parent/link.split('#')[0]).exists(),f'{path}: {link}')

    def test_manifest(self):
        expected=json.loads((ROOT/'package-manifest.json').read_text(encoding='utf-8'))['skill_files_sha256']
        self.assertEqual(digest(SKILL),expected)

    def test_lists_aliases_and_errors(self):
        self.assertEqual(len(json.loads(self.run_script(TOOL,'list','--json').stdout)),12)
        expected=[role for role in self.data['roles'] if role['category']=='data']
        self.assertEqual(json.loads(self.run_script(TOOL,'list','--category','data','--json').stdout),expected)
        result=self.run_script(TOOL,'show','统计与不确定性','statistics','因果推断')
        self.assertEqual(result.stdout.count('# Statistics · 统计与不确定性'),1)
        self.run_script(TOOL,'show','../../SKILL.md',expected=2)
        self.run_script(TOOL,'panel','--preset','ai','--question',' ',expected=2)

    def test_presets_and_modes(self):
        for preset,slugs in self.data['presets'].items():
            result=self.run_script(TOOL,'panel','--preset',preset,'--question','如何验证泛化？')
            for slug in slugs:
                self.assertIn(f'- 职能标识：`{slug}`',result.stdout)
        result=self.run_script(TOOL,'panel','--members','统计与不确定性','因果推断','--question','研究问题','--rounds','2','--offline')
        self.assertIn('职能：2 个；轮次：2；离线：True',result.stdout)

    def test_output_is_not_overwritten(self):
        output=self.base/'prompt space.md'
        args=['panel','--preset','ai','--question','研究问题','--output',output]
        self.run_script(TOOL,*args)
        original=output.read_bytes()
        self.run_script(TOOL,*args,expected=2)
        self.assertEqual(output.read_bytes(),original)

    def test_three_host_install_and_idempotence(self):
        self.install('--target','all','--dry-run')
        self.assertFalse(self.home.exists())
        self.install('--target','all')
        for root in ['.agents/skills','.gemini/config/skills','.claude/skills']:
            self.assertEqual(digest(self.home/root/'mdt-research'),digest(SKILL))
        self.assertEqual(self.install('--target','all').stdout.count('已安装相同内容'),3)
        installed=self.home/'.claude/skills/mdt-research/scripts/mdt.py'
        self.assertEqual(len(json.loads(self.run_script(installed,'list','--json').stdout)),12)

    def test_backup_preserves_customizations(self):
        self.install('--target','claude-code')
        dest=self.home/'.claude/skills/mdt-research'
        (dest/'custom.md').write_text('my changes',encoding='utf-8')
        self.install('--target','claude-code',expected=2)
        self.assertEqual((dest/'custom.md').read_text(encoding='utf-8'),'my changes')
        self.install('--target','claude-code','--replace')
        backups=list((self.home/'.claude/skill-backups').glob('mdt-research.*'))
        self.assertEqual(len(backups),1)
        self.assertEqual((backups[0]/'custom.md').read_text(encoding='utf-8'),'my changes')
        self.assertEqual(digest(dest),digest(SKILL))

    def test_project_layout_all_and_single_host(self):
        project=self.base/'project space'
        self.install('--target','all','--workspace',project)
        for directory in ['.agents','.claude']:
            self.assertEqual(digest(project/directory/'skills/mdt-research'),digest(SKILL))
        claude_only=self.base/'claude-only'
        self.install('--target','claude-code','--workspace',claude_only)
        self.assertTrue((claude_only/'.claude/skills/mdt-research/SKILL.md').exists())
        self.assertFalse((claude_only/'.agents').exists())
        self.install('--target','all','--workspace',project,'--claude-root',self.base/'custom',expected=2)

    def test_legacy_both_cli_and_custom_paths(self):
        self.install('--target','both')
        self.assertFalse((self.home/'.claude').exists())
        self.install('--target','antigravity-cli')
        self.assertTrue((self.home/'.gemini/antigravity-cli/skills/mdt-research/SKILL.md').exists())
        custom=self.base/'custom skills'
        self.install('--target','claude-code','--claude-root',custom)
        self.assertEqual(digest(custom/'mdt-research'),digest(SKILL))

    def test_modified_source_rejected(self):
        copy=self.base/'copy'
        shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
        (copy/'mdt-research/SKILL.md').write_text('changed',encoding='utf-8')
        self.run_script(copy/'install.py','--home-dir',self.home,'--target','all',expected=2)
        self.assertFalse(self.home.exists())


if __name__=='__main__': unittest.main()
