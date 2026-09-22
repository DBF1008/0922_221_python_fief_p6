#!/usr/bin/env bash
#
# Run the unit test suite (defaults to SQLite, like the CI SQLITE matrix job).
#
# Usage:
#   ./test.sh                                  # run all unit tests
#   ./test.sh tests/test_apps_auth_auth.py     # run a specific test file
#   ./test.sh -k VerifyEmail                   # run tests matching a keyword
#
# Environment variables can be overridden, e.g.:
#   DATABASE_TYPE=POSTGRESQL DATABASE_HOST=localhost ./test.sh

set -euo pipefail
cd "$(dirname "$0")"

export ENVIRONMENT="${ENVIRONMENT:-development}"
export TELEMETRY_ENABLED="${TELEMETRY_ENABLED:-0}"
export SECRET="${SECRET:-ThisShouldBeChangedInProduction}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-uSieBJ_695D2NA7bOPUJqFGCS2_qI8G4aI6L42WhjjM=}"
export GENERATED_JWK_SIZE="${GENERATED_JWK_SIZE:-1024}"
export DATABASE_TYPE="${DATABASE_TYPE:-SQLITE}"
export DATABASE_NAME="${DATABASE_NAME:-fief}"
export ALLOW_ORIGIN_REGEX="${ALLOW_ORIGIN_REGEX:-http://localhost:3000}"
export FIEF_CLIENT_ID="${FIEF_CLIENT_ID:-FIEF_CLIENT_ID}"
export FIEF_CLIENT_SECRET="${FIEF_CLIENT_SECRET:-FIEF_CLIENT_SECRET}"

if [ "$#" -eq 0 ]; then
  set -- tests/
fi

PYTHON_BIN="${PYTHON:-python}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python3
fi

exec "$PYTHON_BIN" -m pytest "$@"
