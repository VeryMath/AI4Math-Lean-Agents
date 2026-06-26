# Lean Setup

`lean-setup` is the setup-only entrypoint for AI4Math Lean work. Use it when the
task is to install or verify Lean 4, `elan`, `lake`, or a reusable mathlib
workspace before formalization.

## When To Use It

Use this package when you need to:

- check whether Lean, `elan`, and `lake` are available;
- create or reuse `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`;
- run a Lean/mathlib smoke test;
- report toolchain, workspace, mathlib revision, and remaining setup work.

Do not ask for a theorem target in setup-only mode. For theorem formalization,
proof repair, `sorry` completion, patch review, or optional Numina proof search,
hand off to `lean-formalization`.

## Implementation Boundary

This package does not duplicate Lean runtime logic. It reuses the helper CLI and
runtime references from `../lean-formalization/`.

Useful commands from this package directory:

```bash
python ../lean-formalization/scripts/ai4m_lean.py doctor --cwd <target-project-or-workspace>
python ../lean-formalization/scripts/ai4m_lean.py configure --cwd <target-project-or-workspace> --create-workspace
python ../lean-formalization/scripts/ai4m_lean.py smoke-test --cwd <target-project-or-workspace>
```

Use `--dry-run` when the user wants to review setup actions before downloads,
builds, or environment changes.
