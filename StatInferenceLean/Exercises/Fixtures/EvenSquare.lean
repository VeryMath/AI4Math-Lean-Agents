/-
# EvenSquare — 评测 Fixture（偶数平方仍偶）

**角色**：真 API 短跑靶；Formalize 已对齐 mathlib 4.28，证明留 `sorry` 给 agent 补全。
**勿** import 进 `StatInferenceLean.lean` 根模块（与 Bernoulli / ErrorBank fixtures 策略一致）。
验证：`lake env lean StatInferenceLean/Exercises/Fixtures/EvenSquare.lean`

mathlib 4.28 标准陈述（不要从零重写奇偶教材）：
- `even_pow'`（`Mathlib.Algebra.Group.Int.Even`）：`n ≠ 0 → (Even (m ^ n) ↔ Even m)`，`m : ℤ`
- 泛 Semiring 的 `Even.pow_of_ne_zero` 在 `ℤ` 上会撞 `Add` 实例，不作为本靶的 `exact` 目标

本文件目标与「偶整数平方仍偶」对齐。允许 `exact` / `apply` 已有 mathlib 定理。
-/
import Mathlib.Algebra.Group.Int.Even

namespace StatInferenceLean
namespace Exercises

/--
【ZH】任意偶整数的平方仍是偶数。

【EN】The square of an even integer is even.

【DB】topic: Parity of even squares
【DB】object: `n : ℤ`
【DB】result: `Even (n ^ 2)`
【DB】mathlib: `even_pow'`
-/
theorem even_square {n : ℤ} (hn : Even n) : Even (n ^ 2) := by
  sorry

end Exercises
end StatInferenceLean
