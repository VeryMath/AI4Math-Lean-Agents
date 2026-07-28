import Mathlib
import StatInferenceLean.Basic
import StatInferenceLean.Probability.Defs

namespace StatInferenceLean
namespace Exercises

/-!
# ErrorBankDemo.broken — 故意失败 Fixture

**角色**：Error Bank / tier0 可修类演示。  
**期望错误**：`unknown identifier 'sampleMean'`（未使用 `Probability.` 限定，也未 `open Probability`）。  
**勿** import 进 `StatInferenceLean.lean`（否则 `lake build` 失败）。

对照正确文件：`ErrorBankDemo.fixed.lean`。
-/

/-- 故意使用未限定的 `sampleMean`，触发 unknown identifier。 -/
theorem error_demo : sampleMean ([] : List ℝ) = 0 := by
  simp [sampleMean]

end Exercises
end StatInferenceLean
