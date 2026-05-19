import Mathlib
import StatInferenceLean.Basic
import StatInferenceLean.Probability.Defs
import StatInferenceLean.Statistics.Estimator

namespace StatInferenceLean
namespace Exercises

/-!
# Week 01 — 入门练习 / Week 01 — Getting started

## 本文件在做什么？ / What is this file?

- **中文**：用极小的例子练习 Lean 的基本写法：如何陈述命题、如何写证明、
  常用战术（tactic）长什么样。
- **English**: Tiny examples to practice stating propositions, writing proofs, and reading common
  tactics.

## 阅读方式 / How to read

- 把光标放在 `by` **后面**一行，查看 **Info / Goal** 面板里「当前要证明的目标」。
- Place the cursor **after** `by` to see the **current goal** in the Info / Goal view.

## 符号速查 / Notation cheat sheet

| Lean | 含义（中） | Meaning (EN) |
|------|------------|--------------|
| `Prop` | 命题类型 | type of propositions |
| `Real` 或 `ℝ` | 实数（Mathlib） | real numbers |
| `by ...` | 进入战术模式 | enter tactic mode |
| `example` | 无名定理，仅用于练习 | unnamed lemma for exercises |
| `theorem` | 命名定理 | named theorem |
-/

/-!
## 导入说明 / About these imports

- **中文**：`Mathlib` 提供实数、列表等基础设施；后面三行引入本项目中已写好的定义
  （样本均值、估计量等）。
- **English**: `Mathlib` supplies reals, lists, etc.; the next imports pull in this project's
  definitions (`sampleMean`, estimators, …).
-/

/-!
------------------------------------------------------------------------------
### Example 1 — 逻辑析取 “或” / Disjunction OR

**中文**
- 已知 `P` 成立，要证 `P ∨ Q`（读作「P 或 Q」）。
- 思路：析取 introduction，选左边一支，用 `Or.inl` 把 `P` 的证明包装成 `P ∨ Q`。

**English**
- From `hP : P`, prove `P ∨ Q`.
- Idea: disjunction introduction on the left: `Or.inl` turns a proof of `P` into a proof of `P ∨ Q`.

**战术 / Tactics**
- `exact t`：当前目标恰好是 `t` 的类型时，用这一项结束证明。
- `exact t`: close the goal when its type matches `t` exactly.
-/

example (P Q : Prop) (hP : P) : P ∨ Q := by
  -- exact: 直接给出整个证明项 / give the proof term in one shot
  exact Or.inl hP

/-!
------------------------------------------------------------------------------
### Example 2 — 等式重写 / Rewriting with an equality

**中文**
- 假设 `a = b`，要证 `a + a = b + b`。
- 思路：把式子里的 `a` 全部换成 `b`（或反过来），再用等式自反性。

**English**
- Assume `a = b`, show `a + a = b + b`.
- Idea: replace `a` with `b` using the equality.

**战术 / Tactics**
- `rw [h]`：按等式 `h` 从左到右重写。
- `rw [h]`: rewrite using `h` (left-to-right by default).
-/

example (a b : Real) (h : a = b) : a + a = b + b := by
  rw [h]

/-!
------------------------------------------------------------------------------
### Example 3 — 化简 / Simplification

**中文**
- 对任意实数 `x`，证明 `x + 0 = x`。
- 这是加法零元的定律；`simp` 会尝试用内置的化简规则自动处理。

**English**
- For any real `x`, show `x + 0 = x` (additive identity).
- `simp` tries standard simplification lemmas automatically.

**战术 / Tactics**
- `simp`：自动化简（可带额外引理列表，如 `simp [lemma1, lemma2]`）。
- `simp`: simplify using the default (and optional extra) lemma set.
-/

example (x : Real) : x + 0 = x := by
  simp

/-!
------------------------------------------------------------------------------
### Example 4 — 重写 + 环战术 / Rewrite + ring

**中文**
- 若 `x = y`，则 `x - y = 0`。
- 先把 `x` 换成 `y`，得到 `y - y`，再用环上的一般代数推理。

**English**
- If `x = y`, then `x - y = 0`.
- First `rw` with `x = y`, then `ring` solves the algebraic goal in commutative rings.

**战术 / Tactics**
- `ring`：在交换环（如实数）上证明等式，适合多项式型等式。
- `ring`: prove ring equalities; good for polynomial-like goals over `ℝ`.
-/

example (x y : Real) (hxy : x = y) : x - y = 0 := by
  rw [hxy]
  ring

/-!
------------------------------------------------------------------------------
### Example 5 — 样本均值（数值实例）/ Sample mean (numeric instance)

**中文**
- `Probability.sampleMean` 定义在 `Probability/Defs.lean`：有限列表的样本均值。
- 这里验证具体数：`[2, 4]` 的均值是 `3`。
- `simp` 展开定义后，`norm_num` 对具体数字做归一化计算。

**English**
- `Probability.sampleMean` is defined in `Probability/Defs.lean` as the mean of a finite list.
- Check: the mean of `[2, 4]` is `3`.
- After `simp` unfolds the definition, `norm_num` normalizes numeric expressions.

**注意 / Note**
- 实数上的 `sampleMean` 是 **noncomputable**（不可执行），所以不能用 `native_decide`；用 `simp` + `norm_num` 证明。
- On `ℝ`, `sampleMean` is **noncomputable**, so we prove with `simp` + `norm_num`,
  not `#eval` / `native_decide`.

**战术 / Tactics**
- `simp [Name]`：化简时额外使用某定义的展开规则。
- `norm_num`：处理具体自然数、有理数、实数字面量等算术目标。
- `simp [Name]`: include extra definitions for unfolding.
- `norm_num`: solve goals involving numeric literals.
-/

example : Probability.sampleMean [2, 4] = 3 := by
  simp [Probability.sampleMean]
  norm_num

/-!
------------------------------------------------------------------------------
### Example 6 — 估计量与样本均值一致 / Estimator agrees with sample mean

**中文**
- `Statistics.meanEstimator` 在本项目中就取成 `Probability.sampleMean`。
- 验证 `[2, 4, 6]` 的均值为 `4`。

**English**
- In this project, `meanEstimator` is defined as `sampleMean`.
- Check: mean of `[2, 4, 6]` is `4`.

**战术 / Tactics**
- 同时 `simp` 展开 `meanEstimator` 与 `sampleMean`，再用 `norm_num`。
- Unfold both names, then finish with `norm_num`.
-/

example : Statistics.meanEstimator [2, 4, 6] = 4 := by
  simp [Statistics.meanEstimator, Probability.sampleMean]
  norm_num

end Exercises

end StatInferenceLean
