# AI4Math Lean Agents

AI4Math Lean Agents is a guidance-first Codex skill for Lean 4 formal verification. The active coding agent directly reads, edits, and checks Lean code; the bundled CLI is only a deterministic helper toolbox for environment checks, Lean validation, patch review, and minimal failure handoff.

The canonical skill package lives at:

```text
skills/AI4Math-Lean-Agents/
```

## What It Supports

- Lean project/workspace inspection.
- Reusable `.ai4math/lean-workspace` setup for standalone Lean files.
- Theorem formalization, proof repair, proof completion, and `sorry` completion.
- Patch review for `sorry`, `admit`, newly introduced `axiom`, and theorem statement drift.
- Minimal failing Lean fragment extraction when a proof is blocked.

This project does not deploy or call Numina. Numina is referenced only as workflow provenance in the skill documentation.

## Repository Layout

```text
.
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── README.md
├── LICENSE
├── .codex/
├── .cursor/
├── .github/
├── .opencode/
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

## Use With Codex

Install or sync the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
rsync -a --delete skills/AI4Math-Lean-Agents/ ~/.codex/skills/ai4math-lean-agents/
```

Then ask Codex for Lean formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, or minimal failure extraction.

## Helper Commands

Run commands from the repository root:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py env --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py doctor --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

The helper CLI is not the proof engine. The coding agent remains responsible for reading Lean errors, editing proofs, and choosing proof strategy.

## Validate

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

For a full local Lean workspace check:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```
