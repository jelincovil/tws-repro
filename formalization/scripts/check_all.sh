#!/usr/bin/env bash
# check_all.sh — full type-check of the TWS Lean 4 formalization.
#
# Usage (from anywhere):
#     ./scripts/check_all.sh
#
# What it does:
#   1. fetches the pinned mathlib .olean cache (`lake exe cache get`)
#   2. type-checks the whole library (`lake build`)
#   3. reports the exact `sorry` occurrences found in the sources
#
# Exit status: 0 iff `lake build` succeeded.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJ_DIR}"

echo "=== TWS formalization :: check_all ==============================="
echo "project      : ${PROJ_DIR}"
echo "lean-toolchain: $(cat lean-toolchain)"
echo "lake         : $(lake --version 2>&1 | head -1)"
echo

echo "--- [1/3] lake exe cache get ------------------------------------"
if ! lake exe cache get; then
  echo "WARNING: 'lake exe cache get' failed; the build may recompile"
  echo "         mathlib from source (hours). Continuing anyway."
fi
echo

echo "--- [2/3] lake build --------------------------------------------"
lake build
BUILD_STATUS=$?
echo "lake build exit status: ${BUILD_STATUS}"
echo

echo "--- [3/3] sorry audit -------------------------------------------"
# Only our own sources; .lake/ holds mathlib and is excluded.
# A real proof obligation is the bare token `sorry`. Filtered out:
#   - backtick-quoted prose in docstrings: `sorry`, `sorryAx`
#   - identifiers that merely contain it:  sorryAx, my_sorry, X.sorry
#   - hyphenated prose:                    sorry-free
# The trailing hyphen in the second class is load-bearing: without it this
# audit reported 2 hits, the second being the docstring line
# "The standalone `energy_stability` proved above is sorry-free."
SORRY_HITS="$(grep -rn --include='*.lean' -E '(^|[^A-Za-z0-9_.`])sorry([^A-Za-z0-9_`-]|$)' \
                 TWS.lean TWS scripts 2>/dev/null || true)"
if [ -z "${SORRY_HITS}" ]; then
  echo "real sorry count: 0"
else
  echo "${SORRY_HITS}"
  echo "real sorry count: $(printf '%s\n' "${SORRY_HITS}" | wc -l | tr -d ' ')"
fi
echo "(all textual occurrences, incl. docstring prose:"
grep -rnc --include='*.lean' 'sorry' TWS.lean TWS scripts 2>/dev/null || true
echo " )"
echo

if [ "${BUILD_STATUS}" -eq 0 ]; then
  echo "RESULT: BUILD OK"
else
  echo "RESULT: BUILD FAILED (exit ${BUILD_STATUS})"
fi
exit "${BUILD_STATUS}"
