# Project Guidelines

## Code Style

- Python 4-space indent, 80-char line width, UTF-8 (see `.editorconfig`), compliant with PEP8
- Function-based organization — no classes unless complexity demands it
- Type-annotate all function signatures (see `def main() -> None:` in `src/streamlitlab/app.py`)
- snake_case for functions/variables, lowercase package names
- Use `import streamlit as st` — always reference via `st.` prefix
- **Logging:** avoid printing directly to stdout/stderr. Obtain a `logging.Logger` via `logging.getLogger(__name__)` or with a classname and rely on the configured handlers.
- **Ruff** for linting and formatting — config in `pyproject.toml` (`[tool.ruff]`)
- Rule sets: `E`, `F`, `W`, `I`, `UP`, `B`, `SIM`, `RUF` — run `ruff check .` and `ruff format .`

## Architecture

```
main.py                        # Entry point: adds src/ to sys.path, calls app.main()
src/streamlitlab/
├── app.py                     # Main Streamlit application logic
├── components/                # Reusable UI widgets
├── pages/                     # Streamlit page modules
└── utils/                     # Shared helpers
```

- **src layout** with Hatchling build system — package lives under `src/streamlitlab/`
- `main.py` bootstraps `sys.path` and delegates to `streamlitlab.app.main()`
- `pages/`, `components/`, `utils/` are scaffolded sub-packages — add new modules there
- Keep Streamlit UI in `app.py` or `pages/`; business logic in `utils/`

## Build and Test

```bash
# activate the Python virtualenv before running commands
source .venv/bin/activate

# Install (editable)
pip install -e ".[dev]"

# Run app locally (port 8501)
streamlit run main.py --server.port 8501

# Run tests
pytest

# Run tests with coverage
pytest --cov=streamlitlab

# Lint and format
ruff check .          # lint (add --fix to auto-fix)
ruff format .         # format in-place

# Regenerate pinned requirements.txt (production deps only)
pip-compile --strip-extras --output-file=requirements.txt pyproject.toml
```

- pytest config in `pyproject.toml`: `testpaths = ["tests"]`, `pythonpath = ["src"]`
- Tests can import `streamlitlab` directly — no `sys.path` manipulation needed in tests
- Test files go in `tests/` with `test_` prefix; annotate test functions with `-> None`
- Add docstrings to test functions (see `tests/test_app.py` for the pattern)

## Project Conventions

- All Streamlit UI flows through a single `main()` function in `app.py` — new features should either extend it or add page modules in `pages/`
- `requirements.txt` is a **pip-tools** lockfile for Docker — regenerate with `pip-compile`; add abstract deps to `pyproject.toml` `[project.dependencies]`
- **Never edit `requirements.txt` by hand** — always use VS Code task "Regenerate requirements.txt" to regenerate it
- Docker exposes port **52134** (not 8501); local dev uses 8501 via the VS Code task "Run Streamlit"

## Integration Points

- **Docker**: `python:3.14.3-alpine3.23` base image; `docker-compose.yml` reads `.env` for environment variables
- **Single runtime dependency**: `streamlit>=1.54.0` (pulls pandas, numpy, pyarrow transitively)
- **Dev dependencies**: `pytest>=8.0`, `pytest-cov>=6.0`, `ruff>=0.9`, `pip-tools>=7.0`
