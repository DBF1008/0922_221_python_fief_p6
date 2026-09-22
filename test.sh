#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ "${1:-}" == "regression" ]]; then
  shift
  TARGETS=(
    "tests/test_services_user_manager.py"
    "tests/test_apps_auth_auth.py"
    "tests/test_apps_auth_user.py"
    "tests/test_apps_auth_dashboard.py"
    "tests/test_apps_dashboard_users.py"
  )
elif [[ $# -gt 0 ]]; then
  TARGETS=("$@")
else
  TARGETS=("tests")
fi

if [[ -n "${PYTEST:-}" ]]; then
  run_pytest() {
    "$PYTEST" "$@"
  }
else
  run_pytest() {
    hatch run pytest "$@"
  }
fi

run_pytest "${TARGETS[@]}" --no-cov -p no:cacheprovider
