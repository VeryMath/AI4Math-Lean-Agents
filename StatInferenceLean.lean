/-
Root module for `lake build`.
Intentionally NOT imported here:
- Exercises.Bernoulli — regression via `lake env lean` only
- Exercises.Fixtures.ErrorBankDemo.broken — would break the build
- Exercises.Fixtures.ErrorBankDemo.fixed — verify via `lake env lean` / REGRESSION.md
-/
import StatInferenceLean.Basic
import StatInferenceLean.Probability.Defs
import StatInferenceLean.Statistics.Estimator
import StatInferenceLean.Exercises.Week01
import StatInferenceLean.Exercises.Week02
import StatInferenceLean.Exercises.InteractiveDemo
