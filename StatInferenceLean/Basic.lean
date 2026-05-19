import Mathlib

namespace StatInferenceLean

def hello : String := "world"

example (P Q : Prop) (hP : P) : P ∨ Q := by
  exact Or.inl hP

example (a b : Real) (h : a = b) : b = a := by
  simp [h]

end StatInferenceLean
