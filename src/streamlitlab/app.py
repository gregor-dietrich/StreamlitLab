import logging
from typing import ClassVar

import streamlit as st

from streamlitlab.utils.config import Config


class App:
    """Singleton Streamlit application.

    Only one instance is ever created; subsequent calls return the
    cached instance.
    """

    _instance: ClassVar["App | None"] = None

    def __new__(cls) -> "App":
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._log: logging.Logger = logging.getLogger(__class__.__name__)
        self.cfg: Config = Config()
        self._configure_logging()
        self._log.info("App initialized")

    def _configure_logging(self) -> None:
        """Set up logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S",
        )

    def run(self) -> None:
        st.set_page_config(
            layout="centered",
            page_title="StreamlitLab",
            page_icon=":material/crown:",
        )

        st.write("Hello world!")
        self._log.info("run() completed")
