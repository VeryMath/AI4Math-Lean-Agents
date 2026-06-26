# Lean Formalization

[English](README.md) | 简体中文

`lean-formalization` 帮助 coding agent 处理 Lean 4 形式化、proof repair 和 validation 任务。它是 coding-agent-first，但会蒸馏 Numina、LeanDojo/ReProver、LeanCopilot、COPRA-style proof search、Lean LSP/MCP 集成和轻量迭代 proof agent 的有效机制。

## 适合什么任务

当你有这些输入或需求时使用：

- 需要检查的 Lean project 或 Lean 文件；
- 需要转写或形式化的 theorem statement；
- 带有 `sorry`、`admit`、errors 或 statement drift 风险的 proof；
- 需要由 coding agent 协调的可选 Numina 设置。

## 会产出什么

Agent 应产出 Lean patches、validation summaries、blocked-goal explanations、minimized failures 和可选 Numina setup evidence。

## 安装

把下面这句话发给你的 coding agent：

```text
请帮我安装 `lean-formalization` skill，链接是：https://github.com/VeryMath/AI4Math-Lean-Agents.git，分支：feature/numina-runtime-delivery。请读取 `.agent.md`，安装其中声明的 Skill entrypoint，验证 `$lean-formalization` 可用，并告诉我是否需要重启 agent。
```

如果你已经有这个 skill 仓库的本地文件夹，把链接换成本地路径即可。clone、link、配置、reload/restart 检查和验证都交给 coding agent 处理。

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
- 蒸馏 Lean 专用 agent 模式：theorem-state loop、premise retrieval、bounded proof search、失败记忆、validation oracle 和 minimal handoff。

## 维护者检查

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
