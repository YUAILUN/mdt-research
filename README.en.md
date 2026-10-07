# MDT Research

**A multidisciplinary research review skill for Codex, Antigravity, and Claude Code.**

[中文](README.md) · [Downloads](https://github.com/YUAILUN/mdt-research/releases/latest) · [Review roles](mdt-research/references/roles.md)

MDT stands for Multidisciplinary Team. This skill organizes a research question into professional review functions: domain mechanisms, evidence, experimental design, statistics, causal inference, implementation, and impact. It produces substantive disagreements, evidence gaps, and testable next steps.

Roles represent analytical responsibilities. They do not impersonate named people or claim that real experts participated. Instructions and method cards are primarily in Chinese; the host is instructed to answer in the user's language.

## Install

Requires Git and Python 3.9+. The installer copies local files using only the standard library, without network calls.

```bash
git clone https://github.com/YUAILUN/mdt-research.git
cd mdt-research
python3 install.py --target all
```

Alternatively, download and extract a ZIP from [Releases](https://github.com/YUAILUN/mdt-research/releases/latest), then run the installer.

| Host | Target | Global directory | Invocation |
| --- | --- | --- | --- |
| Codex | `codex` | `~/.agents/skills/mdt-research/` | `$mdt-research` |
| Antigravity 2.0 / IDE | `antigravity` | `~/.gemini/config/skills/mdt-research/` | Mention `mdt-research`; 2.0 supports `/mdt-research` |
| Claude Code | `claude-code` | `~/.claude/skills/mdt-research/` | `/mdt-research` |
| Antigravity CLI | `antigravity-cli` | `~/.gemini/antigravity-cli/skills/mdt-research/` | `/mdt-research` |

Install one host with `python3 install.py --target claude-code`, or another target from the table. Preview with `--dry-run`. `both` installs Codex and Antigravity only; `all` adds Claude Code.

Project installation uses `--target all --workspace /path/to/project`: Codex and Antigravity share `.agents/skills`, while Claude Code uses `.claude/skills`. Custom directories are supported through `--codex-root`, `--antigravity-root`, and `--claude-root`. Older Antigravity IDE versions may use `--antigravity-root ~/.gemini/antigravity/skills`.

For manual installation, copy the entire `mdt-research/` directory, including references. Python is optional when the host reads the Markdown directly.

## Use

```text
Use mdt-research to review this research proposal. Select relevant
professional functions, identify the evidence gaps and disagreements,
and propose three tests that could change the conclusion.
```

Default: 6 relevant functions. Request a quick review (4), deep review (up to 12), specific roles, a second round, or offline analysis. The 12 functions cover domain science, evidence, experiments, causality, statistics, data quality, computation, engineering, reproducibility, ethics, translation, and research strategy.

The host supplies the model and research tools. Multiple role assessments from one model are not independent expert evidence. Missing parameters, citations, or experimental results must not be invented.

## Update and develop

```bash
git pull --ff-only
python3 install.py --target all --replace
```

Different existing content is backed up outside the host's skills directory; identical installations are skipped. After editing the skill:

```bash
python3 scripts/package.py --manifest-only
python3 -B -m unittest discover -s tests -v
python3 scripts/package.py
```

MIT licensed, Copyright (c) 2026 YUAILUN. See the [example review](示例评议.md), [design scope](mdt-research/references/provenance.md), and [verification limits](验证记录.md). Installer logic and local helpers are tested; host UI discovery and answer quality have not been evaluated on every platform.
