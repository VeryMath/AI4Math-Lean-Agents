# Lean Formalization

[English](README.md) | 简体中文

Lean Formalization 是一个面向 Lean 4 形式化验证的 guidance-first Skill
package。默认 Lean Agent 路径是编排官方 Numina Lean Agent runtime；当 Numina 不可用、
用户拒绝或结果不足时，本地 Lean 编辑才是 validation 和 fallback 路径。附带 CLI 只是用于
环境检查、Lean validation、Numina readiness/setup、patch review 和最小失败抽取的确定性辅助工具。

## 这个 Skill 做什么

这个独立 Skill 帮助 coding agent 处理 Lean 4 形式化任务：检查 Lean project，转写 theorem statement，
修复 proof，必要时完成 `sorry`，检查 patch 中不安全的 proof shortcut，并记录 machine-checking evidence
或最小失败片段。

当你有 Lean project、Lean 文件，或希望 agent 形式化/验证的 theorem statement 时，可以直接使用它。

## 安装 / 加载

在你的 coding-agent 环境里 clone 或打开这个 skill 仓库，然后让 coding agent 读取：

```text
AGENTS.md
SKILL.md
skills/lean-formalization/SKILL.md
```

如果目标 agent 支持本地 Skill discovery，可以把 `skills/lean-formalization/`
安装或软链接到它的 Skill 路径，然后按需 reload 或 restart。Codex、Claude、
Gemini 和 OpenCode 的薄 adapter 分别见 `.codex/INSTALL.md`、`CLAUDE.md`、
`GEMINI.md` 和 `.opencode/INSTALL.md`。

## 快速开始

```text
Use this repository's Lean workflow.

Read:
- AGENTS.md
- SKILL.md
- skills/lean-formalization/SKILL.md

Goal:
<描述 Lean formalization、proof repair、theorem transcription 或 validation 任务>

Constraints:
- inspect the Lean project first;
- preserve theorem statements unless approved;
- ask before Numina setup, source edits, or final proof claims.
```

## 如何交互使用

推荐使用 checkpoint 循环：

```text
Lean 任务 -> 项目检查 -> 计划 -> approve / revise / reject / skip
          -> 获批编辑或验证 -> 证据总结 -> 下一轮 checkpoint
```

`approve` 表示执行下一步，`revise` 表示先修改计划，`reject` 表示停止当前路线，
`skip` 表示跳过当前阶段。修改 theorem statement、设置 Numina、编辑源码和接受最终 proof
claim 前都应先问用户。

## 支持范围

- Lean project/workspace inspection。
- theorem formalization、proof repair、proof completion 和 `sorry` completion。
- patch review：检查 `sorry`、`admit`、新引入的 `axiom` 和 theorem statement drift。
- 可选 official `project-numina/numina-lean-agent` runtime 设置和调用。
- proof blocked 时抽取最小失败 Lean fragment。

## 维护者检查

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
