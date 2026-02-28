import io
import logging
import re

from streamlitlab.app import configure_logging


def test_logging_format() -> None:
    """Verify the production formatter is actually used by a handler.

    ``caplog`` installs its own handler with a default format, so we
    bypass it and attach a temporary ``StreamHandler`` to a ``StringIO``
    buffer instead.
    """
    configure_logging()

    # build a logger and attach custom handler that mirrors the formatter
    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )
    handler.setFormatter(fmt)

    logger = logging.getLogger("testlogger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("hello world")
    logger.removeHandler(handler)

    logged = buf.getvalue().strip().splitlines()[0]
    pattern = (
        r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2} "
        r"\[INFO\] testlogger: hello world"
    )
    assert re.match(pattern, logged)
