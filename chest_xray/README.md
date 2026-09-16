# Chest X-ray images (optional, not in git)

Pediatric chest radiographs, labels `NORMAL` / `PNEUMONIA`, Kermany et al.,
*Cell* 172(5):1122–1131, 2018.
DOI: https://doi.org/10.1016/j.cell.2018.02.010

JPEGs are **gitignored**. The companion note uses a 40-image subset of
`test/` (manifest: `medical/medical_subset_manifest.json`). Frozen CSV
rows in `medical/results/` already encode that run; you do not need the
JPEGs to verify Theorem A on those numbers.

## If you re-run the pipeline

Place the public test split here:

```
chest_xray/test/{NORMAL,PNEUMONIA}/*.jpeg
```

Then from `experiments/`:

```bash
PYTHONPATH=src python medical_validation/run_medical_experiment.py
```

Do not copy JPEGs into `medical/` or into git.
