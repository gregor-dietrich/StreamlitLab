import json
import os
from typing import Any, ClassVar, cast


class Config:
    """Singleton configuration manager.

    Reads, merges, and writes a JSON config file. Only one instance
    is ever created; subsequent calls return the cached instance.
    """

    _instance: ClassVar["Config | None"] = None
    default_config: ClassVar[dict[str, Any]] = {
        "sql": {"database": None, "username": None, "password": None}
    }
    env_map: ClassVar[dict[str, tuple[str, ...]]] = {
        "STREAMLITLAB_SQL_DATABASE": ("sql", "database"),
        "STREAMLITLAB_SQL_USERNAME": ("sql", "username"),
        "STREAMLITLAB_SQL_PASSWORD": ("sql", "password"),
    }

    def __new__(
        cls,
        filename: str = "config.json",
    ) -> "Config":
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instance = instance
        return cls._instance

    def __init__(
        self,
        filename: str = "config.json",
    ) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._filename = filename
        self._config: dict[str, Any] = {}
        self._load()

    # -- public API --------------------------------------------------

    @property
    def filename(self) -> str:
        """Return the path to the config file."""
        return self._filename

    @property
    def data(self) -> dict[str, Any]:
        """Return a copy of the current configuration."""
        return dict(self._config)

    def get(self, key: str, default: Any = None) -> Any:
        """Return a top-level config value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a top-level config value and persist to disk."""
        self._config[key] = value
        self._write()

    def reload(self) -> None:
        """Re-read the config file from disk and re-apply defaults."""
        self._load()

    # -- class-level helpers -----------------------------------------

    @classmethod
    def reset(
        cls,
        default_config: dict[str, Any] | None = None,
    ) -> None:
        """Remove the cached instance so the next call creates fresh.

        Primarily useful in tests. Optionally override the class-level
        defaults that will be applied on the next instantiation.
        """
        cls._instance = None
        if default_config is not None:
            cls.default_config = default_config

    # -- private helpers ---------------------------------------------

    def _load(self) -> None:
        env_config = self._build_env_config()

        if not os.path.exists(self._filename):
            self._write_raw(env_config)

        if not os.path.isfile(self._filename):
            raise RuntimeError(f"{self._filename} is not a file")

        data = self._read()
        if not isinstance(data, dict):
            data = {}
        self._config = data
        self._merge(self._config, env_config)
        self._write()

    @classmethod
    def _build_env_config(cls) -> dict[str, Any]:
        """Build a config dict from defaults with env-var overrides.

        Precedence when later merged into the file-based config:
        config.json  >  environment variables  >  defaults
        """
        import copy

        env_config: dict[str, Any] = copy.deepcopy(cls.default_config)
        for var, path in cls.env_map.items():
            value = os.environ.get(var)
            if value is not None:
                target = env_config
                for key in path[:-1]:
                    target = target.setdefault(key, {})
                target[path[-1]] = value
        return env_config

    def _read(self) -> Any:
        try:
            with open(self._filename, encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, ValueError):
            return {}
        except Exception as e:
            raise RuntimeError(f"Unable to read {self._filename}") from e

    def _write(self) -> None:
        self._write_raw(self._config)

    def _write_raw(self, data: dict[str, Any]) -> None:
        try:
            with open(self._filename, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        except Exception as e:
            raise RuntimeError(f"Unable to write {self._filename}") from e

    @staticmethod
    def _merge(config: dict[str, Any], defaults: dict[str, Any]) -> None:
        """Recursively merge *defaults* into *config*."""
        for key, default_value in defaults.items():
            if key not in config:
                config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(
                config[key], dict
            ):
                Config._merge(
                    config[key],
                    cast(dict[str, Any], default_value),
                )
