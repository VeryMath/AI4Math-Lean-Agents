# Lean Runtime Configuration

This skill uses a coding-agent Lean workflow by default. Local Lean/Lake is the primary validation layer. Optional backend integration is adapter-first; the official Numina runtime is a built-in recommended adapter recipe under ignored shared local state. See `numina_runtime.md` for Numina deployment and call details, and `backend_adapter_checklist.md` for other adapters.

## Shared Layout

```text
${AI4MATH_HOME:-~/.ai4math}/
├── lean-workspace/
├── lean-workspaces/
├── numina-runtime/
├── logs/
└── failures/
```

Repository-local machine settings still live under `<repo>/.ai4math/` and should not be committed. The reusable Lean workspace and built-in recommended Numina adapter runtime are shared by default so standalone tasks do not create a fresh workspace in every project.

## Tool Checks

Use:

```bash
python skills/lean-runtime/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py env --cwd .
```

Required default workflow tools are `git`, `python3`, `elan`, `lean`, and `lake`. Backend adapter setup may additionally report adapter-specific tools such as `curl`, `uv`, and `claude`. Numina adapter calls need a working Claude CLI/auth path and may need additional API keys for search/tool skills.

## Reusable Lean Workspace

For standalone tasks, prefer `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`. This canonical managed workspace defaults to the AI4Math baseline toolchain `leanprover/lean4:v4.28.0`; use `--toolchain` only as an explicit override. Create it once with:

```bash
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --create-workspace
```

Equivalent Lake commands:

```bash
elan run leanprover/lean4:v4.28.0 lake new lean_workspace math
elan run leanprover/lean4:v4.28.0 lake update
elan run leanprover/lean4:v4.28.0 lake exe cache get
elan run leanprover/lean4:v4.28.0 lake build
```

If a user project already has `lean-toolchain` and `lakefile.{lean,toml}`, use that project and do not change versions without approval. If the canonical workspace already has `lake-manifest.json` and `.lake/`, reuse it instead of rerunning cache/build. If a standalone task needs a different Lean/mathlib revision than the shared managed workspace, use a versioned workspace under `${AI4MATH_HOME:-~/.ai4math}/lean-workspaces/` instead of overwriting `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`.

## Local Config

Machine-specific settings live in `.ai4math/lean_agent.local.toml` and should not be committed. Example:

```toml
[lean]
workspace_mode = "reuse-managed"
managed_workspace_path = "~/.ai4math/lean-workspace"
align_workspace_versions = true
preferred_toolchain = "leanprover/lean4:v4.28.0"

[agent]
mode = "coding-agent"
backend = "none"
```

Environment overrides:

```bash
export AI4MATH_HOME="~/.ai4math"
export AI4MATH_LEAN_WORKSPACE="~/.ai4math/lean-workspace"
export AI4MATH_LEAN_TOOLCHAIN="leanprover/lean4:v4.28.0"
export AI4MATH_NUMINA_HOME="~/.ai4math/numina-runtime"
```
