# AI4Math Lean Agents

[English](README.md) | 简体中文

AI4Math Lean Agents 是一个面向 Lean 4 形式化验证的 guidance-first Skill
package。coding agent 直接读取、编辑和检查 Lean 代码；附带 CLI 只是用于环境检查、
Lean validation、可选 Numina runtime 设置、patch review 和最小失败交接的确定性辅助工具。

## 安装 / 加载

优先从当前仓库 checkout 使用。让 coding agent 读取：

```text
AGENTS.md
SKILL.md
skills/AI4Math-Lean-Agents/SKILL.md
```

如果目标 agent 支持本地 Skill discovery，可以把 `skills/AI4Math-Lean-Agents/`
安装或软链接到它的 Skill 路径，然后按需 reload 或 restart。Codex、Claude、
Gemini 和 OpenCode 的薄 adapter 分别见 `.codex/INSTALL.md`、`CLAUDE.md`、
`GEMINI.md` 和 `.opencode/INSTALL.md`。

## 快速开始

```text
Use this repository's Lean workflow.

Read:
- AGENTS.md
- SKILL.md
- skills/AI4Math-Lean-Agents/SKILL.md

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
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
