<div align="center">

# AI4Math · Lean Agents

面向 coding agent 的 Lean 4 setup、formalization、proof repair 与本地
Lean/mathlib validation workflows。

[English](README.md) · [Contributors](CONTRIBUTORS.md) · [Skill packages](#skill-packages) · [安装](#安装) · [快速开始](#快速开始) · [参考项目](#相关工作与公开参考) · [安全边界](#安全与边界)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-2-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

<p align="center">
  如果这个项目对你有帮助，欢迎为仓库点 Star ⭐
  <a href="https://github.com/VeryMath/AI4Math-Lean-Agents"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/VeryMath/AI4Math-Lean-Agents?style=social"></a>
</p>

## 这个仓库是什么

本仓库是 AI4Math 的 Lean agent skills 主页。它让 coding agent 能够按结构化
流程检查 Lean projects、配置可复用 Lean/mathlib workspace、形式化 theorem
statements、修复 proofs、补全 `sorry`，并对 Lean patches 做本地验证。

根 README 只作为公开地图。实际使用时，请进入匹配任务的 package 并读取对应
说明。`skills/lean-runtime/` 是共享支持层，放置 scripts、schemas、prompts、
tests 和 references；用户不应把它作为独立 Skill 直接调用。

Backend 集成采用 adapter-first。当前内置推荐 adapter：official Numina Lean Agent runtime。Numina 和 Archon 是推荐 adapter candidates，不是默认项或硬依赖。其他 Lean-specialist backend 可由 coding agent 按 backend adapter checklist 接入；不要调用任何 backend，除非 deployment、readiness checks、调用、validation 和 failure triage 已经文档化。

## Skill Packages

| Package | 用途 | 入口 |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | 安装或验证 Lean 4、`elan`、`lake` 和可复用 mathlib workspace readiness。 | [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | 形式化 theorem statements、修复 Lean proofs、补全 `sorry`、审查 Lean patches，并在获批时协调可选 backend adapters。 | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

## 安装

推荐使用 AI-assisted installation：让 coding agent clone 或更新仓库，读取 Skill
说明，安装两个公开 entrypoints，让 `lean-runtime` 保持在 sibling 位置，并验证
Skill discovery。

```text
请帮我安装这些 AI4Math Lean Skills。

Repository: https://github.com/VeryMath/AI4Math-Lean-Agents.git
Branch: main
Skill paths:
- skills/lean-setup
- skills/lean-formalization

请执行：
1. 本地 clone 或更新仓库。
2. 读取 README.md、AGENTS.md、SKILL.md 和每个目标 Skill entrypoint。
3. 保持 sibling 的 skills/lean-runtime 支持目录在原位。
4. 如果当前环境支持本地 Skill discovery，把每个包含 SKILL.md 的目录链接到本地 skills 目录。
5. 验证 $lean-setup 和 $lean-formalization 是否可被发现。
6. 告诉我安装路径、是否需要重启，并给我一个测试 prompt。
```

Codex-style 本地 discovery 的手动 fallback：

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/lean-setup" ~/.codex/skills/lean-setup
ln -s "$PWD/skills/lean-formalization" ~/.codex/skills/lean-formalization
```

如果你的 agent 使用其他本地 Skill 目录，请把 `~/.codex/skills` 替换为实际配置。

## 快速开始

clone 仓库并选择 package：

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
```

只做 Lean 环境配置时，从这里开始：

```text
skills/lean-setup/SKILL.md
```

做 formalization、proof repair 或 `sorry` completion 时，从这里开始：

```text
skills/lean-formalization/SKILL.md
```

完整交互案例：

```text
examples/lean-setup-add-zero.zh-CN.md
```

## 仓库结构

```text
AI4Math-Lean-Agents/
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── AGENTS.md
├── examples/
└── skills/
    ├── lean-setup/
    ├── lean-formalization/
    └── lean-runtime/
```

用户可见 workflow instructions 放在 `lean-setup` 和 `lean-formalization`。
可复用 scripts、tests、schemas、prompts 和 backend-adapter references 放在
`lean-runtime`。

## 验证

默认本地验证：

在仓库根目录运行交付验证：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

完整本地 Lean workspace 检查：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

可选 adapter 设置：仅当用户明确要求 Numina 或其他 backend adapter，并批准
setup plan 后才运行：

```bash
python3 skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
```

## 安全与边界

不要提交 API keys、`.env` 文件、本地 runtime state、下载的 Lean artifacts、
generated caches 或机器相关 Numina paths。默认 Lean workflow 是本地
coding-agent-first 路径；Numina、Archon、Lean LSP/MCP 或其他 backend adapters
只有在用户明确批准后才 setup 或调用。

最终 Lean patches 应尽量本地验证，并且不能引入 `sorry`、`admit`、新 `axiom`
或未获批准的 theorem statement drift。

## 相关工作与公开参考

本项目参考以下公开 Lean 生态项目，同时保持自己的本地验证边界：

- [Lean](https://lean-lang.org/) 和 [Lean 4](https://github.com/leanprover/lean4)
- [mathlib4](https://github.com/leanprover-community/mathlib4)
- [Numina Lean Agent](https://github.com/project-numina/numina-lean-agent)
- [Numina Putnam 2025](https://github.com/project-numina/Numina-Putnam2025)
- [Archon](https://github.com/frenzymath/Archon)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo) 和 [ReProver](https://github.com/lean-dojo/ReProver)
- [LeanCopilot](https://github.com/lean-dojo/LeanCopilot)
- [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp)
- [COPRA](https://github.com/trishullab/copra)

这些项目用于说明 setup、proof-state loop、retrieval、validation 和 failure
handoff 等设计来源。除非另有明确说明，本仓库不内置、不复刻、不替代，也不声称
兼容原系统。
