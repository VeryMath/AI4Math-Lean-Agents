---
name: autoadmm-formalization
description: Use when converting or attempting to formalize evolved adaptive-ADMM Python update_rho rules, routing Strategy3-safe candidates to deterministic Lean certificates and routing novel candidates into bounded coding-agent Lean proof attempts.
---

# AutoADMM Formalization

Use this skill for the AutoADMM pipeline where an evolutionary search produces a Python `update_rho` rule and the coding agent must decide how to attempt Lean formalization.

This skill has two modes:

- **Strict certificate mode:** use the R1-R7 checker as a hard gate only when the user wants a deterministic Strategy3 certificate.
- **Exploration mode:** use the checker as a risk map, not a rejection gate. Rank evolved candidates by score/novelty, let the coding agent attempt Lean proof work for a fixed round/time budget, then either deliver a compiling proof or preserve the smallest failing Lean fragment.

## Required Contract

A candidate is immediately certifiable only when it satisfies the Strategy3/R1-R7 shape:

- `tau_k` is nonnegative, summable, and depends only on `k` and fixed constants.
- The rho update is exactly one of `rho * (1 + tau_k)`, `rho / (1 + tau_k)`, or `rho`.
- Residuals may decide only the direction, not the numeric update factor.
- No clipping, projection, damping, smoothing, averaging, or post-update rho modification is allowed.
- The rule is deterministic and fully specified.

Read `references/strategy3_contract.md` when the candidate is not obviously valid. In exploration mode, violations are proof obligations or likely blockers; they are not automatic reasons to stop.

## Workflow

1. Locate the Lean project root, usually the folder with `lakefile.lean` and `Optlib`.
2. Locate the evolved Python candidate, usually `lean_admm/alpha_evolve/openevolve_output/best/best_program.py`.
3. Run the static contract check:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py inspect --program <candidate.py> --json
   ```

   To audit a full OpenEvolve output directory without calling Lean, Numina, or model APIs, run:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py audit --path <openevolve_output> --json
   ```

   The audit command scans Python files and JSON files with a top-level `code` string, then reports valid/invalid counts, violated R-rule counts, the first issue per candidate, and `best_valid_candidate` when any candidate is Strategy3-safe.

   For coding-agent orchestration over large OpenEvolve runs, prefer the compact form:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py audit --path <openevolve_output> --summary-only --json
   ```

   To pick candidates for a softer coding-agent attempt, rank them without requiring R1-R7 success:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py explore \
     --path <openevolve_output> \
     --min-generation 1 \
     --exclude-program <alpha_evolve>/initial_program.py \
     --top-n 10 \
     --json
   ```

   `explore` returns candidates with `proof_route = strict-template` or `exploratory-coding-agent`. For the exploratory route, do not render the fixed Strategy3 template as the final proof. Instead, create a scratch Lean file, state the candidate-specific update, and try to connect it to existing ADMM convergence lemmas or identify the missing mathematical lemma.

   To materialize the highest-scoring Strategy3-safe candidate from JSON `code` into a Python file:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py audit --path <openevolve_output> --write-best <candidate.py> --summary-only --json
   ```

   When the OpenEvolve run includes a Strategy3-safe seed, exclude it before selecting the formalized candidate:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py audit \
     --path <openevolve_output> \
     --min-generation 1 \
     --exclude-program <alpha_evolve>/initial_program.py \
     --write-best <candidate.py> \
     --summary-only \
     --json
   ```

   To run the full deterministic certificate chain in one helper command:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py certify-best \
     --openevolve-output <openevolve_output> \
     --project-root <lean_project> \
     --candidate-output <formal_best.py> \
     --lean-output <project>/Optlib/Algorithm/AdaptiveADMM/Strategies/auto_update_rho_formal_best.lean \
     --min-generation 1 \
     --exclude-program <alpha_evolve>/initial_program.py \
     --report-output <certificate.json> \
     --json
   ```

   `certify-best` performs audit, writes the best Strategy3-safe candidate, renders the Lean template, runs `lake env lean`, and can persist the full JSON certificate. It should be the default helper for coding-agent orchestration when a full OpenEvolve output directory is available.

   In the original AutoADMM repository, prefer the local evaluator gate when present:

   ```python
   from alpha_evolve.strategy3_contract import analyze_file
   ```

4. If the candidate fails R1-R7:
   - In strict certificate mode, do not render the Strategy3 template. Report the exact violated R-rules and keep the smallest offending Python fragment.
   - In exploration mode, continue with a bounded coding-agent Lean attempt. Treat violated R-rules as the list of proof obligations to attack or minimize.
5. In evaluator mode, expose separate `formal_score`, `numeric_score`, and `combined_score = formal_score * numeric_score` metrics. Keep `combined_score` for OpenEvolve compatibility.
6. In search mode, harden the evolutionary system prompt: explicitly forbid `factor`, `scale`, `adjusted_t`, clipping, residual-scaled tau, and residual-dependent auxiliary values. Include the safe Strategy3 template and tell the search loop to fix `formal_score` before optimizing `numeric_score`.
7. If the candidate is accepted by strict mode, render the supported Strategy3 Lean template. If the best candidate came from JSON, render from the file produced by `--write-best`:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py render-lean --program <candidate.py> --output <project>/Optlib/Algorithm/AdaptiveADMM/Strategies/auto_update_rho_generated.lean --json
   ```

8. Verify the generated Lean file:

   ```bash
   python skills/AI4Math-Lean-Agents/autoadmm-formalization/scripts/autoadmm_formalize.py verify-lean --project-root <project> --lean-file <generated.lean> --json
   ```

9. For exploration mode, use `ai4math-lean-agents` directly:
   - budget: default 5 proof-edit rounds or 30 minutes unless the user specifies otherwise;
   - temporary `sorry` is allowed only inside scratch work, never in final accepted output;
   - after each meaningful edit, run `lake env lean <scratch-or-target-file>`;
   - if blocked, preserve the smallest failing Lean file plus exact goals/errors and the mathematical condition needed to continue.

## Boundaries

- Do not deploy Numina or require Claude CLI for this skill.
- Do not let an LLM directly generate arbitrary final Lean from Python. Use a checked IR/template path first.
- Do not accept generated Lean that compiles only because of `sorry`.
- Do not weaken `Strategy3`, `AdaptableStrategy`, `h_update_equiv`, or `auto_converges` to fit an unsafe candidate.
- Do not present exploration-mode failure as a formal certificate. It is a proof attempt with a minimal failure handoff.

## Current Scope

The bundled script supports the exact L1 p-series residual-balancing pattern whose `tau` is a single return of `c / ((k + 1) ** p)`. Shifted, piecewise, clipped, residual-scaled, or otherwise transformed `tau` definitions are rejected until a matching Lean proof template and tests are added.
