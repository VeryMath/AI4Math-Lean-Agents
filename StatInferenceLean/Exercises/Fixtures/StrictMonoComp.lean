/-
# StrictMonoComp — 评测 Fixture（严格单调复合）

**角色**：真 API 短跑靶；Formalize 已对齐 mathlib 4.28，证明留 `sorry` 给 agent 补全。
**勿** import 进 `StatInferenceLean.lean` 根模块（与 Bernoulli / ErrorBank fixtures 策略一致）。
验证：`lake env lean StatInferenceLean/Exercises/Fixtures/StrictMonoComp.lean`

mathlib 4.28 标准陈述（不要从零重写单调性教材）：
- `StrictMono.comp`：`StrictMono g → StrictMono f → StrictMono (g ∘ f)`
  （`Mathlib.Order.Monotone.Defs`）

本文件目标与 `StrictMono.comp` 对齐（限制到 `ℝ → ℝ`）。允许 `exact` / `apply` 已有 mathlib 定理。
-/
import Mathlib.Data.Real.Basic
import Mathlib.Order.Monotone.Defs

namespace StatInferenceLean
namespace Exercises

/--
【ZH】若 \(f,g:\mathbb{R}\to\mathbb{R}\) 都严格单调递增，则 \(g\circ f\) 也严格单调递增。

【EN】The composition of strictly monotone real functions is strictly monotone.

【DB】topic: Strict monotonicity of composition
【DB】object: `f g : ℝ → ℝ`
【DB】result: `StrictMono (g ∘ f)`
【DB】mathlib: `StrictMono.comp`
-/
theorem strict_mono_comp {f g : ℝ → ℝ} (hf : StrictMono f) (hg : StrictMono g) :
    StrictMono (g ∘ f) := by
  exact hg.comp hf

end Exercises
end StatInferenceLean
