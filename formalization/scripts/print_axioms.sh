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
# A clean audit is a subset of the standard mathlib axioms
# `propext`, `Classical.choice`, `Quot.sound`.  Any `sorryAx` or any
# additional axiom name is a failure.

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
# Extract the bracketed list after `depends on axioms:` and reject every
# name outside the three standard mathlib axioms.  This catches `sorryAx`
# and any locally declared axiom, not just `sorryAx`.
BAD_AXIOMS="$(printf '%s\n' "${AUDIT}" | awk '
  /depends on axioms:/ {
    line = $0
    sub(/^.*\[/, "", line)
    sub(/\].*$/, "", line)
    n = split(line, parts, ", ")
    for (i = 1; i <= n; i++) {
      if (parts[i] != "propext" &&
          parts[i] != "Classical.choice" &&
          parts[i] != "Quot.sound") {
        print parts[i]
      }
    }
  }' | sort -u)"

if [ -n "${BAD_AXIOMS}" ]; then
  echo "ERROR: axiom audit found unexpected axiom(s):" >&2
  printf '%s\n' "${BAD_AXIOMS}" >&2
  exit 1
fi
if [ "${STATUS}" -ne 0 ]; then
  echo "ERROR: axiom audit elaboration failed (exit ${STATUS})." >&2
  exit "${STATUS}"
fi
echo "axiom audit: only [propext, Classical.choice, Quot.sound] (or subsets)."
exit 0
