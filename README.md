# stat-inference-lean

Lean4 + mathlib learning project for statistical inference beginners.

## Project goal

This project follows *Statistical Inference* and focuses on:

1. Learn Lean while doing statistics examples.
2. Build reusable formal definitions and lemmas.
3. Move from tiny exercises to textbook-level statements.

## Folder layout

- `StatInferenceLean/Basic.lean`: tiny Lean basics and proof style warm-up.
- `StatInferenceLean/Probability/Defs.lean`: beginner probability definitions.
- `StatInferenceLean/Statistics/Estimator.lean`: statistic/estimator skeleton.
- `StatInferenceLean/Exercises/Week01.lean`: first-week guided exercises.
- `StatInferenceLean/Exercises/Week02.lean`: lists, finite sums, `linarith` / `omega`.
- `StatInferenceLean.lean`: root import file.

## Quick start (Cursor / VS Code terminal)

```powershell
cd d:\Lean\projects\stat-inference-lean
lake build
```

Open `StatInferenceLean/Exercises/Week01.lean` (then `Week02.lean`) and place the cursor inside
each proof to see goals in the Lean Infoview.

## Week 01 checklist (done when you finish the file)

- Read the first exercises in `Week01.lean`.
- Try to replace one `exact` proof with your own proof term.
- Use `#check` in scratch area to inspect symbols.
- Keep each proof small and compiling.

## Week 02 (current step)

- Open `StatInferenceLean/Exercises/Week02.lean`.
- Work through Examples 1–6, then read Example 7 (uses `field_simp` + `linarith`).

## Next milestones

- Week 03-04: connect to probability definitions in mathlib.
- Week 05+: formalize simple textbook propositions.
