/-
# OddSquareMod8 — 评测 Fixture（奇平方减 1 整除 8）

**角色**：真 API 短跑靶；Formalize 已对齐 mathlib 4.28，证明留 `sorry` 给 agent 补全。
**勿** import 进 `StatInferenceLean.lean` 根模块（与 Bernoulli / ErrorBank fixtures 策略一致）。
验证：`lake env lean StatInferenceLean/Exercises/Fixtures/OddSquareMod8.lean`

mathlib 4.28 标准陈述（不要从零重写同余教材）：
- `Int.eight_dvd_sq_sub_one_of_odd`：`Odd k → 8 ∣ k ^ 2 - 1`
  （`Mathlib.NumberTheory.Multiplicity`）
- 相关：`Int.sq_mod_four_eq_one_of_odd`（奇平方 ≡ 1 mod 4）

本文件目标与 `Int.eight_dvd_sq_sub_one_of_odd` 对齐。允许 `exact` / `apply` 已有 mathlib 定理。
-/
import Mathlib.NumberTheory.Multiplicity

namespace StatInferenceLean
namespace Exercises

/--
【ZH】任意奇整数的平方减 1 是 8 的倍数。

【EN】If an integer is odd, then 8 divides its square minus one.

【DB】topic: Odd squares modulo 8
【DB】object: `k : ℤ`
【DB】result: `8 ∣ k ^ 2 - 1`
【DB】mathlib: `Int.eight_dvd_sq_sub_one_of_odd`
-/
theorem odd_square_mod8 {k : ℤ} (hk : Odd k) : 8 ∣ k ^ 2 - 1 := by
  exact Int.eight_dvd_sq_sub_one_of_odd hk

end Exercises
end StatInferenceLean
