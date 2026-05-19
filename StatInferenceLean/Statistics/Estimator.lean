import Mathlib
import StatInferenceLean.Probability.Defs

namespace StatInferenceLean
namespace Statistics

open Probability

/-- Statistic as a function from a finite sample to a real value. -/
abbrev Statistic := List Real → Real

/-- Estimator in this beginner project: same shape as a statistic.
Later we can index this by model parameters. -/
abbrev Estimator := Statistic

noncomputable def meanEstimator : Estimator := Probability.sampleMean

example : meanEstimator [1, 3] = 2 := by
  simp [meanEstimator, Probability.sampleMean]
  norm_num

example : meanEstimator [2, 4, 6] = 4 := by
  simp [meanEstimator, Probability.sampleMean]
  norm_num

end Statistics
end StatInferenceLean
