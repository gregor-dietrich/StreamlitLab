import json
import os
from typing import Any

import pytest

from streamlitlab.utils.config import Config

# Snapshot of the real defaults so each test can restore them.
_REAL_DEFAULTS: dict[str, Any] = dict(Config.default_config)


@pytest.fixture(autouse=True)
def _clean_singleton(  # pyright: ignore[reportUnusedFunction]
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> Any:
    """Reset Config singleton, clear SQL env vars, chdir to tmp."""
    Config.reset()
    for var in Config.env_map:
        monkeypatch.delenv(var, raising=False)
    original = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(original)
    Config.reset(default_config=dict(_REAL_DEFAULTS))


def _with_defaults(defaults: dict[str, Any], path: str) -> Config:
    """Create a Config instance with custom defaults for testing."""
    Config.reset(default_config=defaults)
    return Config(path)


def test_creates_file_with_defaults(tmp_path: Any) -> None:
    """Config creates the JSON file when it doesn't exist."""
    path = str(tmp_path / "cfg.json")
    cfg = _with_defaults({"a": 1}, path)

    assert os.path.isfile(path)
    assert cfg.get("a") == 1


def test_singleton_returns_same_instance(tmp_path: Any) -> None:
    """Second call returns the cached instance."""
    path = str(tmp_path / "test.json")
    _with_defaults({"x": 1}, path)
    cfg2 = Config()

    assert Config() is cfg2


def test_merge_preserves_existing_values(tmp_path: Any) -> None:
    """Existing values in the file are not overwritten by defaults."""
    path = str(tmp_path / "cfg.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"a": 99, "b": 2}, fh)

    cfg = _with_defaults({"a": 1, "c": 3}, path)

    assert cfg.get("a") == 99  # kept
    assert cfg.get("b") == 2  # kept
    assert cfg.get("c") == 3  # merged from defaults


def test_set_persists_to_disk(tmp_path: Any) -> None:
    """set() writes the value to disk immediately."""
    path = str(tmp_path / "cfg.json")
    cfg = _with_defaults({}, path)
    cfg.set("new_key", "hello")

    with open(path, encoding="utf-8") as fh:
        on_disk = json.load(fh)

    assert on_disk["new_key"] == "hello"


def test_reload_picks_up_external_changes(tmp_path: Any) -> None:
    """reload() re-reads the file from disk."""
    path = str(tmp_path / "cfg.json")
    cfg = _with_defaults({"v": 1}, path)
    assert cfg.get("v") == 1

    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"v": 42}, fh)

    cfg.reload()
    assert cfg.get("v") == 42


def test_reset_clears_singleton(tmp_path: Any) -> None:
    """reset() allows a fresh instance to be created."""
    path = str(tmp_path / "r.json")
    cfg1 = _with_defaults({"z": 0}, path)
    Config.reset()

    # Remove the old file so the new defaults take effect
    os.remove(path)
    cfg2 = _with_defaults({"z": 5}, path)

    assert cfg1 is not cfg2
    assert cfg2.get("z") == 5


def test_nested_merge(tmp_path: Any) -> None:
    """Nested dicts in defaults are merged recursively."""
    path = str(tmp_path / "cfg.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"sql": {"database": "mydb"}}, fh)

    cfg = _with_defaults(
        {"sql": {"database": None, "username": None, "password": None}},
        path,
    )

    sql = cfg.get("sql")
    assert sql["database"] == "mydb"  # preserved
    assert sql["username"] is None  # merged
    assert sql["password"] is None  # merged


def test_real_defaults_applied(tmp_path: Any) -> None:
    """The built-in defaults include the sql section."""
    path = str(tmp_path / "cfg.json")
    cfg = Config(path)

    sql = cfg.get("sql")
    assert isinstance(sql, dict)
    assert "database" in sql


def test_empty_file_replaced_with_defaults(tmp_path: Any) -> None:
    """An empty config file is overwritten with defaults."""
    path = str(tmp_path / "cfg.json")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("")

    cfg = _with_defaults({"a": 1}, path)

    assert cfg.get("a") == 1


def test_non_dict_json_replaced_with_defaults(tmp_path: Any) -> None:
    """A config file containing a JSON array is overwritten with defaults."""
    path = str(tmp_path / "cfg.json")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("[]")

    cfg = _with_defaults({"b": 2}, path)

    assert cfg.get("b") == 2


def test_env_var_overrides_default(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An env var fills in a value that would otherwise be None."""
    path = str(tmp_path / "cfg.json")
    monkeypatch.setenv("STREAMLITLAB_SQL_DATABASE", "from_env")

    cfg = Config(path)

    assert cfg.get("sql")["database"] == "from_env"


def test_config_file_beats_env_var(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A value already in config.json is not overwritten by an env var."""
    path = str(tmp_path / "cfg.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"sql": {"database": "from_file"}}, fh)

    monkeypatch.setenv("STREAMLITLAB_SQL_DATABASE", "from_env")
    cfg = Config(path)

    assert cfg.get("sql")["database"] == "from_file"


def test_env_var_not_set_falls_to_default(tmp_path: Any) -> None:
    """Without the env var, the default (None) is used."""
    path = str(tmp_path / "cfg.json")
    cfg = Config(path)

    assert cfg.get("sql")["database"] is None
