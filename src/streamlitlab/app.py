import logging
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from streamlitlab.utils.config import Config

_log: logging.Logger = logging.getLogger(__file__)


def configure_logging() -> None:
    """Set up logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )


def main() -> None:
    cfg = Config()
    configure_logging()
    _log.info(cfg.data)

    st.write(
        "Got lots of data? Great! Streamlit can show "
        "[dataframes](https://docs.streamlit.io/develop/api-reference/data) "
        "with hundred thousands of rows, images, sparklines – and even "
        "supports editing! ✍️"
    )

    num_rows = st.slider("Number of rows", 1, 10000, 500)
    np.random.seed(42)
    data_list: list[dict[str, Any]] = []
    for i in range(num_rows):
        data_list.append(
            {
                "Preview": f"https://picsum.photos/400/200?lock={i}",
                "Views": np.random.randint(0, 1000),
                "Active": np.random.choice([True, False]),
                "Category": np.random.choice(["🤖 LLM", "📊 Data", "⚙️ Tool"]),
                "Progress": np.random.randint(1, 100),
            }
        )
    data: pd.DataFrame = pd.DataFrame(data_list)

    config: dict[str, Any] = {
        "Preview": st.column_config.ImageColumn(),
        "Progress": st.column_config.ProgressColumn(),
    }

    if st.toggle("Enable editing"):
        edited_data = st.data_editor(
            data, column_config=config, width="stretch"
        )
    else:
        st.dataframe(data, column_config=config, width="stretch")
