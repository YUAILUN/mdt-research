# MDT Research

**MDT 科研：用跨学科专业方法评议研究问题，形成证据判断与验证计划。**

[English](README.en.md) · [下载安装包](https://github.com/YUAILUN/mdt-research/releases/latest) · [安装说明](安装与使用.md) · [职能目录](mdt-research/references/roles.md) · [示例评议](示例评议.md)

MDT 是 Multidisciplinary Team。本 skill 以领域机制、文献证据、实验设计、统计、因果推断等专业职能审查同一个科研问题，再综合关键分歧、证据缺口和可执行的下一步。角色是方法职责，不对应真实人物，也不模仿个人经历、观点或语言。

支持 **Codex、Antigravity、Claude Code**。工作流和方法卡以中文编写，输出默认使用用户的语言。

## 快速安装

需要 Git 和 Python 3.9+。安装器仅使用标准库、复制本地文件，不调用模型或网络。

```bash
git clone https://github.com/YUAILUN/mdt-research.git
cd mdt-research
python3 install.py --target all
```

也可从 [Releases](https://github.com/YUAILUN/mdt-research/releases/latest) 下载 ZIP，解压后运行同一条安装命令。

| 平台 | 单平台安装 | 全局 skill 目录 | 调用 |
| --- | --- | --- | --- |
| Codex | `python3 install.py --target codex` | `~/.agents/skills/mdt-research/` | `$mdt-research` |
| Antigravity 2.0 / IDE | `python3 install.py --target antigravity` | `~/.gemini/config/skills/mdt-research/` | 使用 mdt-research；2.0 可用 `/mdt-research` |
| Claude Code | `python3 install.py --target claude-code` | `~/.claude/skills/mdt-research/` | `/mdt-research` |
| Antigravity CLI | `python3 install.py --target antigravity-cli` | `~/.gemini/antigravity-cli/skills/mdt-research/` | `/mdt-research` |

安装目录依据 [Codex](https://learn.chatgpt.com/docs/build-skills)、[Antigravity](https://antigravity.google/docs/skills) 与 [Claude Code](https://code.claude.com/docs/en/skills) 官方文档。安装后新开聊天，未显示时重新加载或重启宿主。

```bash
# 只查看安装计划
python3 install.py --target all --dry-run

# 项目内安装
python3 install.py --target all --workspace /path/to/project
```

项目安装时，Codex 和 Antigravity 使用 `.agents/skills/`，Claude Code 使用 `.claude/skills/`。自定义路径、旧版目录和手动安装见 [完整说明](安装与使用.md)。

## 如何使用

```text
使用 mdt-research 对这个课题开展跨学科科研评议：
小样本条件下，怎样验证一个候选生物标志物具有真实预测价值？
请给出主要证据缺口、关键分歧和三个可执行的验证步骤。
```

Claude Code：

```text
/mdt-research 仅由 Experimental Design、Statistics、Causal Inference
审查下面的研究方案，围绕会改变结论的分歧进行第二轮评议。
```

计算研究：

```text
使用 mdt-research 审查这个模型改进是否值得继续投入。
预算固定，不能增加训练算力。请比较公平基线、消融与泛化测试。
```

## 专业职能与模式

12 个职能：Domain Science、Evidence Review、Experimental Design、Causal Inference、Statistics、Data Quality、Computational Modeling、Engineering Feasibility、Reproducibility、Ethics & Governance、Translation & Impact、Research Strategy。

默认按问题选 6 个互补职能；快速 4 个；深入可覆盖 12 个；也支持指定职能、第二轮评议和离线模式。没有适用任务的职能可以省略，不为凑人数添加角色。

每个职能提供判断、方法应用、关键缺口与验证动作。综合依据外部证据和论证，不按同意人数判断真伪。同一模型的多职能输出不等于多个独立专家意见。

## 本地工具

```bash
python3 mdt-research/scripts/mdt.py list
python3 mdt-research/scripts/mdt.py show statistics causal-inference
python3 mdt-research/scripts/mdt.py panel --preset biomed --question '如何验证候选靶点？' --output panel-prompt.md
```

`panel` 只组装提示包，不调用模型、访问网络或执行实验。正常使用由宿主读取 [SKILL.md](mdt-research/SKILL.md) 和按需加载的方法卡。

## 更新与开发

```bash
git pull --ff-only
python3 install.py --target all --replace
```

已有不同内容先保留备份，相同内容重复安装会跳过。改动 skill 后更新清单并检查：

```bash
python3 scripts/package.py --manifest-only
python3 -B -m unittest discover -s tests -v
python3 scripts/package.py
```

欢迎通过 Issue 或 Pull Request 改进方法、别名和示例。具体专业规则应说明适用条件并提供可核验来源。MIT 许可，Copyright (c) 2026 YUAILUN。

安装器与本地工具经过隔离目录检查；宿主 UI 的实际发现和回答效果未逐个平台评测，见 [验证记录](验证记录.md)。本 skill 帮助组织科研分析，具体结论仍需研究证据与适用的方法支持。
