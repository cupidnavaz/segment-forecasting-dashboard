# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Before committing

Run:

```bash
pytest
ruff check .
```

If behavior changes, add or update tests.

## Commit style

Use short, imperative Conventional Commit-style messages, for example:

- `feat: add scenario comparison`
- `fix: correct confidence calculation`
- `docs: update deployment guide`
- `test: cover advisory scoring`

## Pull requests

A pull request should explain:

- What changed.
- Why it changed.
- How it was tested.
- Any known limitations or migration concerns.

Do not commit secrets, credentials, local environment files, generated exports, or production data.
