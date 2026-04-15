import pandas as pd


def read_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df


def create_row_text(row: pd.Series) -> str:
    return (
        f"Order {row['Order ID']} on {row['Order Date']}: "
        f"Customer {row['Customer Name']} from {row['City']}, {row['State']}, {row['Region']} "
        f"ordered {row['Quantity']} '{row['Product Name']}' "
        f"with ship mode {row['Ship Mode']}, generating {row['Sales']} in sales and {row['Profit']} in profit."
    )


def create_row_texts(df: pd.DataFrame) -> list[str]:
    return [create_row_text(row) for _, row in df.iterrows()]


def create_month_text(row: pd.Series) -> str:
    return (
        f"Monthly orders for {row['Order Date']}: "
        f"Total sales {row['total_sales']}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit {row['total_profit']}."
    )


def create_month_texts(df: pd.DataFrame) -> list[str]:
    month_rows = (
        df.groupby(df["Order Date"].dt.to_period("M"))
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_month_text(month_row) for _, month_row in month_rows.iterrows()]


def create_region_text(row: pd.Series) -> str:
    return (
        f"Regional orders for {row['Region']}: "
        f"Total sales {row['total_sales']}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit {row['total_profit']}."
    )


def create_region_texts(df: pd.DataFrame) -> list[str]:
    region_rows = (
        df.groupby("Region")
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_region_text(region_row) for _, region_row in region_rows.iterrows()]


def create_category_text(row: pd.Series) -> str:
    return (
        f"Category summary for {row['Category']}: "
        f"Total sales {row['total_sales']:.2f}, "
        f"Total profit {row['total_profit']:.2f}."
    )


def create_category_texts(df: pd.DataFrame) -> list[str]:
    category_rows = (
        df.groupby("Category")
        .agg(
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_category_text(row) for _, row in category_rows.iterrows()]


def create_texts(df: pd.DataFrame) -> list[str]:
    texts = []
    texts += create_row_texts(df)
    texts += create_month_texts(df)
    texts += create_region_texts(df)
    texts += create_category_texts(df)

    return texts


def chunk_texts(texts: list[str], chunk_size: int = 500) -> list[str]:
    chunked_texts = []
    for text in texts:
        if len(text) <= chunk_size:
            chunked_texts.append(text)
        else:
            current = []
            current_length = 0
            for word in text.split():
                if current_length + len(word) + 1 > chunk_size:
                    chunked_texts.append(" ".join(current))
                current.append(word)
                current_length += len(word) + 1
            if current:
                chunked_texts.append(" ".join(current))

    return chunked_texts
