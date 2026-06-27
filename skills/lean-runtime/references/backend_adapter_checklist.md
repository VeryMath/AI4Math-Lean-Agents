# Backend Adapter Checklist

Use this checklist before connecting any Lean-specialist backend. Backend integration is adapter-first: default coding-agent Lean work must not require any backend adapter, and every backend call must pass through an explicit adapter contract.

## Support Status

- `supported`: setup, readiness checks, invocation, local validation, and failure triage are documented and guarded.
- `experimental`: partial adapter exists, but the agent must explain gaps and request approval before use.
- `candidate`: recommended backend family or related work, but not a default dependency.
- `future`: related work only; do not call it automatically.

Built-in recommended adapter: official Numina Lean Agent runtime.

Numina and Archon are recommended adapter candidates, not defaults or hard requirements. Other Lean-specialist backends may be connected by the coding agent through the backend adapter checklist, but do not call any backend until deployment, readiness checks, invocation, validation, and failure triage are documented.

## Adapter Contract

Document all of the following before calling a backend adapter:

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

Do not call a backend adapter unless its setup, call, credential, mutation, and validation contracts are documented. Undocumented adapters may be cited as related work or recommended candidates only.
