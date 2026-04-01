import logging

import pandas as pd


def read_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    logging.debug(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    return df


def create_row_text(row: pd.Series) -> str:
    return (
        f"Order {row['Order Id']} on {row['Order Date']}:"
        f"Customer {row['Customer Name']} from {row['City']}, {row['State']}, {row['Region']} "
        f"ordered {row['Quantity']} '{row['Product Name']}' "
        f"with ship mode {row['Ship Mode']}, generating {row['Sales']} in sales and {row['Profit']} in profit."
    )


def create_row_texts(df: pd.DataFrame) -> list[str]:
    return [create_row_text(row) for _, row in df.iterrows()]


def create_month_texts(df: pd.DataFrame) -> list[str]:
    pass


def create_texts(df: pd.DataFrame) -> list[str]:
    texts = []
    texts += create_row_texts(df)

    return texts
