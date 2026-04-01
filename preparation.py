import logging

import pandas as pd


def read_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    logging.debug(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    return df


def create_texts(df: pd.DataFrame) -> list[str]:
    pass
