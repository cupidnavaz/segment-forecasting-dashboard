# Release Checklist

## Source

- [ ] Working tree is clean.
- [ ] Version updated in `pyproject.toml`.
- [ ] Changelog updated.
- [ ] Documentation reflects current behavior.
- [ ] No secrets or local files are committed.

## Quality

- [ ] `pytest` passes.
- [ ] `ruff check .` passes.
- [ ] Application starts with `streamlit run app.py`.
- [ ] CSV export verified.
- [ ] Executive report verified.
- [ ] Scenario controls verified.
- [ ] Filters and sorting verified.

## Git

```bash
git status
git add .
git diff --cached
git commit -m "release: v1.0.0"
git tag v1.0.0
git push origin main --tags
```

Do not push until the staged diff has been reviewed.
