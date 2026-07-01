<div align="center">

# AI4Math · Lean Agents

面向 Lean 4 环境准备、形式化、proof repair、patch review 和可选 Lean-specialist backend 的 AI4Math 技能集合。

[English](README.md) · [贡献者](CONTRIBUTORS.md) · [技能包](#技能包) · [安装](#安装) · [快速开始](#快速开始) · [安全边界](#安全边界)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-2-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

## 这个仓库是什么

这个仓库是 AI4Math Lean agent 技能入口。它提供一个 setup-only 入口和一个 formalization 入口，让 coding agent 可以检查 Lean 项目、准备可复用 mathlib workspace、修复证明，并用证据验证最终 patch。

两个公开入口共享仓库内的 `skills/lean-runtime/` 支持层。这里放 helper scripts、references、prompts、schemas、examples 和 tests。用户只调用 `lean-setup` 或 `lean-formalization`；安装时应把 `lean-runtime` 作为相邻支持目录保留。

`lean-formalization` 采用 coding-agent-first 定位，并蒸馏 Numina、LeanDojo/ReProver、LeanCopilot、COPRA-style proof search、Lean LSP/MCP 集成和轻量迭代 proof agent 等公开 Lean 专用 agent 的机制。默认 coding-agent 路径应执行 distilled Lean-agent loop：project gating、statement normalization、local context pack、retrieve-before-inventing、bounded proof attempts、failed-route memory、Lean/Lake validation 和 minimal failure handoff。能力地图见 `skills/lean-runtime/references/lean_agent_capability_map.md`。

Backend 集成采用 adapter-first。当前内置推荐 adapter：official Numina Lean Agent runtime。Numina 和 Archon 是推荐 adapter candidates，不是默认项或硬依赖。Lean LSP/MCP 作为可选 adapter recipe，用于用户明确要求 goal-state tooling 或 MCP-backed theorem search 的场景。其他 Lean-specialist backend 可由 coding agent 按 backend adapter checklist 接入；在 deployment、readiness checks、调用、validation 和 failure triage 文档化前，不要调用任何 backend。

## 适合什么任务

适用场景如下：

- 只想创建或验证 Lean/mathlib 工作区时使用 `lean-setup`；
- 需要检查的 Lean project 或 Lean 文件；
- 需要转写或形式化的 theorem statement；
- 带有 `sorry`、`admit`、errors 或 statement drift 风险的 proof；
- 需要由 coding agent 通过 adapter contract 协调的可选 Lean 专用 agent backend。

Agent 应产出 Lean patches、validation summaries、blocked-goal explanations、minimized failures，以及在用户要求已批准 adapter 路径时产出可选 backend setup evidence。

## 技能包

| 包 | 适用任务 | 入口 |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | 安装或验证 Lean 4、`elan`、`lake` 和可复用 mathlib workspace，就绪后再进入证明工作。 | [`README`](skills/lean-setup/README.md) · [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | 形式化 theorem statement、修复 Lean proof、完成 `sorry`、审查 patch，并在需要时协调已批准的 backend adapter。 | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

`skills/lean-runtime/` 是共享实现层，不是用户直接调用的 skill。

## 安装

推荐方式是 AI 自动安装：让你的 coding agent 自己 clone 或更新仓库、读取 Skill 说明、安装入口并验证 discovery。

```text
请帮我安装这些 AI4Math Skills。

仓库：https://github.com/VeryMath/AI4Math-Lean-Agents.git
分支：main
Skill 路径：
- skills/lean-setup
- skills/lean-formalization

请执行：
1. 本地 clone 或更新仓库。
2. 读取 README.md、SKILL.md、AGENTS.md（如果存在）以及每个目标 Skill 入口。
3. 如果当前环境支持本地 Skill discovery，把每个包含 SKILL.md 的目录链接到本地 skills 目录。
4. 如果某个 Skill 依赖相邻的共享支持目录，请保留这些 sibling 目录。
5. 验证安装后的 Skills 是否可被发现。
6. 告诉我安装路径、是否需要重启 agent，并给我一个测试 prompt。
```

Lean skills 需要把 `skills/lean-runtime` 保持为相邻支持目录。它不是公开入口，但 `lean-setup` 和 `lean-formalization` 会依赖它。

Codex 风格本地 discovery 的手工 fallback：

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/lean-setup" ~/.codex/skills/lean-setup
ln -s "$PWD/skills/lean-formalization" ~/.codex/skills/lean-formalization
ln -s "$PWD/skills/lean-runtime" ~/.codex/skills/lean-runtime
```

如果你的 agent 使用别的本地 Skill 目录，把 `~/.codex/skills` 替换成对应配置路径。

## 快速开始

克隆仓库并选择入口：

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
```

只配置环境时，从这里开始：

```text
skills/lean-setup/SKILL.md
```

形式化或 proof repair 时，从这里开始：

```text
skills/lean-formalization/SKILL.md
```

可选 IDE 前端配置：

```text
当本地 Lean/Lake setup 和 smoke test 通过后，请继续引导我完成 Lean 的
VS Code 前端配置。

请告诉我：
- 如何安装或确认 official Lean 4 VS Code extension；
- 我在 macOS、Windows 或 Linux 上需要注意哪些系统相关 setup 步骤；
- 我应该打开哪个 Lake project 或共享 workspace 目录；
- 我应该先打开哪个 `.lean` 文件；
- 如何确认 Lean InfoView 使用的是刚才命令行 smoke test 通过的同一套 toolchain。
```

coding-agent 路径通过 `lake env lean`、`lake build` 或内置 smoke test
验证 Lean。[VS Code](https://code.visualstudio.com/) 和
[official Lean 4 extension](https://marketplace.visualstudio.com/items?itemName=leanprover.lean4)
是推荐的人类编辑前端，用于查看 goals、diagnostics、hovers 和 InfoView；
macOS、Windows 和 Linux 都可使用；但它不能替代本地 Lean/Lake 验证。
[Lean 官方安装说明](https://lean-lang.org/install/) 推荐使用 VS Code 和 Lean 4
extension 作为完整开发环境，extension setup guide 会提供系统相关引导；
IDE 与命令行检查应使用同一套 `elan`/`lake` toolchain。

这三件事不要混为一谈：

- VS Code 和 Lean InfoView 是人类查看 goals 与 diagnostics 的前端。
- Lean LSP/MCP 是可选 agent tool server；只有用户明确要求 MCP-backed
  goal/search tooling 时才配置。
- Numina 是可选 backend adapter recipe，不属于默认 Lean setup、IDE setup
  或本地验证流程。

完整交互案例：

- [从安装 Lean skills 到验证第一个定理](examples/lean-setup-add-zero.zh-CN.md)：展示 coding agent 如何安装 `lean-setup` / `lean-formalization`，创建或复用共享 Lean workspace，并验证一个最小 `Nat` 定理。

`approve` 表示执行下一步，`revise` 表示先修改计划，`reject` 表示停止当前路线，
`skip` 表示跳过当前阶段。修改 theorem statement、设置 Numina、编辑源码和接受最终 proof
claim 前都应先请求用户确认。

## 支持范围

- Lean project/workspace inspection。
- 只配置环境时，可创建或复用共享 `~/.ai4math/lean-workspace`；默认使用 AI4Math managed baseline `leanprover/lean4:v4.28.0`，除非用户明确覆盖。
- 本地 Lean/Lake readiness 通过后，可继续引导用户配置 macOS/Windows/Linux 上的 VS Code / Lean 4 extension 前端。
- theorem formalization、proof repair、proof completion 和 `sorry` completion。
- patch review：检查 `sorry`、`admit`、新引入的 `axiom` 和 theorem statement drift。
- 可选 Lean 专用 agent backend adapter 流程；内置推荐 recipe 是由 coding agent 协调的 official `project-numina/numina-lean-agent` runtime 设置和调用。
- proof blocked 时抽取最小失败 Lean fragment。
- 蒸馏 Lean 专用 agent 模式：theorem-state loop、premise retrieval、bounded proof search、failed-route memory、validation oracle 和 minimal handoff。
- 可选 Lean LSP/MCP adapter recipe：在用户明确要求时，用于 goal state、diagnostics、hover/declaration lookup、local search、MCP theorem search 和 multi-attempt screening。

Numina 是可选链路，并作为内置推荐 adapter recipe 提供。Lean LSP/MCP 是可选链路，文档位于 `skills/lean-runtime/references/lean_lsp_mcp_adapter.md`。Archon 和其他 Lean-specialist systems 可由 coding agent 按 `skills/lean-runtime/references/backend_adapter_checklist.md` 接入；它们不是默认依赖。公共 CLI 不提供并行的 `numina-*` workflow；`doctor` 用于报告 readiness，`configure --setup-numina --project-name <name>` 用于在 review 后执行本地设置，默认位置为 `~/.ai4math/numina-runtime/`。只有当用户明确要求 `Numina`、`official Lean Agent`、批量 proof search、Lean LSP/MCP 或外部 subagent run 时，才应进入 adapter。

不要调用任何 backend，除非 deployment、readiness checks、调用、validation 和 failure triage 已经文档化。

## 仓库结构

```text
AI4Math-Lean-Agents/
├── README.md
├── README.zh-CN.md
├── SKILL.md
└── skills/
    ├── lean-setup/
    ├── lean-formalization/
    └── lean-runtime/
```

根 `SKILL.md` 是兼容路由层。具体 Lean 工作以包内说明为准；共享脚本和 references 位于 `skills/lean-runtime/`。

## 辅助命令

在仓库根目录运行。

默认本地验证：

```bash
python skills/lean-runtime/scripts/ai4m_lean.py env --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/lean-runtime/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

可选 adapter 设置：仅当用户明确要求 Numina 或其他 backend adapter，并批准
setup plan 后才运行：

```bash
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
```

辅助 CLI 不是 proof engine。coding agent 仍负责读取 Lean errors、编辑 proofs、选择 proof strategy，并匹配用户语言。

distilled capability contract 请读取 `skills/lean-runtime/references/lean_agent_capability_map.md`；内置推荐 Numina adapter 路径请读取 `skills/lean-runtime/references/numina_runtime.md`；Lean LSP/MCP 请读取 `skills/lean-runtime/references/lean_lsp_mcp_adapter.md`；其他 backend 请先读取 `skills/lean-runtime/references/backend_adapter_checklist.md`。setup 和 runner calls 可能 clone repositories、安装工具或使用外部 model/API credentials，因此执行前应先说明。

## 验证

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
retrieval、validation 和 failure handoff 等机制。默认 skill 会蒸馏其中一部分机制
进入 coding-agent workflow；除非另有明确说明，本仓库不内置、不复刻、不替代，
也不声称兼容原系统。

## 安全边界

不要提交 Lean build artifacts、下载的 Numina runtime state、API key、`.env` 文件、机器相关路径或私有 theorem notes。没有本地 Lean/Lake 验证或明确通过的 review gate 时，不要宣称 proof accepted。
