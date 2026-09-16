# How to put this tree on GitHub

This directory is a **standalone** git repository (see `.git/`). It is not
the CompAMa/arXiv manuscript. Create an **empty** GitHub repo (no
auto-README) and:

```bash
cd tws-repro
git remote add origin git@github.com:<YOU>/<REPO>.git
git push -u origin main
```

Do not invent the URL in README or CITATION.cff until the remote exists.

After the note is on arXiv, replace every `arXiv:XXXX.XXXXX` in
`README.md` and `CITATION.cff` with the real identifier, commit, tag.
