/-
# InfinitelyManyPrimes — 评测 Fixture（素数无穷）

**角色**：真 API 短跑靶；Formalize 已对齐 mathlib 4.28，证明留 `sorry` 给 agent 补全。
**勿** import 进 `StatInferenceLean.lean` 根模块（与 Bernoulli / ErrorBank fixtures 策略一致）。
验证：`lake env lean StatInferenceLean/Exercises/Fixtures/InfinitelyManyPrimes.lean`

mathlib 4.28 标准陈述（不要从零重写 Euclid 长文）：
- Euclid 形式：`Nat.exists_infinite_primes (n : ℕ) : ∃ p, n ≤ p ∧ Nat.Prime p`
  （`Mathlib.Data.Nat.Prime.Infinite`）
- 集合形式：`Nat.infinite_setOf_prime : { p | Nat.Prime p }.Infinite`
  （`Mathlib.Data.Nat.PrimeFin`）

本文件目标与集合形式对齐。允许 `exact` / `apply` 已有 mathlib 定理。
-/
import Mathlib.Data.Nat.PrimeFin

namespace StatInferenceLean
namespace Exercises

/--
【ZH】素数有无穷多个：自然数中素数集合是无限集。

【EN】There are infinitely many primes: the set of prime natural numbers is infinite.

【DB】topic: Infinitude of primes
【DB】object: `{ p : ℕ | Nat.Prime p }`
【DB】result: `Set.Infinite`
【DB】mathlib: `Nat.infinite_setOf_prime`
-/
theorem infinitely_many_primes : { p : ℕ | Nat.Prime p }.Infinite := by
  exact Nat.infinite_setOf_prime

end Exercises
end StatInferenceLean
