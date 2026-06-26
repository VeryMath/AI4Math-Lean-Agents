# Backend Adapter Checklist

Use this checklist before claiming that a Lean-specialist backend is supported. Backend adapters are optional escalation paths; default coding-agent Lean work must not require any backend adapter.

## Support Status

- `supported`: setup, readiness checks, invocation, local validation, and failure triage are documented and guarded.
- `experimental`: partial adapter exists, but the agent must explain gaps and request approval before use.
- `future`: related work or candidate backend only; do not claim support or call it automatically.

Currently supported optional backend: official Numina Lean Agent runtime.

Future backend adapters may include Archon or other Lean-specialist systems, but do not claim support until deployment, readiness checks, invocation, validation, and failure triage are documented.

## Adapter Contract

Document all of the following before moving a backend out of `future`:

- Name, upstream source, license, and support status.
- Trigger phrases that justify using this backend.
- Setup location, install commands, network access, and local state written.
- Required tools, credentials, API keys, proxy settings, or MCP scope.
- Readiness checks that do not call external model APIs.
- Invocation command, working directory, target project/file/folder, prompt, result directory, and round limits.
- Mutation boundary: which files may be changed, where generated outputs go, and which actions require approval.
- Local validation gate: Lean/Lake check, `detect-sorry`, `review`, and theorem statement drift checks.
- Failure triage: auth, proxy, MCP, toolchain, runner, timeout, and fallback to the coding-agent path.

## Non-Claim Rule

Do not claim support for a backend adapter unless its setup, call, credential, mutation, and validation contracts are documented. Unimplemented adapters may be cited as related work or future adapters only.
