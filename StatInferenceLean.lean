/-
Root module for `lake build`.
Intentionally NOT imported here:
- Exercises.Bernoulli — regression via `lake env lean` only
- Exercises.Fixtures.ErrorBankDemo.broken — would break the build
- Exercises.Fixtures.ErrorBankDemo.fixed — verify via `lake env lean` / REGRESSION.md
- Exercises.Fixtures.InfinitelyManyPrimes — 评测 Fixture；单独 `lake env lean`
- Exercises.Fixtures.StrictMonoComp / DvdTrans / EvenSquare / OddSquareMod8 — 评测 Fixture；单独 `lake env lean`
-/
import StatInferenceLean.Basic
import StatInferenceLean.Probability.Defs
import StatInferenceLean.Statistics.Estimator
import StatInferenceLean.Exercises.Week01
import StatInferenceLean.Exercises.Week02
import StatInferenceLean.Exercises.InteractiveDemo
