# AI4Math Lean Agents

AI4Math Lean Agents is a guidance-first skill package for Lean 4 formal verification with coding agents. The active coding agent directly reads, edits, and checks Lean code; the bundled CLI is only a deterministic helper toolbox for environment checks, Lean validation, optional official Numina runtime setup, patch review, and minimal failure handoff.

The canonical skill package lives at:

```text
skills/AI4Math-Lean-Agents/
```

## What It Supports

- Lean project/workspace inspection.
- Reusable shared `~/.ai4math/lean-workspace` setup for standalone Lean files.
- Theorem formalization, proof repair, proof completion, and `sorry` completion.
- Patch review for `sorry`, `admit`, newly introduced `axiom`, and theorem statement drift.
- Minimal failing Lean fragment extraction when a proof is blocked.
- Optional official `project-numina/numina-lean-agent` deployment/call flow, mediated by the coding agent.

Numina is optional. The public CLI does not expose a parallel `numina-*` workflow; `doctor` reports readiness and `configure --setup-numina --project-name <name>` performs the reviewed local setup under `~/.ai4math/numina-runtime/` by default.

## Repository Layout

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
    └── AI4Math-Lean-Agents/
        ├── SKILL.md
        ├── agents/
        ├── config/
        ├── prompts/
        ├── references/
        ├── schemas/
        ├── scripts/
        └── tests/
```

## Use With Coding Agents

Point your coding agent at the canonical workflow:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

The repository also includes lightweight adapters for several agent environments:

- `AGENTS.md` for general repository-aware coding agents.
- `.cursor/rules/ai4math-lean-agents.mdc` for Cursor.
- `.opencode/agents/ai4math-lean-agents.md` for OpenCode.
- `CLAUDE.md` and `GEMINI.md` for agent-specific repository instructions.

For Codex-style skill installation, sync the skill folder into the user skill directory. The repository does not include a repo-local Codex shim, so a workspace that also has the system skill installed will not show two `ai4math-lean-agents` entries.

```bash
mkdir -p ~/.codex/skills
rsync -a --delete skills/AI4Math-Lean-Agents/ ~/.codex/skills/ai4math-lean-agents/
```

Then ask the coding agent for Lean formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, or minimal failure extraction.

## Helper Commands

Run commands from the repository root:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py env --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py doctor --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

The helper CLI is not the proof engine. The coding agent remains responsible for reading Lean errors, editing proofs, choosing proof strategy, and matching the user's language.

For the optional Numina path, read `skills/AI4Math-Lean-Agents/references/numina_runtime.md`. Setup and official runner calls may clone repositories, install tools, or use external model/API credentials, so they should be explained before execution.

## Validate

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

For a full local Lean workspace check:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```
