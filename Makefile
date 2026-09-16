# Companion repo — no manuscript targets.
.PHONY: help hashes medical-kit test lean

help:
	@echo "make hashes       — shasum -a 256 -c SHA256SUMS"
	@echo "make medical-kit  — verify frozen medical CSV/JSON + caption"
	@echo "make test         — pytest experiments/"
	@echo "make lean         — lake build (formalization/)"

hashes:
	shasum -a 256 -c SHA256SUMS

medical-kit:
	cd medical && python3 verify_results.py && python3 check_caption.py

test:
	cd experiments && PYTHONPATH=src python3 -m pytest tests/ -q

lean:
	cd formalization && lake build
