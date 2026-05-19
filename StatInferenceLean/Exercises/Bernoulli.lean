import Mathlib.Probability.ProbabilityMassFunction.Constructions
import Mathlib.Probability.ProbabilityMassFunction.Integrals

namespace StatInferenceLean
namespace Exercises

/-!
【Topic】伯努利（Bernoulli）

为了让后续开发统计 agent 的“数据库/检索”更稳定，这个文件使用 mathlib 的标准伯努利 PMF：
- `PMF.bernoulli`（参数类型与 mathlib 一致）
- 配套的期望引理：`PMF.bernoulli_expectation`

后续你可以把更多统计量（方差、生成函数等）按同样风格加进来。
-/

/--
【ZH】在伯努利 PMF 下，随机变量 `cond b 1 0` 的期望等于 `p.toReal`。

【EN】The expectation of the Bernoulli PMF random variable `cond b 1 0` equals `p.toReal`.

【DB】topic: Bernoulli
【DB】object: `PMF.bernoulli`
【DB】params: `p : ℝ≥0`, `h : p ≤ 1`
【DB】result: `∫ b, cond b 1 0 ∂((PMF.bernoulli p h).toMeasure) = p.toReal`
-/
theorem bernoulli_expectation_is_p (p : NNReal) (h : p ≤ (1 : NNReal)) :
    ∫ b, cond b (1 : ℝ) (0 : ℝ) ∂((PMF.bernoulli p h).toMeasure) = p.toReal := by
  simpa using (PMF.bernoulli_expectation (p := p) h)

end Exercises
end StatInferenceLean
