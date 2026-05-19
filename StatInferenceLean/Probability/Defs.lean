import Mathlib

namespace StatInferenceLean
namespace Probability

/-- A tiny wrapper for beginner stage: random variable over a sample type. -/
abbrev RV (Ω : Type) := Ω → Real

/-- A simple finite-sample mean for exercises.
This is intentionally elementary before moving to measure-theoretic expectation. -/
noncomputable def sampleMean (xs : List Real) : Real :=
  if xs.length = 0 then 0 else xs.sum / xs.length

example : sampleMean [] = 0 := by
  simp [sampleMean]

end Probability
end StatInferenceLean
