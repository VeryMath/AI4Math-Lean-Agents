# Optional Official Numina Runtime

This skill can deploy and call the official `project-numina/numina-lean-agent` repository when the user wants the original Numina behavior. Treat it as an optional human-in-the-loop runtime, not as the default proof backend.

## Agent Flow

1. Clarify the user's intent: direct Lean repair, official Numina run, or a mix.
2. Run `doctor --cwd .` when useful and read the `numina` readiness block.
3. Explain what setup may do: clone the official repository, run `tutorial/setup.sh`, install or use `elan`, `lake`, `curl`, `uv`, and `claude`, and require model/API credentials for some tools.
4. After approval, run `configure --cwd . --setup-numina --project-name <name>`. Use `--dry-run` first when the user wants to review commands.
5. For an official run, call the upstream runner from `.ai4math/numina-runtime/upstream` using its documented interface, normally `uv run python -m scripts.run_claude from-folder <target> --prompt-file prompts/autosearch/main_entry.md --max-rounds <n> --result-dir <dir>`.
6. After Numina changes Lean files, use local `check`, `detect-sorry`, and `review` before accepting the patch.

## Local State

- Runtime root: `.ai4math/numina-runtime/`
- Upstream checkout: `.ai4math/numina-runtime/upstream/`
- Ignored credential file: `.ai4math/numina-runtime/.env.local`
- Suggested outputs: `.ai4math/numina-runtime/results/`

Do not commit runtime state, API keys, generated results, or local machine paths.

## Credentials

Claude Code authentication can come from the user's normal Claude login or environment variables such as `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, and `ANTHROPIC_MODEL`. Numina's CLI skills may also need `GEMINI_API_KEY`, `OPENAI_API_KEY`, `LEAN_LEANDEX_API_KEY`, or `AXLE_API_KEY`.

The helper readiness report redacts values and only reports whether keys appear configured.

## Boundary

The AI4Math skill still owns delivery quality. Official Numina may propose or edit proofs, but final acceptance requires local Lean/Lake validation and the usual patch safety checks: no `sorry`, no `admit`, no newly introduced `axiom`, and no theorem statement drift unless explicitly approved.
