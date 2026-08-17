/-
# DvdTrans — 评测 Fixture（整除传递）

**角色**：真 API 短跑靶；Formalize 已对齐 mathlib 4.28，证明留 `sorry` 给 agent 补全。
**勿** import 进 `StatInferenceLean.lean` 根模块（与 Bernoulli / ErrorBank fixtures 策略一致）。
验证：`lake env lean StatInferenceLean/Exercises/Fixtures/DvdTrans.lean`

mathlib 4.28 标准陈述（不要从零重写整除教材）：
- `dvd_trans`：`a ∣ b → b ∣ c → a ∣ c`
  （`Mathlib.Algebra.Divisibility.Basic`）

本文件目标与 `dvd_trans` 对齐（限制到 `ℤ`）。允许 `exact` / `apply` 已有 mathlib 定理。
-/
import Mathlib.Algebra.Divisibility.Basic
import Mathlib.Data.Int.Basic
import Mathlib.Algebra.Ring.Int.Defs

namespace StatInferenceLean
namespace Exercises

/--
【ZH】整数 \(a\mid b\) 且 \(b\mid c\) 则 \(a\mid c\)。

【EN】Divisibility of integers is transitive.

【DB】topic: Transitivity of divisibility
【DB】object: `a b c : ℤ`
【DB】result: `a ∣ c`
【DB】mathlib: `dvd_trans`
-/
theorem dvd_trans_int {a b c : ℤ} (hab : a ∣ b) (hbc : b ∣ c) : a ∣ c := by
  exact dvd_trans hab hbc

end Exercises
end StatInferenceLean
