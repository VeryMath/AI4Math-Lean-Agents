# Lean Runtime Configuration

This skill uses a direct coding-agent workflow by default. It can also prepare an optional official Numina runtime under ignored local state when the user approves that path; see `numina_runtime.md` for deployment and call details.

## Shared Layout

```text
${AI4MATH_HOME:-~/.ai4math}/
├── lean-workspace/
├── lean-workspaces/
├── numina-runtime/
├── logs/
└── failures/
```

Repository-local machine settings still live under `<repo>/.ai4math/` and should not be committed. The reusable Lean workspace and optional Numina runtime are shared by default so standalone tasks do not create a fresh workspace in every project.

## Tool Checks

Use:

```bash
python scripts/ai4m_lean.py doctor --cwd .
python scripts/ai4m_lean.py env --cwd .
```

Required local tools for the direct workflow are `git`, `python3`, `elan`, `lean`, and `lake`. Optional Numina setup additionally reports `curl`, `uv`, and `claude` readiness. Numina and model API keys are not required for the direct workflow.

## Reusable Lean Workspace

For standalone tasks, prefer `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`. Create it once with:

```bash
python scripts/ai4m_lean.py configure --cwd . --create-workspace --toolchain leanprover/lean4:v4.28.0
```

Equivalent Lake commands:

```bash
lake new lean_workspace math
lake update
lake exe cache get
lake build
```

If a user project already has `lean-toolchain` and `lakefile.{lean,toml}`, use that project and do not change versions without approval. If a standalone task needs a different Lean/mathlib revision than the shared managed workspace, use a versioned workspace under `${AI4MATH_HOME:-~/.ai4math}/lean-workspaces/`.

## Local Config

Machine-specific settings live in `.ai4math/lean_agent.local.toml` and should not be committed. Example:

```toml
[lean]
workspace_mode = "reuse-managed"
managed_workspace_path = "~/.ai4math/lean-workspace"
align_workspace_versions = true
preferred_toolchain = "auto"

[agent]
mode = "direct-coding-agent"
backend = "none"
```

Environment overrides:

```bash
export AI4MATH_HOME="~/.ai4math"
export AI4MATH_LEAN_WORKSPACE="~/.ai4math/lean-workspace"
export AI4MATH_LEAN_TOOLCHAIN="leanprover/lean4:v4.28.0"
export AI4MATH_NUMINA_HOME="~/.ai4math/numina-runtime"
```
