#!/usr/bin/env python3
"""Conservative AutoADMM update_rho -> Strategy3 Lean helper.

This script intentionally accepts only the narrow Strategy3-safe shape:

- tau(k, c, p) is a p-series step depending only on k and fixed constants.
- update_rho returns exactly rho * (1 + tau), rho / (1 + tau), or rho.
- residuals may influence only the branch direction, not the numeric factor.
- no clipping, projection, smoothing, or post-update modification of rho.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


STATE_NAMES = {
    "r_norm",
    "s_norm",
    "rho",
    "r_ratio",
    "s_ratio",
    "residual_scale",
    "excess_ratio",
}
RHO_POSTPROCESS_NAMES = {"max", "min", "clip", "maximum", "minimum"}

SAFE_STRATEGY3_REPAIR_TEMPLATE = """Strategy3-safe rewrite template:
def tau(k, c=1.0, p=1.2):
    return c / ((k + 1.0) ** p)

def update_rho(rho, k, r_norm, s_norm, mu=3.0, c=1.0, p=1.2, eps=1e-12):
    t = tau(k, c, p)
    if r_norm > mu * max(s_norm, eps):
        new_rho = rho * (1.0 + t)
        mode = "mul"
    elif s_norm > mu * max(r_norm, eps):
        new_rho = rho / (1.0 + t)
        mode = "div"
    else:
        new_rho = rho
        mode = "keep"
    aux = t
    return new_rho, aux, mode
"""

SAFE_REPAIR_GUIDANCE = (
    "Do not introduce factor, scale, adjusted_t, clipping, max_change, smoothing, or any "
    "rho post-processing. Residuals may appear only in branch conditions deciding mul/div/keep. "
    "The numeric update factor must be exactly (1.0 + t), where t = tau(k, c, p) and tau "
    "depends only on k and fixed constants."
)


LEAN_TEMPLATE = """-- AUTO GENERATED Lean4 FILE
import Optlib.Algorithm.AdaptiveADMM.Strategies.AdaptiveStrategyBase

noncomputable section
open Topology Filter AdaptiveADMM_Verification AdaptiveADMM_Convergence_Proof AdaptiveStrategyBase

variable {E₁ E₂ F : Type*} [NormedAddCommGroup E₁] [InnerProductSpace ℝ E₁] [FiniteDimensional ℝ E₁]
  [NormedAddCommGroup E₂] [InnerProductSpace ℝ E₂] [FiniteDimensional ℝ E₂]
  [NormedAddCommGroup F] [InnerProductSpace ℝ F] [FiniteDimensional ℝ F]
variable (admm : ADMM E₁ E₂ F)

def tau_seq (c p : ℝ) (n : ℕ) : ℝ := c / Real.rpow ((n : ℝ) + 1) p

theorem h_tau_summable (c p : ℝ) (hp : 1 < p) : Summable (tau_seq c p) := by
  simpa [tau_seq] using p_series_summable_template c p hp

def dir_seq (mu eps : ℝ) (r_norm_seq s_norm_seq : ℕ → ℝ) (n : ℕ) : ℤ :=
  if r_ratio r_norm_seq s_norm_seq eps n > mu then 1
  else if s_ratio r_norm_seq s_norm_seq eps n > mu then -1 else 0

lemma h_dir (mu eps : ℝ) (r_norm_seq s_norm_seq : ℕ → ℝ) :
    ∀ n, dir_seq mu eps r_norm_seq s_norm_seq n = 1 ∨
         dir_seq mu eps r_norm_seq s_norm_seq n = 0 ∨
         dir_seq mu eps r_norm_seq s_norm_seq n = -1 := by
  intro n; by_cases h1 : r_ratio r_norm_seq s_norm_seq eps n > mu
  · simp [dir_seq, h1]
  · by_cases h2 : s_ratio r_norm_seq s_norm_seq eps n > mu
    · simp [dir_seq, h1, h2]
    · simp [dir_seq, h1, h2]

theorem auto_converges (admm_kkt : Existance_of_kkt admm) [Setting E₁ E₂ F admm admm_kkt] [IsOrderedMonoid ℝ]
    (mu eps c p : ℝ) (hp : 1 < p) (r_norm_seq s_norm_seq : ℕ → ℝ) (h_tau_nonneg : ∀ n, 0 ≤ tau_seq c p n)
    (h_rho : ∀ n, admm.ρₙ (n+1) = update_fun (tau_seq c p) (dir_seq mu eps r_norm_seq s_norm_seq) n (admm.ρₙ n))
    (fullrank₁ : Function.Injective admm.A₁) (fullrank₂ : Function.Injective admm.A₂) :
    ∃ x₁ x₂ y, Convex_KKT x₁ x₂ y admm.toOptProblem ∧ Tendsto admm.x₁ atTop (𝓝 x₁) ∧
      Tendsto admm.x₂ atTop (𝓝 x₂) ∧ Tendsto admm.y atTop (𝓝 y) := by
  let tau := tau_seq c p; let dir := dir_seq mu eps r_norm_seq s_norm_seq
  have h_dir' : ∀ n, dir n = 1 ∨ dir n = 0 ∨ dir n = -1 := fun n => by simpa [dir] using h_dir mu eps r_norm_seq s_norm_seq n
  exact Strategy3.converges_from_adaptable_strategy (admm := admm) (admm_kkt := admm_kkt)
    { tau_seq := tau, h_tau_nonneg := h_tau_nonneg, h_tau_summable := h_tau_summable c p hp,
      update_fun := update_fun tau dir, h_update_equiv := h_update_equiv tau dir h_dir' } h_rho fullrank₁ fullrank₂
"""


def read_program(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise SystemExit(f"Python parse failed: {exc}") from exc


def find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def names_in(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
        elif isinstance(child, ast.Attribute):
            names.add(child.attr)
    return names


def calls_in(node: ast.AST) -> set[str]:
    calls: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
    return calls


def assigned_names(fn: ast.FunctionDef) -> dict[str, list[ast.AST]]:
    assigned: dict[str, list[ast.AST]] = {}
    for node in ast.walk(fn):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets: list[ast.AST]
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
                value = node.value
            else:
                targets = [node.target]
                value = node.value
            for target in targets:
                if isinstance(target, ast.Name):
                    assigned.setdefault(target.id, []).append(value)
    return assigned


def direct_return_update_values(fn: ast.FunctionDef) -> list[ast.AST]:
    values: list[ast.AST] = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Return):
            continue
        value = node.value
        if not isinstance(value, (ast.Tuple, ast.List)) or not value.elts:
            continue
        update_expr = value.elts[0]
        if is_name(update_expr, "new_rho"):
            continue
        values.append(update_expr)
    return values


def invalid_mode_values(fn: ast.FunctionDef, assignments: dict[str, list[ast.AST]]) -> set[str]:
    allowed = {"mul", "div", "keep"}
    modes: set[str] = set()

    for value in assignments.get("mode", []):
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            modes.add(value.value)

    for node in ast.walk(fn):
        if not isinstance(node, ast.Return):
            continue
        value = node.value
        if not isinstance(value, (ast.Tuple, ast.List)) or len(value.elts) < 3:
            continue
        mode_expr = value.elts[2]
        if isinstance(mode_expr, ast.Constant) and isinstance(mode_expr.value, str):
            modes.add(mode_expr.value)

    return {mode for mode in modes if mode not in allowed}


def is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def is_number_one(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value in (1, 1.0)


def is_tau_name(node: ast.AST) -> bool:
    if is_name(node, "t"):
        return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "tau":
        return True
    return False


def is_one_plus_tau(node: ast.AST) -> bool:
    if is_tau_name(node):
        return False
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
        return False
    return (is_number_one(node.left) and is_tau_name(node.right)) or (
        is_tau_name(node.left) and is_number_one(node.right)
    )


def allowed_rho_update(value: ast.AST) -> bool:
    if is_name(value, "rho"):
        return True
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Mult):
        return (is_name(value.left, "rho") and is_one_plus_tau(value.right)) or (
            is_one_plus_tau(value.left) and is_name(value.right, "rho")
        )
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Div):
        return is_name(value.left, "rho") and is_one_plus_tau(value.right)
    return False


def tau_looks_like_pseries(tau_fn: ast.FunctionDef | None) -> bool:
    if tau_fn is None:
        return False
    body = effective_body(tau_fn)
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return False
    return is_supported_tau_expr(body[0].value)


def effective_body(fn: ast.FunctionDef) -> list[ast.stmt]:
    body = list(fn.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    return body


def is_supported_tau_expr(value: ast.AST | None) -> bool:
    if not isinstance(value, ast.BinOp) or not isinstance(value.op, ast.Div):
        return False
    if not is_name(value.left, "c"):
        return False
    denom = value.right
    if not isinstance(denom, ast.BinOp) or not isinstance(denom.op, ast.Pow):
        return False
    return is_k_plus_one(denom.left) and is_name(denom.right, "p")


def is_k_plus_one(value: ast.AST) -> bool:
    if not isinstance(value, ast.BinOp) or not isinstance(value.op, ast.Add):
        return False
    return (is_name(value.left, "k") and is_number_one(value.right)) or (
        is_number_one(value.left) and is_name(value.right, "k")
    )


def has_nondeterminism(fn: ast.FunctionDef) -> bool:
    bad = {"random", "time", "uuid", "requests", "open", "input"}
    return bool(calls_in(fn) & bad)


def analyze_program(program: Path) -> dict[str, Any]:
    return analyze_source(program.read_text(encoding="utf-8"), program=str(program))


def analyze_source(code: str, *, program: str | None = None) -> dict[str, Any]:
    try:
        tree = ast.parse(code, filename=program or "<candidate>")
    except SyntaxError as exc:
        checks = {
            f"R{i}": {
                "status": "violated",
                "explanation": f"Python parse failed: {exc}",
            }
            for i in range(1, 8)
        }
        return build_payload(
            program,
            checks,
            [f"Python parse failed: {exc}"],
        )
    tau_fn = find_function(tree, "tau")
    update_fn = find_function(tree, "update_rho")

    checks: dict[str, dict[str, str]] = {
        f"R{i}": {"status": "violated", "explanation": "not checked yet"} for i in range(1, 8)
    }
    issues: list[str] = []

    if update_fn is None:
        for check in checks.values():
            check["explanation"] = "update_rho was not found."
        return build_payload(program, checks, ["update_rho was not found."])

    tau_ok = tau_looks_like_pseries(tau_fn)
    if tau_ok:
        checks["R1"] = {
            "status": "satisfied",
            "explanation": "tau has p-series shape c / (k + 1)^p; Lean proof still requires c >= 0.",
        }
        checks["R2"] = {
            "status": "satisfied",
            "explanation": "tau has p-series shape; Lean proof uses p_series_summable_template with p > 1.",
        }
        checks["R3"] = {
            "status": "satisfied",
            "explanation": "tau body does not reference residuals, rho, ratios, or state variables.",
        }
    else:
        checks["R1"]["explanation"] = "tau is missing or not recognized as nonnegative p-series."
        checks["R2"]["explanation"] = "tau is missing or not recognized as summable p-series."
        checks["R3"]["explanation"] = "tau may depend on state or does not match the supported p-series shape."
        issues.append("tau is not recognized as the supported p-series form.")

    assignments = assigned_names(update_fn)
    new_rho_values = assignments.get("new_rho", []) + direct_return_update_values(update_fn)
    if not new_rho_values:
        checks["R4"]["explanation"] = "rho update expressions were not found."
        checks["R5"]["explanation"] = "numeric update factor could not be checked."
        checks["R6"]["explanation"] = "rho post-processing could not be checked."
        issues.append("rho update expressions were not found.")
    else:
        illegal_updates = [ast.unparse(value) for value in new_rho_values if not allowed_rho_update(value)]
        postprocess = [
            ast.unparse(value)
            for value in new_rho_values
            if "new_rho" in names_in(value) or calls_in(value) & RHO_POSTPROCESS_NAMES
        ]
        factor_violations = [
            ast.unparse(value)
            for value in new_rho_values
            if not allowed_rho_update(value) and "rho" in names_in(value)
        ]

        if illegal_updates:
            checks["R4"] = {
                "status": "violated",
                "explanation": "Some rho updates are not exactly rho*(1+tau), rho/(1+tau), or rho.",
            }
            issues.append("rho update is not exactly one of the Strategy3 forms: " + "; ".join(illegal_updates))
        else:
            checks["R4"] = {
                "status": "satisfied",
                "explanation": "Every new_rho assignment matches the Strategy3 three-state form.",
            }

        if factor_violations:
            checks["R5"] = {
                "status": "violated",
                "explanation": "At least one numeric update factor depends on a non-tau expression.",
            }
            issues.append(
                "numeric update factor is not only (1 + tau): " + "; ".join(factor_violations)
            )
        else:
            checks["R5"] = {
                "status": "satisfied",
                "explanation": "Multiplicative/divisive factors are exactly (1 + tau) or its reciprocal.",
            }

        if postprocess:
            checks["R6"] = {
                "status": "violated",
                "explanation": "Detected clipping, min/max bounds, or reassignment based on prior new_rho.",
            }
            issues.append("post-processing of rho was detected: " + "; ".join(postprocess))
        else:
            checks["R6"] = {
                "status": "satisfied",
                "explanation": "No rho clipping, projection, smoothing, or post-update modification detected.",
            }

    invalid_modes = invalid_mode_values(update_fn, assignments)
    if has_nondeterminism(update_fn):
        checks["R7"] = {
            "status": "violated",
            "explanation": "Detected nondeterministic or external-effect calls in update_rho.",
        }
        issues.append("update_rho is not purely deterministic.")
    elif invalid_modes:
        checks["R7"] = {
            "status": "violated",
            "explanation": "Detected mode strings outside the allowed mul/div/keep set.",
        }
        issues.append("invalid mode strings: " + ", ".join(sorted(invalid_modes)))
    else:
        checks["R7"] = {
            "status": "satisfied",
            "explanation": "No random/time/input/external calls detected in update_rho.",
        }

    return build_payload(program, checks, issues)


def build_payload(
    program: str | None, checks: dict[str, dict[str, str]], issues: list[str]
) -> dict[str, Any]:
    violated_rules = [
        rule for rule, result in sorted(checks.items()) if result["status"] != "satisfied"
    ]
    valid = not violated_rules
    formal_feedback = (
        "Strategy3-safe rewrite accepted."
        if valid
        else "Strategy3-safe rewrite required. Violated rules: "
        + ", ".join(violated_rules)
        + ". "
        + " ".join(issues)
    )
    return {
        "program": program,
        "valid": valid,
        "classification": "L1-pseries-ratio-balance" if valid else "rejected",
        "checks": checks,
        "violated_rules": violated_rules,
        "issues": issues,
        "formal_feedback": formal_feedback,
        "repair_guidance": SAFE_REPAIR_GUIDANCE,
        "repair_template": SAFE_STRATEGY3_REPAIR_TEMPLATE,
    }


def audit_path(
    path: Path,
    *,
    min_generation: int | None = None,
    exclude_code_hashes: set[str] | None = None,
) -> dict[str, Any]:
    root = path.resolve()
    candidates = [audit_candidate(candidate, root) for candidate in candidate_sources(root)]
    violated_rule_counts: Counter[str] = Counter()
    for candidate in candidates:
        violated_rule_counts.update(candidate["violated_rules"])

    valid_count = sum(1 for candidate in candidates if candidate["valid"])
    return {
        "root": str(root),
        "total": len(candidates),
        "valid_count": valid_count,
        "invalid_count": len(candidates) - valid_count,
        "violated_rule_counts": dict(sorted(violated_rule_counts.items())),
        "selection_policy": selection_policy(min_generation, exclude_code_hashes),
        "best_valid_candidate": best_valid_candidate(
            candidates,
            min_generation=min_generation,
            exclude_code_hashes=exclude_code_hashes,
        ),
        "candidates": candidates,
    }


def audit_candidate(candidate: dict[str, Any], root: Path) -> dict[str, Any]:
    result = analyze_source(candidate["code"], program=candidate["path"])
    issues = result.get("issues", [])
    return {
        "path": display_path(Path(candidate["path"]), root),
        "source": candidate["source"],
        "id": candidate.get("id"),
        "score": candidate.get("score"),
        "generation": candidate.get("generation"),
        "parent_id": candidate.get("parent_id"),
        "iteration_found": candidate.get("iteration_found"),
        "code_hash": source_hash(candidate["code"]),
        "valid": result["valid"],
        "classification": result["classification"],
        "violated_rules": result["violated_rules"],
        "first_issue": issues[0] if issues else None,
        "formal_feedback": result["formal_feedback"],
    }


def candidate_sources(root: Path) -> list[dict[str, Any]]:
    files = [root] if root.is_file() else sorted(root.rglob("*"))
    candidates: list[dict[str, Any]] = []
    for path in files:
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix == ".py":
            candidates.append(
                {"path": str(path), "source": "python", "code": path.read_text(encoding="utf-8")}
            )
        elif path.suffix == ".json":
            candidate = json_candidate(path)
            if candidate is not None:
                candidates.append(candidate)
    return candidates


def json_candidate(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    code = payload.get("code") if isinstance(payload, dict) else None
    if not isinstance(code, str):
        return None
    return {
        "path": str(path),
        "source": "json.code",
        "code": code,
        "id": payload.get("id"),
        "score": extract_score(payload),
        "generation": payload.get("generation"),
        "parent_id": payload.get("parent_id"),
        "iteration_found": payload.get("iteration_found"),
    }


def extract_score(payload: dict[str, Any]) -> float | None:
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        return None
    score = metrics.get("combined_score")
    if isinstance(score, (int, float)):
        return float(score)
    nested = metrics.get("metrics")
    if isinstance(nested, dict):
        nested_score = nested.get("combined_score")
        if isinstance(nested_score, (int, float)):
            return float(nested_score)
    return None


def best_valid_candidate(
    candidates: list[dict[str, Any]],
    *,
    min_generation: int | None = None,
    exclude_code_hashes: set[str] | None = None,
) -> dict[str, Any] | None:
    valid = [
        candidate
        for candidate in candidates
        if candidate["valid"]
        and candidate_is_selectable(
            candidate,
            min_generation=min_generation,
            exclude_code_hashes=exclude_code_hashes,
        )
    ]
    if not valid:
        return None
    best = max(
        valid,
        key=lambda candidate: (
            score_sort_key(candidate),
            generation_sort_key(candidate),
            candidate["path"],
        ),
    )
    return {
        "path": best["path"],
        "source": best["source"],
        "id": best.get("id"),
        "score": best.get("score"),
        "generation": best.get("generation"),
        "parent_id": best.get("parent_id"),
        "iteration_found": best.get("iteration_found"),
        "code_hash": best.get("code_hash"),
        "classification": best["classification"],
        "formal_feedback": best["formal_feedback"],
    }


def selection_policy(
    min_generation: int | None,
    exclude_code_hashes: set[str] | None,
) -> dict[str, Any]:
    return {
        "min_generation": min_generation,
        "excluded_code_hashes": sorted(exclude_code_hashes or []),
    }


def source_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def hash_program(path: Path) -> str:
    return source_hash(path.read_text(encoding="utf-8"))


def excluded_hashes(paths: list[str] | None) -> set[str]:
    return {hash_program(Path(path).resolve()) for path in paths or []}


def candidate_is_selectable(
    candidate: dict[str, Any],
    *,
    min_generation: int | None = None,
    exclude_code_hashes: set[str] | None = None,
) -> bool:
    if min_generation is not None:
        generation = candidate.get("generation")
        if not isinstance(generation, int) or generation < min_generation:
            return False
    if exclude_code_hashes and candidate.get("code_hash") in exclude_code_hashes:
        return False
    return True


def score_sort_key(candidate: dict[str, Any]) -> float:
    score = candidate.get("score")
    return float(score) if isinstance(score, (int, float)) else float("-inf")


def generation_sort_key(candidate: dict[str, Any]) -> int:
    generation = candidate.get("generation")
    return generation if isinstance(generation, int) else -1


def summary_report(report: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in report.items() if key != "candidates"}


def select_best_valid_source(
    path: Path,
    *,
    min_generation: int | None = None,
    exclude_code_hashes: set[str] | None = None,
) -> dict[str, Any] | None:
    root = path.resolve()
    best: tuple[tuple[float, str], dict[str, Any], dict[str, Any]] | None = None
    for candidate in candidate_sources(root):
        audited = audit_candidate(candidate, root)
        if not audited["valid"]:
            continue
        if not candidate_is_selectable(
            audited,
            min_generation=min_generation,
            exclude_code_hashes=exclude_code_hashes,
        ):
            continue
        key = (score_sort_key(audited), generation_sort_key(audited), audited["path"])
        if best is None or key > best[0]:
            best = (key, candidate, audited)
    if best is None:
        return None
    return {"code": best[1]["code"], "candidate": best[2]}


def exploratory_candidates(
    path: Path,
    *,
    min_generation: int | None = None,
    exclude_code_hashes: set[str] | None = None,
    top_n: int = 10,
) -> dict[str, Any]:
    root = path.resolve()
    rows: list[dict[str, Any]] = []
    for candidate in candidate_sources(root):
        audited = audit_candidate(candidate, root)
        if not candidate_is_selectable(
            audited,
            min_generation=min_generation,
            exclude_code_hashes=exclude_code_hashes,
        ):
            continue
        rows.append(
            {
                **audited,
                "static_gate_status": "strict_pass" if audited["valid"] else "strict_fail",
                "proof_route": "strict-template" if audited["valid"] else "exploratory-coding-agent",
            }
        )
    rows.sort(
        key=lambda candidate: (
            score_sort_key(candidate),
            generation_sort_key(candidate),
            candidate["path"],
        ),
        reverse=True,
    )
    return {
        "ok": bool(rows),
        "status": "exploration_ready" if rows else "no_candidates",
        "root": str(root),
        "total_candidates_seen": len(candidate_sources(root)),
        "selection_policy": selection_policy(min_generation, exclude_code_hashes),
        "top_n": top_n,
        "candidates": rows[:top_n],
        "workflow": {
            "mode": "soft-gate",
            "round_budget_default": 5,
            "time_budget_minutes_default": 30,
            "final_acceptance": "Lean must compile without sorry/admit/new axiom; otherwise preserve the minimal failing Lean fragment.",
        },
    }


def render_lean_candidate(program: Path, output: Path) -> dict[str, Any]:
    payload = analyze_program(program.resolve())
    output = output.resolve()
    payload["lean_file"] = str(output)
    if not payload["valid"]:
        return payload
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(LEAN_TEMPLATE, encoding="utf-8")
    return payload


def verify_lean(project_root: Path, lean_file: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    lean_file = lean_file.resolve()
    try:
        rel = lean_file.relative_to(project_root)
    except ValueError:
        rel = lean_file
    proc = subprocess.run(
        ["lake", "env", "lean", str(rel)],
        cwd=project_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "project_root": str(project_root),
        "lean_file": str(lean_file),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def certify_best(
    openevolve_output: Path | str,
    project_root: Path | str,
    candidate_output: Path | str,
    lean_output: Path | str,
    *,
    min_generation: int | None = None,
    exclude_code_hashes: set[str] | None = None,
) -> dict[str, Any]:
    openevolve_output = Path(openevolve_output)
    candidate_output = Path(candidate_output).resolve()
    lean_output = Path(lean_output).resolve()

    audit = audit_path(
        openevolve_output,
        min_generation=min_generation,
        exclude_code_hashes=exclude_code_hashes,
    )
    selection = select_best_valid_source(
        openevolve_output,
        min_generation=min_generation,
        exclude_code_hashes=exclude_code_hashes,
    )
    payload: dict[str, Any] = {
        "ok": False,
        "stage": "audit",
        "audit": summary_report(audit),
        "selection_policy": selection_policy(min_generation, exclude_code_hashes),
        "candidate_file": str(candidate_output),
        "lean_file": str(lean_output),
    }
    if selection is None:
        payload["written_best"] = None
        return payload

    candidate_output.parent.mkdir(parents=True, exist_ok=True)
    candidate_output.write_text(selection["code"], encoding="utf-8")
    payload["written_best"] = {"output": str(candidate_output), "candidate": selection["candidate"]}

    render_payload = render_lean_candidate(candidate_output, lean_output)
    payload["lean_render"] = render_payload
    if not render_payload["valid"]:
        payload["stage"] = "render-lean"
        return payload

    verify_payload = verify_lean(Path(project_root), lean_output)
    payload["lean_verify"] = verify_payload
    payload["stage"] = "complete" if verify_payload["ok"] else "verify-lean"
    payload["ok"] = verify_payload["ok"]
    return payload


def display_path(path: Path, root: Path) -> str:
    base = root if root.is_dir() else root.parent
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def write_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_inspect(args: argparse.Namespace) -> int:
    payload = analyze_program(Path(args.program).resolve())
    if args.json:
        write_json(payload)
    else:
        print("valid:", payload["valid"])
        print("classification:", payload["classification"])
        for issue in payload["issues"]:
            print("issue:", issue)
    return 0 if payload["valid"] else 2


def command_audit(args: argparse.Namespace) -> int:
    exclude_hashes = excluded_hashes(args.exclude_program)
    payload = audit_path(
        Path(args.path),
        min_generation=args.min_generation,
        exclude_code_hashes=exclude_hashes,
    )
    if args.write_best:
        selection = select_best_valid_source(
            Path(args.path),
            min_generation=args.min_generation,
            exclude_code_hashes=exclude_hashes,
        )
        if selection is None:
            payload["written_best"] = None
            if args.json:
                write_json(summary_report(payload) if args.summary_only else payload)
            return 2
        output = Path(args.write_best).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(selection["code"], encoding="utf-8")
        payload["written_best"] = {"output": str(output), "candidate": selection["candidate"]}
        if args.json:
            write_json(summary_report(payload) if args.summary_only else payload)
        else:
            print(output)
        return 0
    if args.json:
        write_json(summary_report(payload) if args.summary_only else payload)
    else:
        print("total:", payload["total"])
        print("valid:", payload["valid_count"])
        print("invalid:", payload["invalid_count"])
        for rule, count in payload["violated_rule_counts"].items():
            print(f"{rule}: {count}")
    return 0 if payload["invalid_count"] == 0 else 2


def command_explore(args: argparse.Namespace) -> int:
    exclude_hashes = excluded_hashes(args.exclude_program)
    payload = exploratory_candidates(
        Path(args.path),
        min_generation=args.min_generation,
        exclude_code_hashes=exclude_hashes,
        top_n=args.top_n,
    )
    if args.json:
        write_json(payload)
    else:
        print("status:", payload["status"])
        for candidate in payload["candidates"]:
            print(
                candidate["path"],
                "score=",
                candidate.get("score"),
                "generation=",
                candidate.get("generation"),
                "route=",
                candidate["proof_route"],
            )
    return 0 if payload["ok"] else 2


def command_render_lean(args: argparse.Namespace) -> int:
    program = Path(args.program).resolve()
    output = Path(args.output).resolve()
    payload = render_lean_candidate(program, output)
    if not payload["valid"]:
        if args.json:
            write_json(payload)
        else:
            print("Candidate is not Strategy3-safe; refusing to render Lean.", file=sys.stderr)
        return 2
    if args.json:
        write_json(payload)
    else:
        print(output)
    return 0


def command_verify(args: argparse.Namespace) -> int:
    payload = verify_lean(Path(args.project_root), Path(args.lean_file))
    if args.json:
        write_json(payload)
    else:
        if payload["stdout"]:
            sys.stdout.write(payload["stdout"])
        if payload["stderr"]:
            sys.stderr.write(payload["stderr"])
    return int(payload["returncode"])


def command_certify_best(args: argparse.Namespace) -> int:
    exclude_hashes = excluded_hashes(args.exclude_program)
    payload = certify_best(
        args.openevolve_output,
        args.project_root,
        args.candidate_output,
        args.lean_output,
        min_generation=args.min_generation,
        exclude_code_hashes=exclude_hashes,
    )
    if args.report_output:
        report = Path(args.report_output).resolve()
        report.parent.mkdir(parents=True, exist_ok=True)
        payload["report_file"] = str(report)
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        write_json(payload)
    else:
        print("ok:", payload["ok"])
        print("stage:", payload["stage"])
        print("candidate:", payload["candidate_file"])
        print("lean:", payload["lean_file"])
    return 0 if payload["ok"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="Check a Python update_rho candidate against R1-R7.")
    inspect.add_argument("--program", required=True)
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=command_inspect)

    audit = sub.add_parser("audit", help="Audit Python and JSON-code candidates under a path.")
    audit.add_argument("--path", required=True)
    audit.add_argument("--write-best", help="Write the highest-scoring valid candidate source here.")
    audit.add_argument("--summary-only", action="store_true", help="Omit the full candidate list.")
    audit.add_argument("--min-generation", type=int, help="Select only candidates with generation >= this value.")
    audit.add_argument(
        "--exclude-program",
        action="append",
        help="Exclude candidates whose source is identical to this Python file when selecting best.",
    )
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(func=command_audit)

    explore = sub.add_parser(
        "explore",
        help="Rank candidates for coding-agent proof attempts without treating R1-R7 as a hard gate.",
    )
    explore.add_argument("--path", required=True)
    explore.add_argument("--top-n", type=int, default=10)
    explore.add_argument("--min-generation", type=int, help="Select only candidates with generation >= this value.")
    explore.add_argument(
        "--exclude-program",
        action="append",
        help="Exclude candidates whose source is identical to this Python file when ranking.",
    )
    explore.add_argument("--json", action="store_true")
    explore.set_defaults(func=command_explore)

    render = sub.add_parser("render-lean", help="Render the supported Strategy3 Lean template.")
    render.add_argument("--program", required=True)
    render.add_argument("--output", required=True)
    render.add_argument("--json", action="store_true")
    render.set_defaults(func=command_render_lean)

    verify = sub.add_parser("verify-lean", help="Run lake env lean on a generated Lean file.")
    verify.add_argument("--project-root", required=True)
    verify.add_argument("--lean-file", required=True)
    verify.add_argument("--json", action="store_true")
    verify.set_defaults(func=command_verify)

    certify = sub.add_parser(
        "certify-best",
        help="Audit, write the best Strategy3-safe candidate, render Lean, and verify it.",
    )
    certify.add_argument("--openevolve-output", required=True)
    certify.add_argument("--project-root", required=True)
    certify.add_argument("--candidate-output", required=True)
    certify.add_argument("--lean-output", required=True)
    certify.add_argument("--report-output", help="Write the full certificate JSON to this file.")
    certify.add_argument("--min-generation", type=int, help="Select only candidates with generation >= this value.")
    certify.add_argument(
        "--exclude-program",
        action="append",
        help="Exclude candidates whose source is identical to this Python file when selecting best.",
    )
    certify.add_argument("--json", action="store_true")
    certify.set_defaults(func=command_certify_best)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
