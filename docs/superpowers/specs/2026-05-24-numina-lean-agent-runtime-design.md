# Numina Lean Agent Runtime Skill Design

## Context

The current `ai4math-lean-agents` skill is intentionally a distilled, direct Lean coding-agent workflow. It uses the public Numina workflow as design provenance, but it does not deploy Numina, require Claude Code, call model APIs, or treat Numina as a proof backend.

The new work adds a separate sister skill for users who explicitly want the opposite mode: fetch the official upstream Numina Lean Agent, configure a local runtime environment, and invoke the upstream runner.

## Goal

Create a new skill named `numina-lean-agent-runtime` that guides Codex through local deployment and invocation of the official `project-numina/numina-lean-agent` repository.

The skill must:

- clone or update the official upstream repository locally;
- configure required local tools and Python dependencies;
- run the upstream setup flow for a named Lean project;
- diagnose missing tools, project layout problems, and API-key gaps before long runs;
- invoke upstream `scripts.run_claude` commands for `run`, `batch`, and `from-folder` tasks;
- keep this runtime workflow separate from `ai4math-lean-agents`.

## Non-Goals

- Do not vendor, fork, or modify Numina source code by default.
- Do not make `ai4math-lean-agents` depend on Numina.
- Do not claim offline or key-free operation.
- Do not hide that upstream Numina may call Claude, external services, or third-party CLI skills.
- Do not store secrets in tracked files.

## Proposed Repository Layout

```text
skills/
  AI4Math-Lean-Agents/
  Numina-Lean-Agent-Runtime/
    SKILL.md
    agents/
      openai.yaml
    config/
      numina_runtime.example.toml
    references/
      upstream_usage.md
    scripts/
      numina_runtime.py
    tests/
      test_numina_runtime.py
```

Use `Numina-Lean-Agent-Runtime/` as the package folder name to match the existing repository style. Use `numina-lean-agent-runtime` as the skill name in frontmatter and docs.

## Runtime State

Runtime state lives under `.ai4math/numina-runtime/` by default and must be ignored by git.

```text
.ai4math/
  numina-runtime/
    upstream/            # cloned official project-numina/numina-lean-agent
    projects/            # optional project workspace root used by setup.sh
    results/             # default wrapper result root
    .env.local           # optional local environment overrides, not tracked
    numina_runtime.local.toml
```

The wrapper must respect these environment variables:

- `AI4MATH_NUMINA_HOME`: override runtime root.
- `NUMINA_LEAN_AGENT_REPO`: override upstream URL only when the user explicitly requests it.
- `NUMINA_LEAN_AGENT_REF`: optional branch, tag, or commit to check out.

The default upstream URL is `https://github.com/project-numina/numina-lean-agent`.

## CLI Wrapper

`scripts/numina_runtime.py` provides a deterministic wrapper around upstream setup and runner commands.

### `doctor`

Report JSON with:

- tool availability: `git`, `curl`, `uv`, `elan`, `lean`, `lake`, `claude`, `python`;
- upstream clone status and current commit;
- Python environment status;
- required and optional API key presence, redacted;
- whether a target path is inside a Lake project when a target is supplied.

`doctor` must not call external model APIs.

Credential diagnostics must distinguish:

- Claude configuration: `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, and `ANTHROPIC_MODEL`, or an already authenticated `claude` CLI;
- Numina skill keys: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `LEAN_LEANDEX_API_KEY`, and `AXLE_API_KEY`;
- optional keys from required keys, because upstream Numina only needs some keys for specific backends or tools.

### `install`

Clone or update upstream Numina into `.ai4math/numina-runtime/upstream`.

Default behavior:

- clone when missing;
- fetch when present;
- checkout `NUMINA_LEAN_AGENT_REF` only when configured;
- avoid overwriting local upstream modifications without reporting them.

The first version must include `--dry-run`, returning the clone/fetch/checkout commands without running them.

### `configure`

Run upstream setup for a named Lean project:

```bash
python scripts/numina_runtime.py configure --project-name myproofs
```

The wrapper should:

- ensure upstream is installed;
- run `tutorial/setup.sh <project-name>` from the upstream `tutorial/` directory;
- run `uv python install` and `uv sync` from the upstream root when `uv` is available;
- record paths and status in local JSON/TOML metadata;
- return clear next steps when `claude`, API keys, Lean, or Lake setup is missing.

`configure` runs dependency sync by default and supports `--skip-sync` for users who only want the upstream project scaffold step.

### `run`

Invoke upstream single-target mode:

```bash
python scripts/numina_runtime.py run \
  --target /path/to/Foo.lean \
  --prompt-file /path/to/prompt.md \
  --max-rounds 10
```

Before launching upstream Numina, validate:

- the target exists;
- the target is inside a Lake project with `lean-toolchain` and `lakefile.lean` or `lakefile.toml`;
- a prompt or prompt file is available;
- upstream installation and Python environment are present.

The actual upstream command should be equivalent to:

```bash
python -m scripts.run_claude run <target> --prompt-file <prompt-file> --max-rounds <n> --result-dir <dir>
```

### `from-folder`

Invoke upstream folder scanning mode:

```bash
python scripts/numina_runtime.py from-folder \
  --target /path/to/LeanFolder \
  --prompt-file prompts/autosearch/main_entry.md \
  --max-rounds 10
```

The wrapper should provide a default result directory under `.ai4math/numina-runtime/results/` if the user does not supply one.

### `batch`

Pass through to upstream batch mode for YAML or JSON configs:

```bash
python scripts/numina_runtime.py batch --config /path/to/config.yaml
```

The wrapper should validate the config file exists and then invoke upstream `python -m scripts.run_claude batch`.

## Skill Behavior

The skill body should guide Codex to:

1. Confirm the user wants official Numina runtime mode, not the distilled direct Lean workflow.
2. Run `doctor` before installation or invocation.
3. Use `install` to fetch upstream.
4. Use `configure` for first-time setup.
5. Validate the target Lake project before `run`, `batch`, or `from-folder`.
6. Report missing credentials without printing secret values.
7. Treat upstream runner output and result directories as the source of truth.
8. Fall back to `ai4math-lean-agents` only when the user chooses direct local Lean repair instead of official Numina runtime.

## Error Handling

The wrapper should return machine-readable JSON for all commands.

Common statuses:

- `ready`: local runtime is usable.
- `missing_tool`: required executable is unavailable.
- `missing_upstream`: upstream repo has not been cloned.
- `upstream_dirty`: upstream checkout has local modifications.
- `missing_credentials`: model or skill API keys are absent.
- `missing_lake_project`: target is not inside a Lake project.
- `setup_failed`: upstream setup or dependency sync failed.
- `run_failed`: upstream runner exited nonzero.

Human-facing diagnostics should explain the next concrete command.

## Secrets and Local Files

Tracked files may include only examples such as:

```text
config/numina_runtime.example.toml
```

Local files must be ignored:

```text
.ai4math/numina-runtime/
```

The wrapper must read `.ai4math/numina-runtime/.env.local` when present, redact values in output, and never write user-provided secrets unless the user explicitly asks.

## Tests

Default tests must be offline and deterministic.

Required unit coverage:

- Lake project root detection.
- command construction for `install`, `configure`, `run`, `from-folder`, and `batch`;
- missing tool diagnostics;
- missing upstream diagnostics;
- dirty upstream protection;
- key redaction;
- default path resolution under `.ai4math/numina-runtime`;
- JSON output shape.

Do not clone upstream, run `uv sync`, call `claude`, or call external APIs in default tests.

Optional integration tests may be gated by an environment variable such as `AI4MATH_NUMINA_INTEGRATION=1`.

## Validation

The implementation is acceptable when:

- the new skill passes skill validation;
- repository unit tests pass;
- wrapper offline tests pass without network or API keys;
- `doctor` works on a fresh checkout and reports missing runtime state cleanly;
- `install --dry-run` or equivalent command construction test proves the official upstream URL is used;
- existing `ai4math-lean-agents` delivery verification still passes.

## Implementation Decisions

- `install --dry-run` is required in the first version.
- `.env.local` loading belongs in the wrapper, with redacted reporting.
- `configure` runs `uv sync` by default and supports `--skip-sync`.
- Validation remains per skill; do not add a repository-level `verify-all` helper in the first version.
