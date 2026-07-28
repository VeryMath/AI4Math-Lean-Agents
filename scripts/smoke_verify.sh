#!/usr/bin/env bash
# Smoke regression: lake build + lake env lean on positive targets; broken must fail.
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"
cd "$project_root"

if [[ -x /mnt/d/Lean/elan/bin/lake ]]; then
  export PATH="/mnt/d/Lean/elan/bin:$PATH"
fi

ok() {
  local label="$1"; shift
  echo "==> $label"
  "$@"
  echo "OK: $label"
}

expect_fail() {
  local label="$1"; shift
  echo "==> $label (expect fail)"
  set +e
  "$@"
  local code=$?
  set -e
  if [[ $code -eq 0 ]]; then
    echo "FAILED (expected non-zero): $label" >&2
    exit 1
  fi
  echo "OK (failed as expected): $label"
}

ok "lake build" lake build
ok "InteractiveDemo" lake env lean StatInferenceLean/Exercises/InteractiveDemo.lean
ok "ErrorBank fixed" lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.fixed.lean
ok "Bernoulli" lake env lean StatInferenceLean/Exercises/Bernoulli.lean
expect_fail "ErrorBank broken" lake env lean StatInferenceLean/Exercises/Fixtures/ErrorBankDemo.broken.lean

echo
echo "smoke_verify: all checks passed."
