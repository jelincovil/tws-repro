#!/usr/bin/env bash
# check_all.sh — full type-check and source audit of the TWS Lean 4 library.
#
# Usage (from anywhere):
#     ./scripts/check_all.sh
#
# What it does:
#   1. fetches the pinned mathlib .olean cache (`lake exe cache get`)
#   2. type-checks the whole library (`lake build`)
#   3. audits the sources for `sorry`, `admit`, and explicit `axiom`
#      declarations (the archived skeleton is outside the library target)
#
# Exit status: 0 iff `lake build` succeeded and all source audits are clean.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJ_DIR}"

echo "=== TWS formalization :: check_all ==============================="
echo "project       : ${PROJ_DIR}"
echo "lean-toolchain: $(cat lean-toolchain)"
echo "lake          : $(lake --version 2>&1 | head -1)"
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

echo "--- [3/3] source audit ------------------------------------------"
# Only the library sources; .lake/ holds mathlib and archive/ is historical.
# A real proof obligation is the bare token `sorry` (or `admit`). Filtered out:
#   - backtick-quoted prose in docstrings: `sorry`, `sorryAx`
#   - identifiers that merely contain it:  sorryAx, my_sorry, X.sorry
#   - hyphenated prose:                    sorry-free
SORRY_HITS="$(grep -rn --include='*.lean' -E '(^|[^A-Za-z0-9_.`])sorry([^A-Za-z0-9_`-]|$)' \
                 TWS.lean TWS scripts 2>/dev/null || true)"
ADMIT_HITS="$(grep -rn --include='*.lean' -E '(^|[^A-Za-z0-9_.`])admit([^A-Za-z0-9_`-]|$)' \
                 TWS.lean TWS scripts 2>/dev/null || true)"
AXIOM_HITS="$(grep -rn --include='*.lean' -E '^[[:space:]]*axiom[[:space:]]' \
                 TWS.lean TWS scripts 2>/dev/null || true)"

if [ -z "${SORRY_HITS}" ]; then
  echo "real sorry count: 0"
else
  echo "${SORRY_HITS}"
  echo "real sorry count: $(printf '%s\n' "${SORRY_HITS}" | wc -l | tr -d ' ')"
fi
if [ -z "${ADMIT_HITS}" ]; then
  echo "real admit count: 0"
else
  echo "${ADMIT_HITS}"
  echo "real admit count: $(printf '%s\n' "${ADMIT_HITS}" | wc -l | tr -d ' ')"
fi
if [ -z "${AXIOM_HITS}" ]; then
  echo "explicit axiom declarations: 0"
else
  echo "${AXIOM_HITS}"
  echo "explicit axiom declarations: $(printf '%s\n' "${AXIOM_HITS}" | wc -l | tr -d ' ')"
fi
echo "(all textual occurrences of 'sorry', incl. docstring prose:"
grep -rnc --include='*.lean' 'sorry' TWS.lean TWS scripts 2>/dev/null || true
echo " )"
echo

AUDIT_STATUS=0
if [ -n "${SORRY_HITS}" ] || [ -n "${ADMIT_HITS}" ] || [ -n "${AXIOM_HITS}" ]; then
  AUDIT_STATUS=1
fi

if [ "${BUILD_STATUS}" -eq 0 ] && [ "${AUDIT_STATUS}" -eq 0 ]; then
  echo "RESULT: BUILD OK"
  exit 0
elif [ "${BUILD_STATUS}" -ne 0 ]; then
  echo "RESULT: BUILD FAILED (exit ${BUILD_STATUS})"
  exit "${BUILD_STATUS}"
else
  echo "RESULT: SOURCE AUDIT FAILED"
  exit 1
fi
