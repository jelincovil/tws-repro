#!/usr/bin/env bash
# print_axioms.sh — run `#print axioms` on every exported theorem of the
# TWS formalization and dump the literal Lean output.
#
# Usage (from anywhere):
#     ./scripts/print_axioms.sh            # print to stdout
#     ./scripts/print_axioms.sh out.txt    # also tee into out.txt
#
# Requires a successful `lake build` first (the script runs it for you).
#
# A clean audit is exactly:  [propext, Classical.choice, Quot.sound]
# Any `sorryAx` in the output means the theorem is NOT proved.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJ_DIR}"

OUT="${1:-}"

echo "=== TWS formalization :: axiom audit ============================="
echo "project       : ${PROJ_DIR}"
echo "lean-toolchain: $(cat lean-toolchain)"
echo

# Make sure the oleans exist; `lake env lean` needs them to import TWS.
if ! lake build >/dev/null 2>&1; then
  echo "ERROR: 'lake build' failed. Run ./scripts/check_all.sh to see why." >&2
  exit 1
fi

run_audit() {
  lake env lean scripts/print_axioms.lean 2>&1
}

# Elaborate ONCE and keep the output. Running the audit again to re-grep it
# would let the reported note disagree with the text actually printed, and
# reading $PIPESTATUS after an intervening `echo` would clobber the status
# (that bug made the `tee` branch always exit 0, even on a failed elaboration).
AUDIT="$(run_audit)"
STATUS=$?

printf '%s\n' "${AUDIT}"
if [ -n "${OUT}" ]; then
  printf '%s\n' "${AUDIT}" > "${OUT}"
  echo
  echo "(written to ${OUT})"
fi

echo
if printf '%s\n' "${AUDIT}" | grep -q 'sorryAx'; then
  echo "ERROR: axiom audit reports sorryAx (incomplete proof)." >&2
  exit 1
fi
exit "${STATUS}"
