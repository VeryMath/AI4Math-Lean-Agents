<div align="center">

# AI4Math · Lean Agents

面向 Lean 4 环境准备、形式化、proof repair、patch review 和可选 Numina subagent 的 AI4Math 技能集合。

[English](README.md) · [技能包](#技能包) · [快速开始](#快速开始) · [安全边界](#安全边界)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-2-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

## 这个仓库是什么

这个仓库是 AI4Math Lean agent 技能入口。它提供一个 setup-only 入口和一个 formalization 入口，让 coding agent 可以检查 Lean 项目、准备可复用 mathlib workspace、修复证明，并用证据验证最终 patch。

`lean-formalization` 借鉴公开 Lean-specialist agent 机制，例如 theorem-state loop、premise retrieval、bounded proof search、validation gate、failure memory 和可选官方 Numina handoff。这些是工作流机制，不是强制外部服务。

## 技能包

| 包 | 适用任务 | 入口 |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | 安装或验证 Lean 4、`elan`、`lake` 和可复用 mathlib workspace，就绪后再进入证明工作。 | [`README`](skills/lean-setup/README.md) · [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | 形式化 theorem statement、修复 Lean proof、完成 `sorry`、审查 patch，并在需要时协调 Numina。 | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

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

## 仓库结构

```text
AI4Math-Lean-Agents/
├── README.md
├── README.zh-CN.md
├── SKILL.md
└── skills/
    ├── lean-setup/
    └── lean-formalization/
```

根 `SKILL.md` 是兼容路由层。具体 Lean 工作以包内说明为准。

## 验证

修改 Lean 逻辑时优先使用包内验证。formalization 包提供：

```bash
python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

至少应对变更过的标准技能包运行本地 skill validator，并检查 README 链接。

## 安全边界

不要提交 Lean build artifacts、下载的 Numina runtime state、API key、`.env` 文件、机器相关路径或私有 theorem notes。没有本地 Lean/Lake 验证或明确通过的 review gate 时，不要宣称 proof accepted。
