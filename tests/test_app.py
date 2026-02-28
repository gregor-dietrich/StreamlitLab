from streamlitlab.app import main


def test_main_exists() -> None:
    """Smoke test: main function is importable."""
    assert callable(main)
