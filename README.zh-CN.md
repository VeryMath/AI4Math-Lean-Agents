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

`lean-formalization` 借鉴公开 Lean-specialist agent 机制，例如 theorem-state loop、premise retrieval、bounded proof search、validation gate、failure memory 和可选官方 Numina handoff。这些是工作流机制，不是强制外部服务。

可选 Lean 专用 agent backend 当前只记录已经验证过的运行路径。当前支持的可选 backend：official Numina Lean Agent runtime。未来 backend adapter 需要等 setup、调用、验证和 failure triage 合约文档化后再宣称支持；不要写成已支持。

## 技能包

| 包 | 适用任务 | 入口 |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | 安装或验证 Lean 4、`elan`、`lake` 和可复用 mathlib workspace，就绪后再进入证明工作。 | [`README`](skills/lean-setup/README.md) · [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | 形式化 theorem statement、修复 Lean proof、完成 `sorry`、审查 patch，并在需要时协调 Numina。 | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

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

`approve` 表示执行下一步，`revise` 表示先修改计划，`reject` 表示停止当前路线，
`skip` 表示跳过当前阶段。修改 theorem statement、设置 Numina、编辑源码和接受最终 proof
claim 前都应先请求用户确认。

## 支持范围

- Lean project/workspace inspection。
- 只配置环境时，可创建或复用共享 `~/.ai4math/lean-workspace`；默认使用 AI4Math managed baseline `leanprover/lean4:v4.28.0`，除非用户明确覆盖。
- theorem formalization、proof repair、proof completion 和 `sorry` completion。
- patch review：检查 `sorry`、`admit`、新引入的 `axiom` 和 theorem statement drift。
- 可选 Lean 专用 agent backend adapter 流程；当前实现的是由 coding agent 协调的 official `project-numina/numina-lean-agent` runtime 设置和调用。
- proof blocked 时抽取最小失败 Lean fragment。
- 借鉴 Lean 专用 agent 模式：theorem-state loop、premise retrieval、bounded proof search、失败记忆、validation oracle 和 minimal handoff。

Numina 是可选链路，也是当前唯一内置可部署 backend adapter。公共 CLI 不提供并行的 `numina-*` workflow；`doctor` 用于报告 readiness，`configure --setup-numina --project-name <name>` 用于在 review 后执行本地设置，默认位置为 `~/.ai4math/numina-runtime/`。只有当用户明确要求 `Numina`、`official Lean Agent`、批量 proof search 或外部 subagent run 时，才应进入 official Numina backend。

未来 backend adapter 可参考 `skills/lean-runtime/references/backend_adapter_checklist.md`，但在 deployment、readiness checks、调用、validation 和 failure triage 文档化前，不要写成已支持。
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

## 验证

修改 Lean 逻辑时优先使用包内验证。formalization 包提供：

```bash
python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

至少应对变更过的标准技能包运行本地 skill validator，并检查 README 链接。

## 安全边界

不要提交 Lean build artifacts、下载的 Numina runtime state、API key、`.env` 文件、机器相关路径或私有 theorem notes。没有本地 Lean/Lake 验证或明确通过的 review gate 时，不要宣称 proof accepted。
