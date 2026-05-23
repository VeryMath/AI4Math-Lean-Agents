# Strategy3 Contract

Use this reference when deciding whether an evolved adaptive-ADMM `update_rho` rule can be connected to the existing Lean Strategy3 convergence proof.

## R1-R7

R1. `tau_k >= 0` for all `k`.

R2. `sum_k tau_k < infinity`.

R3. `tau_k` depends only on `k` and fixed constants. It must not depend on residuals, ratios, rho, counters, or mutable state.

R4. Eventually, every rho update is exactly one of:

- `rho_{k+1} = rho_k * (1 + tau_k)`
- `rho_{k+1} = rho_k / (1 + tau_k)`
- `rho_{k+1} = rho_k`

R5. Residuals may choose the branch, but the numeric factor must be exactly `(1 + tau_k)` or its reciprocal.

R6. No post-processing of rho is allowed: no clipping, projection, min/max bounds, smoothing, averaging, damping, or corrective factors.

R7. The rule must be deterministic and defined for all valid inputs.

## Acceptable L1 Shape

The currently supported Lean template accepts this exact `tau` shape:

```python
def tau(k, c=1.0, p=1.2):
    return c / ((k + 1.0) ** p)

def update_rho(rho, k, r_norm, s_norm, mu=3.0, c=1.0, p=1.2, eps=1e-12):
    t = tau(k, c, p)
    if r_norm > mu * max(s_norm, eps):
        return rho * (1.0 + t), t, "mul"
    elif s_norm > mu * max(r_norm, eps):
        return rho / (1.0 + t), t, "div"
    return rho, t, "keep"
```

Equivalent local assignments are acceptable if the rho update remains exactly the same.

Shifted or piecewise variants such as `if k < K0: return 0.0; return c / ((k - K0 + 1) ** p)` are mathematically plausible but are not accepted by the current checker because the generated Lean template would no longer be definitionally aligned with the Python candidate. Add a separate Lean template and tests before accepting them.

## Reject Immediately

Reject and return a minimal failure fragment when any of these appear:

- `factor = ...` where `factor` depends on residuals and `rho * factor` or `rho / factor` is used.
- `new_rho = max(min(new_rho, ...), ...)` or any other clipping.
- `tau` depends on `r_norm`, `s_norm`, residual ratios, rho, or mutable counters.
- The output mode is not exactly `"mul"`, `"div"`, or `"keep"`.
- The Lean file contains `sorry`, `admit`, or a new `axiom`.

## Evaluator Integration

In an OpenEvolve evaluator, run the deterministic Strategy3 gate before any API-backed math alignment, numerical ADMM simulation, or Lean generation. Invalid candidates should receive score `0.0` with artifacts containing:

- `formal_gate: deterministic_strategy3`
- `violated_rules`
- `issues`
- the full gate result under `strategy3_contract`

This prevents residual-dependent or clipped candidates from being rewarded because they run fast numerically.

Expose separate metrics so the search loop can distinguish failure modes:

- `formal_score`: `0.0` for deterministic/LLM formal rejection, `0.5` for Lean not auto-proven, `1.0` for Lean-proven.
- `numeric_score`: `0.0` when ADMM does not converge, otherwise `1 / iterations`.
- `combined_score`: `formal_score * numeric_score`.

Keep `combined_score` for OpenEvolve compatibility, but include the component scores in `metrics` so prompt feedback can steer both formal validity and convergence speed.

## Search Prompt Hardening

The evolutionary search prompt must explicitly block the common invalid mutations observed in AutoADMM runs:

- variable names such as `factor`, `scale`, `adjusted_t`, `base_factor`, or `max_change`;
- `tau` multiplied by residual ratios, logarithms of residual ratios, thresholds, or counters;
- clipping such as `max(min(new_rho, ...), ...)`, `np.clip`, projections, smoothing, averaging, damping, or post-update bounds;
- auxiliary outputs that are residual-dependent adjusted values.

Include a safe Strategy3 template in the prompt and tell the search loop that `formal_score` must become positive before `numeric_score` matters.
