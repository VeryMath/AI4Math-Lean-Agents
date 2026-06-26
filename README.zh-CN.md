# AI4Math Lean Skills

[English](README.md) | 简体中文

本仓库提供两个 AI4Math Lean skills：

- `lean-setup`：用于 Lean 4、`elan`、`lake` 和可复用 mathlib workspace 的 setup-only 入口。
- `lean-formalization`：面向 coding agent 的 Lean 4 形式化、proof repair 和 validation skill package。

`lean-formalization` 采用 coding-agent-first 定位，设计参考并整合了 Numina、LeanDojo/ReProver、LeanCopilot、COPRA-style proof search、Lean LSP/MCP 集成和轻量迭代 proof agent 等公开 Lean 专用 agent 的机制。

## 适合什么任务

当你有这些输入或需求时使用：

- 只想创建或验证 Lean/mathlib 工作区时使用 `lean-setup`；
- 需要检查的 Lean project 或 Lean 文件；
- 需要转写或形式化的 theorem statement；
- 带有 `sorry`、`admit`、errors 或 statement drift 风险的 proof；
- 需要由 coding agent 协调的可选 Numina 设置。

## 会产出什么

Agent 应产出 Lean patches、validation summaries、blocked-goal explanations、minimized failures 和可选 Numina setup evidence。

## 安装

把下面这句话发给你的 coding agent：

```text
请帮我安装 `lean-setup` 和 `lean-formalization` skills，链接是：https://github.com/VeryMath/AI4Math-Lean-Agents.git。请读取 `.agent.md`，安装其中声明的 Skill entrypoints，验证 `$lean-setup` 和 `$lean-formalization` 可用，并告诉我是否需要重启 agent。
```

如果你已经有本仓库的本地文件夹，把链接换成本地路径即可。clone、link、配置、reload/restart 检查和验证都交给 coding agent 处理。

## 快速开始

只配置 Lean 环境和 mathlib 工作区：

```text
请使用本仓库的 Lean setup 工作流。

请先读取：
- AGENTS.md
- skills/lean-setup/SKILL.md

目标：
创建或验证一个可复用的 Lean 4/mathlib 工作区。
```

形式化或 proof repair：

```text
请使用本仓库的 Lean formalization 工作流。

请先读取：
- AGENTS.md
- SKILL.md
- skills/lean-formalization/SKILL.md

目标：
<描述 Lean formalization、proof repair、theorem transcription 或 validation 任务>

约束：
- 先检查 Lean project；
- 未获批准前保留 theorem statement；
- 在设置 Numina、编辑源码或接受最终 proof claim 前先请求确认。
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
- 只配置环境时，可创建或复用共享 `~/.ai4math/lean-workspace`。
- theorem formalization、proof repair、proof completion 和 `sorry` completion。
- patch review：检查 `sorry`、`admit`、新引入的 `axiom` 和 theorem statement drift。
- 可选 official `project-numina/numina-lean-agent` runtime 设置和调用。
- proof blocked 时抽取最小失败 Lean fragment。
- 参考并整合 Lean 专用 agent 模式：theorem-state loop、premise retrieval、bounded proof search、失败记忆、validation oracle 和 minimal handoff。

## 维护者检查

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

## 相关工作与公开参考

本项目设计参考以下公开 Lean 生态项目和 Lean-agent 系统，同时保持自己的
coding-agent-first 工作流和本地 Lean 验证边界：

- [Lean](https://lean-lang.org/) 和 [Lean 4](https://github.com/leanprover/lean4)
- [mathlib4](https://github.com/leanprover-community/mathlib4)
- [Numina Lean Agent](https://github.com/project-numina/numina-lean-agent)
- [Numina Putnam 2025](https://github.com/project-numina/Numina-Putnam2025)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo) 和 [ReProver](https://github.com/lean-dojo/ReProver)
- [LeanCopilot](https://github.com/lean-dojo/LeanCopilot)
- [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp)
- [COPRA](https://github.com/trishullab/copra)

这些项目用于说明相关工作和设计来源，主要涉及 setup、proof-state loop、
retrieval、validation 和 failure handoff 等机制。除非另有明确说明，本仓库不
内置、不复刻、不替代，也不声称兼容原系统。
