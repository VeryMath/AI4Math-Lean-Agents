import Mathlib
import StatInferenceLean.Basic
import StatInferenceLean.Probability.Defs

namespace StatInferenceLean
namespace Exercises

/-!
# ErrorBankDemo.fixed — 正确对照 Fixture

**角色**：与 `ErrorBankDemo.broken.lean` 配对的正确证明。  
使用完整限定名 `Probability.sampleMean`，证明空列表样本均值为 0。

本文件可不挂根模块；回归用 `lake env lean` 单独验证。
-/

/-- 使用完整限定名调用 `Probability.sampleMean` 并证明空列表情况。 -/
theorem error_demo : Probability.sampleMean ([] : List ℝ) = 0 := by
  simp [Probability.sampleMean]

end Exercises
end StatInferenceLean
