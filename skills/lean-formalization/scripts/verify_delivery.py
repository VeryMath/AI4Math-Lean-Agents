from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from check_lean_project import check_project
from common import run_command
from configure_lean import inspect_environment
from direct_task import run_direct_task
from extract_minimal_failure import extract
from smoke_test import run_smoke_test
from tool_status import doctor, find_tool
from validate_patch import review_files


SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "config/lean_agent.example.toml",
    "config/numina_runtime.example.toml",
    "examples/smoke/NuminaSmoke.lean",
    "schemas/task.schema.json",
    "schemas/result.schema.json",
    "schemas/config.schema.json",
    "references/lean_runtime_configuration.md",
    "references/interactive_orchestration.md",
    "references/direct_lean_workflow.md",
    "references/specialist_agent_patterns.md",
    "references/numina_runtime.md",
    "references/numina_subagent_troubleshooting.md",
    "references/review_checklist.md",
    "references/failure_taxonomy.md",
    "references/numina_reverse_analysis.md",
    "scripts/ai4m_lean.py",
    "scripts/configure_lean.py",
    "scripts/direct_task.py",
    "scripts/numina_runtime.py",
    "scripts/smoke_test.py",
    "scripts/validate_patch.py",
    "scripts/extract_minimal_failure.py",
]
REQUIRED_COMMANDS = {
    "env",
    "doctor",
    "configure",
    "check",
    "prove",
    "formalize",
    "repair",
    "complete-sorries",
    "batch",
    "review",
    "detect-sorry",
    "minimize-failure",
    "smoke-test",
    "verify-delivery",
}


def _parser_commands() -> set[str]:
    from ai4m_lean import build_parser

    parser = build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices)
    return set()


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _package_hygiene() -> dict[str, Any]:
    generated = [
        str(path.relative_to(SKILL_ROOT))
        for path in SKILL_ROOT.rglob("*")
        if "__pycache__" in path.parts or path.suffix == ".pyc"
    ]
    suspicious_secret_patterns = [
        "sk-" + "ant-",
        "sk-" + "proj-",
        "BEGIN " + "OPENAI API KEY",
    ]
    secret_hits: list[str] = []
    for path in SKILL_ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(pattern in text for pattern in suspicious_secret_patterns):
            secret_hits.append(str(path.relative_to(SKILL_ROOT)))
    return {
        "ok": not secret_hits,
        "generated_files": generated,
        "generated_files_note": "ignored by .gitignore; remove before packaging if creating an archive" if generated else None,
        "secret_pattern_hits": secret_hits,
    }


def _guidance_first_check() -> dict[str, Any]:
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    orchestration = (SKILL_ROOT / "references" / "interactive_orchestration.md").read_text(encoding="utf-8", errors="replace")
    required_phrases = [
        "## Agent Playbook",
        "## Helper Toolbox",
        "This is a coding-agent-first Lean skill.",
        "The coding agent is the primary Lean worker.",
        "Official Numina is an optional deployable subagent backend.",
        "Default execution mode is coding-agent mode.",
        "Learn from Lean-specialist agent patterns and integrate them into the default coding-agent workflow.",
        "Use specialist-agent patterns as mechanisms, not mandatory external services.",
        "Use Numina when the user asks for the official Lean Agent, batch proof search, or an external subagent run.",
        "Use the bundled smoke test when no user target is available.",
        "Lead the interaction; do not wait for the user to drive every step.",
        "If the user's language is ambiguous, default to Chinese.",
        "A language switch is not a task reset.",
        "If no target is available, run or propose a safe local smoke/readiness check.",
        "Avoid ending with only \"send me a file\"",
        "Opening readiness should inspect local Lean readiness and Numina subagent readiness separately.",
        "Do not require API keys for the default coding-agent path.",
        "Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.",
        "offer a small next-step menu",
        "Ask at most one blocking question at a time.",
        "The bundled CLI is a helper toolbox, not the workflow driver.",
        "Use official Numina through a human-in-the-loop subagent workflow.",
        "Do not turn helper commands into a closed proof workflow.",
        "Do not remove the official Numina subagent path.",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in text]
    orchestration_required = [
        "## Session Opening",
        "This is a coding-agent-first Lean skill.",
        "Official Numina is an optional deployable subagent backend.",
        "The default coding-agent path should still absorb Lean-specialist agent mechanisms:",
        "Use the bundled smoke test when no user target is available.",
        "Lead the interaction; do not wait for the user to drive every step.",
        "A language switch is not a task reset.",
        "If no target is available, run or propose a safe local smoke/readiness check.",
        "Avoid ending with only \"send me a file\"",
        "Opening readiness should inspect local Lean readiness and Numina subagent readiness separately.",
        "Do not require API keys for the default coding-agent path.",
        "Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.",
        "A good opening ends with one decision question, not a checklist.",
    ]
    orchestration_missing = [phrase for phrase in orchestration_required if phrase not in orchestration]
    openai_yaml = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8", errors="replace")
    openai_required = [
        "请用中文开始",
        "如果用户明确使用其他语言",
        "默认走 coding agent Lean 工作流",
        "这个 skill 会学习并整合",
        "Numina 是可部署的可选 subagent",
    ]
    openai_missing = [phrase for phrase in openai_required if phrase not in openai_yaml]
    return {
        "ok": not missing and not orchestration_missing and not openai_missing and "## Commands" not in text,
        "missing_phrases": missing,
        "orchestration_missing_phrases": orchestration_missing,
        "openai_yaml_missing_phrases": openai_missing,
        "commands_section_present": "## Commands" in text,
    }


def verify(
    cwd: str | Path = ".",
    require_environment: bool = False,
    include_workspace_build: bool = False,
    run_tests: bool = False,
) -> dict[str, Any]:
    cwd_path = Path(cwd).resolve()
    files = [{"path": item, "exists": (SKILL_ROOT / item).exists()} for item in REQUIRED_FILES]
    commands = _parser_commands()
    schemas = []
    for name in ("task.schema.json", "result.schema.json", "config.schema.json"):
        path = SKILL_ROOT / "schemas" / name
        try:
            _load_schema(path)
            schemas.append({"path": f"schemas/{name}", "ok": True})
        except Exception as exc:  # noqa: BLE001 - report schema parse failure in JSON
            schemas.append({"path": f"schemas/{name}", "ok": False, "error": str(exc)})

    fixtures = SKILL_ROOT / "tests" / "fixtures"
    with tempfile.TemporaryDirectory() as tmp:
        dry_root = Path(tmp)
        dry_target = dry_root / "Failure.lean"
        (dry_root / "lean-toolchain").write_text("leanprover/lean4:v4.28.0\n", encoding="utf-8")
        (dry_root / "lakefile.toml").write_text('name = "verify_delivery"\n', encoding="utf-8")
        dry_target.write_text((fixtures / "failure.lean").read_text(encoding="utf-8"), encoding="utf-8")
        dry_run = run_direct_task("prove", dry_root, dry_target, dry_run=True)
    review = review_files(fixtures / "before.lean", fixtures / "after_bad.lean")
    failure = extract(fixtures / "failure.lean", target=None, run_lean=False)
    smoke = run_smoke_test(cwd_path, dry_run=True)

    tool_report = doctor(cwd_path) if require_environment else None
    env_report = inspect_environment(cwd_path) if require_environment else None
    workspace_check = None
    workspace_build = None
    if include_workspace_build:
        env_for_workspace = env_report or inspect_environment(cwd_path)
        workspace_root = env_for_workspace.get("lean", {}).get("workspace_project_root")
        if workspace_root:
            workspace_check = check_project(workspace_root, skip_build=True)
            lake = find_tool("lake") or "lake"
            workspace_build = run_command([lake, "build"], cwd=workspace_root, timeout=1800)
        else:
            workspace_check = {"ok": False, "status": "missing_workspace"}

    tests = None
    if run_tests:
        tests = run_command([sys.executable, "-m", "unittest", "discover", "-s", str(SKILL_ROOT / "tests")], cwd=SKILL_ROOT, timeout=300)

    hygiene = _package_hygiene()
    guidance_first = _guidance_first_check()
    checks = {
        "required_files": all(item["exists"] for item in files),
        "required_commands": REQUIRED_COMMANDS.issubset(commands),
        "no_parallel_numina_commands": not any(command.startswith("numina") for command in commands),
        "schemas": all(item["ok"] for item in schemas),
        "guidance_first_skill": bool(guidance_first.get("ok")),
        "dry_run_prove": bool(dry_run.get("ok") and dry_run.get("status") == "dry_run"),
        "patch_guard": bool(not review.get("ok") and review.get("findings")),
        "minimal_failure": bool(failure.get("ok") and failure.get("minimal_failure", {}).get("snippet")),
        "bundled_smoke_test": bool(smoke.get("ok") and smoke.get("status") == "dry_run" and Path(smoke.get("smoke_file", "")).exists()),
        "package_hygiene": bool(hygiene.get("ok")),
    }
    if require_environment:
        checks["tool_environment"] = bool(tool_report and tool_report.get("ok"))
        checks["lean_agent_environment"] = bool(env_report and env_report.get("ok"))
    if include_workspace_build:
        checks["workspace_check"] = bool(workspace_check and workspace_check.get("ok"))
        checks["workspace_build"] = bool(workspace_build and workspace_build.get("ok"))
    if run_tests:
        checks["unit_tests"] = bool(tests and tests.get("ok"))

    ok = all(checks.values())
    return {
        "ok": ok,
        "status": "delivery_ready" if ok else "delivery_blocked",
        "cwd": str(cwd_path),
        "skill_root": str(SKILL_ROOT),
        "checks": checks,
        "files": files,
        "commands": {
            "required": sorted(REQUIRED_COMMANDS),
            "available": sorted(commands),
            "missing": sorted(REQUIRED_COMMANDS - commands),
        },
        "schemas": schemas,
        "guidance_first_skill": guidance_first,
        "dry_run_prove": {
            "ok": dry_run.get("ok"),
            "status": dry_run.get("status"),
            "backend": dry_run.get("backend"),
            "agent_mode": dry_run.get("agent_mode"),
            "missing_config": dry_run.get("missing_config"),
        },
        "patch_guard": {
            "ok": review.get("ok"),
            "status": review.get("status"),
            "finding_count": len(review.get("findings", [])),
        },
        "minimal_failure": {
            "ok": failure.get("ok"),
            "status": failure.get("status"),
            "start_line": failure.get("minimal_failure", {}).get("start_line"),
            "end_line": failure.get("minimal_failure", {}).get("end_line"),
        },
        "bundled_smoke_test": {
            "ok": smoke.get("ok"),
            "status": smoke.get("status"),
            "smoke_file": smoke.get("smoke_file"),
            "project_root": smoke.get("project_root"),
        },
        "hygiene": hygiene,
        "tool_environment": tool_report,
        "lean_agent_environment": env_report,
        "workspace_check": workspace_check,
        "workspace_build": workspace_build,
        "unit_tests": tests,
        "external_api_note": "env, doctor, check, review, tests, and dry-runs do not call external APIs. configure --setup-numina and approved official Numina runs may clone/install/call external tools, then final Lean changes must be validated locally.",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Verify Lean Formalization delivery readiness")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--require-environment", action="store_true")
    parser.add_argument("--include-workspace-build", action="store_true")
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args(argv)
    result = verify(
        cwd=args.cwd,
        require_environment=args.require_environment,
        include_workspace_build=args.include_workspace_build,
        run_tests=args.run_tests,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
