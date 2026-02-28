# StreamlitLab

A playground for experimenting with [Streamlit](https://streamlit.io/), the Python library for building data apps.

## For End Users (Docker)

The quickest way to run the app without a Python environment:

```bash
docker compose up -d --build
```

The app is available at **<http://localhost:52134>**.

## For Developers

### Prerequisites

- Python 3.11+
- A virtual environment (`.venv`) in the project root

### First-Time Setup

Install dev dependencies **before anything else**. You can do this via the VS Code task or manually:

**VS Code task:** Run **Terminal → Run Task… → Install Dev Dependencies**

**Manual:**

```bash
python -m venv .venv
.venv/Scripts/activate   # Windows — use `source .venv/bin/activate` on Unix
pip install -e ".[dev]"
```

### Running the App

**VS Code task:** **Terminal → Run Task… → Run Streamlit** — launches on port 8501.

**Manual:**

```bash
streamlit run main.py --server.port 8501
```

### Debugging

Use the **Debug Streamlit** launch configuration (F5) to start the app with the debugpy debugger attached.

### Testing and Linting

```bash
pytest                    # run tests
pytest --cov=streamlitlab # run tests with coverage
ruff check .              # lint (add --fix to auto-fix)
ruff format .             # format in-place
```

### Regenerating requirements.txt

`requirements.txt` is a pip-tools lockfile for Docker — never edit it by hand.

**VS Code task:** **Terminal → Run Task… → Regenerate requirements.txt**

**Manual:**

```bash
pip-compile --strip-extras --output-file=requirements.txt pyproject.toml
```

### Project Structure

```txt
main.py                        # Entry point
src/streamlitlab/
├── app.py                     # Main Streamlit application
├── components/                # Reusable UI widgets
├── pages/                     # Streamlit page modules
└── utils/                     # Shared helpers
```
