# AI4Math Lean Skills

[English](README.md) | 简体中文

本仓库提供两个 AI4Math Lean skills：

- `lean-setup`：用于 Lean 4、`elan`、`lake` 和可复用 mathlib workspace 的 setup-only 入口。
- `lean-formalization`：面向 coding agent 的 Lean 4 形式化、proof repair 和 validation skill package。

两个公开 skill 共享随仓库提供的 `skills/lean-runtime/` 支持层，其中包含 helper scripts、references、prompts、schemas、examples 和 tests。用户只调用两个公开 skill；安装时应让 `lean-runtime` 保持在它们的 sibling 位置。

`lean-formalization` 采用 coding-agent-first 定位，设计借鉴了 Numina、LeanDojo/ReProver、LeanCopilot、COPRA-style proof search、Lean LSP/MCP 集成和轻量迭代 proof agent 等公开 Lean 专用 agent 的机制。这些是 workflow patterns 和相关工作参考，不表示所有 backend 都已经实现。

Backend 集成采用 adapter-first。当前内置推荐 adapter：official Numina Lean Agent runtime。Numina 和 Archon 是推荐 adapter candidates，不是默认项或硬依赖。其他 Lean-specialist backend 可由 coding agent 按 backend adapter checklist 接入；在 deployment、readiness checks、调用、validation 和 failure triage 文档化前，不要调用任何 backend。

## 适合什么任务

适用场景如下：

- 只想创建或验证 Lean/mathlib 工作区时使用 `lean-setup`；
- 需要检查的 Lean project 或 Lean 文件；
- 需要转写或形式化的 theorem statement；
- 带有 `sorry`、`admit`、errors 或 statement drift 风险的 proof；
- 需要由 coding agent 通过 adapter contract 协调的可选 Lean 专用 agent backend。

## 会产出什么

Agent 应产出 Lean patches、validation summaries、blocked-goal explanations、minimized failures，以及在用户要求已批准 adapter 路径时产出可选 backend setup evidence。

## 安装

将以下安装请求提供给你的 coding agent：

```text
请帮我安装 `lean-setup` 和 `lean-formalization` skills，链接是：https://github.com/VeryMath/AI4Math-Lean-Agents.git。请读取 `.agent.md`，安装其中声明的 Skill entrypoints，并同时安装它们 sibling 的 `lean-runtime` 支持目录；验证 `$lean-setup` 和 `$lean-formalization` 可用，并告诉我是否需要重启 agent。
```

如果你已经有本仓库的本地文件夹，可将链接替换为本地路径。coding agent 应负责 clone/link、配置、reload/restart 检查与验证。

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

完整交互案例：

- [从安装 Lean skills 到验证第一个定理](examples/lean-setup-add-zero.zh-CN.md)：展示 coding agent 如何安装 `lean-setup` / `lean-formalization`，创建或复用共享 Lean workspace，并验证一个最小 `Nat` 定理。

## 如何交互使用

推荐使用 checkpoint 循环：

```text
Lean 任务 -> 项目检查 -> 计划 -> approve / revise / reject / skip
          -> 获批编辑或验证 -> 证据总结 -> 下一轮 checkpoint
```

`approve` 表示执行下一步，`revise` 表示先修改计划，`reject` 表示停止当前路线，
`skip` 表示跳过当前阶段。修改 theorem statement、设置 Numina、编辑源码和接受最终 proof
claim 前都应先请求用户确认。

## 支持范围

- Lean project/workspace inspection。
- 只配置环境时，可创建或复用共享 `~/.ai4math/lean-workspace`；默认使用 AI4Math managed baseline `leanprover/lean4:v4.28.0`，除非用户明确覆盖。
- theorem formalization、proof repair、proof completion 和 `sorry` completion。
- patch review：检查 `sorry`、`admit`、新引入的 `axiom` 和 theorem statement drift。
- 可选 Lean 专用 agent backend adapter 流程；内置推荐 recipe 是由 coding agent 协调的 official `project-numina/numina-lean-agent` runtime 设置和调用。
- proof blocked 时抽取最小失败 Lean fragment。
- 借鉴 Lean 专用 agent 模式：theorem-state loop、premise retrieval、bounded proof search、失败记忆、validation oracle 和 minimal handoff。

Numina 是可选链路，并作为内置推荐 adapter recipe 提供。Archon 和其他 Lean-specialist systems 可由 coding agent 按 `skills/lean-runtime/references/backend_adapter_checklist.md` 接入；它们不是默认依赖。公共 CLI 不提供并行的 `numina-*` workflow；`doctor` 用于报告 readiness，`configure --setup-numina --project-name <name>` 用于在 review 后执行本地设置，默认位置为 `~/.ai4math/numina-runtime/`。只有当用户明确要求 `Numina`、`official Lean Agent`、批量 proof search 或外部 subagent run 时，才应进入 Numina adapter。

不要调用任何 backend，除非 deployment、readiness checks、调用、validation 和 failure triage 已经文档化。

## 仓库结构

```text
.
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── README.md
├── LICENSE
├── .github/
├── .cursor/             # optional Cursor rule
├── .opencode/           # optional OpenCode agent
└── skills/
    ├── lean-setup/          # setup-only entrypoint
    ├── lean-formalization/  # proof/formalization entrypoint
    └── lean-runtime/        # shared support layer, not a user-invoked skill
```

## 辅助命令

在仓库根目录运行：

```bash
python skills/lean-runtime/scripts/ai4m_lean.py env --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
python skills/lean-runtime/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

辅助 CLI 不是 proof engine。coding agent 仍负责读取 Lean errors、编辑 proofs、选择 proof strategy，并匹配用户语言。

内置推荐 Numina adapter 路径请读取 `skills/lean-runtime/references/numina_runtime.md`；其他 backend 请先读取 `skills/lean-runtime/references/backend_adapter_checklist.md`。setup 和 runner calls 可能 clone repositories、安装工具或使用外部 model/API credentials，因此执行前应先说明。

## 维护者检查

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

完整本地 Lean workspace 检查：

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
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
