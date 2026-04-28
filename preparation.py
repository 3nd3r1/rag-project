import calendar

import pandas as pd


def read_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["is_discounted"] = df["Discount"] > 0
    return df


def create_row_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"Order {row['Order ID']} on {row['Order Date']}: "
        f"Customer {row['Customer Name']} from {row['City']}, {row['State']}, {row['Region']} "
        f"ordered {row['Quantity']} '{row['Product Name']}' "
        f"with ship mode {row['Ship Mode']}, generating ${row['Sales']:.2f} in sales and ${row['Profit']:.2f} in profit."
    )
    metadata = {
        "type": "order",
        "region": row["Region"],
        "category": row["Category"],
        "sub_category": row["Sub-Category"],
        "year": row["Order Date"].year,
    }
    return text, metadata


def create_row_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    return [create_row_text(row) for _, row in df.iterrows()]


def create_month_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"Monthly orders for {calendar.month_name[row['Order Date'].month]} {row['Order Date'].year}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {
        "type": "monthly_summary",
        "year": row["Order Date"].year,
        "month": row["Order Date"].month,
    }
    return text, metadata


def create_month_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    month_rows = (
        df.groupby(df["Order Date"].dt.to_period("M"))
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_month_text(row) for _, row in month_rows.iterrows()]


def create_month_aggregate_text(row: pd.Series) -> tuple[str, dict]:
    month_name = calendar.month_name[int(row["month"])]
    text = (
        f"Aggregate orders for {month_name} across all years: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {"type": "month_aggregate_summary", "month": int(row["month"])}
    return text, metadata


def create_month_aggregate_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    month_rows = (
        df.groupby(df["Order Date"].dt.month.rename("month"))
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_month_aggregate_text(row) for _, row in month_rows.iterrows()]


def create_region_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"Regional orders for {row['Region']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {"type": "region_summary", "region": row["Region"]}
    return text, metadata


def create_region_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    region_rows = (
        df.groupby("Region")
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_region_text(row) for _, row in region_rows.iterrows()]


def create_state_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"State summary for {row['State']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {
        "type": "state_summary",
        "state": row["State"],
        "total_sales": float(row["total_sales"]),
    }
    return text, metadata


def create_state_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    state_rows = (
        df.groupby("State")
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_state_text(row) for _, row in state_rows.iterrows()]


def create_city_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"City summary for {row['City']}, {row['State']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {
        "type": "city_summary",
        "city": row["City"],
        "state": row["State"],
        "total_sales": float(row["total_sales"]),
    }
    return text, metadata


def create_city_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    city_rows = (
        df.groupby(["City", "State"])
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_city_text(row) for _, row in city_rows.iterrows()]


def _format_ranking(
    names: list[str],
    values: list[float],
    label: str,
    metric: str,
    n: int,
    chunk_type: str,
) -> tuple[str, dict]:
    lines = ", ".join(
        f"{i}. {name} ${val:.2f}" for i, (name, val) in enumerate(zip(names, values), 1)
    )
    text = f"Top {n} {label} by total {metric}: {lines}."
    return text, {"type": chunk_type}


def create_city_ranking_text(
    top: pd.DataFrame, metric: str, col: str, n: int
) -> tuple[str, dict]:
    names = [f"{r['City']}, {r['State']}" for _, r in top.iterrows()]
    values = [r[col] for _, r in top.iterrows()]
    return _format_ranking(names, values, "cities", metric, n, "cities_ranking")


def create_city_ranking_texts(df: pd.DataFrame, n: int = 10) -> list[tuple[str, dict]]:
    city_rows = (
        df.groupby(["City", "State"])
        .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
        .reset_index()
    )
    return [
        create_city_ranking_text(
            city_rows.sort_values(col, ascending=False).head(n), metric, col, n
        )
        for metric, col in [("sales", "total_sales"), ("profit", "total_profit")]
    ]


def create_state_ranking_text(
    top: pd.DataFrame, metric: str, col: str, n: int
) -> tuple[str, dict]:
    names = [r["State"] for _, r in top.iterrows()]
    values = [r[col] for _, r in top.iterrows()]
    return _format_ranking(names, values, "states", metric, n, "states_ranking")


def create_state_ranking_texts(df: pd.DataFrame, n: int = 10) -> list[tuple[str, dict]]:
    state_rows = (
        df.groupby("State")
        .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
        .reset_index()
    )
    return [
        create_state_ranking_text(
            state_rows.sort_values(col, ascending=False).head(n), metric, col, n
        )
        for metric, col in [("sales", "total_sales"), ("profit", "total_profit")]
    ]


def create_category_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"Category summary for {row['Category']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {"type": "category_summary", "category": row["Category"]}
    return text, metadata


def create_category_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    category_rows = (
        df.groupby("Category")
        .agg(
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_category_text(row) for _, row in category_rows.iterrows()]


def create_subcategory_text(row: pd.Series) -> tuple[str, dict]:
    profit_margin = (
        (row["total_profit"] / row["total_sales"] * 100) if row["total_sales"] else 0
    )
    text = (
        f"Sub-Category summary for {row['Sub-Category']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total profit ${row['total_profit']:.2f}, "
        f"Profit margin {profit_margin:.2f}%, "
        f"Total orders {row['total_orders']}, "
        f"Total discounted orders {row['total_discounted_orders']}."
    )
    metadata = {"type": "subcategory_summary", "sub_category": row["Sub-Category"]}
    return text, metadata


def create_subcategory_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    subcategory_rows = (
        df.groupby("Sub-Category")
        .agg(
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            total_orders=("Order ID", "nunique"),
            total_discounted_orders=("is_discounted", "sum"),
        )
        .reset_index()
    )

    return [create_subcategory_text(row) for _, row in subcategory_rows.iterrows()]


def create_product_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"Product summary for {row['product_name']} ({row['Product ID']}): "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total profit ${row['total_profit']:.2f}, "
        f"Total quantity sold {row['total_quantity']}, "
        f"Total orders {row['total_orders']}, "
        f"Total discounted orders {row['total_discounted_orders']}."
    )
    metadata = {
        "type": "product_summary",
        "product_id": row["Product ID"],
        "product_name": row["product_name"],
    }
    return text, metadata


def create_product_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    product_rows = (
        df.groupby("Product ID")
        .agg(
            product_name=("Product Name", "first"),
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            total_quantity=("Quantity", "sum"),
            total_orders=("Order ID", "nunique"),
            total_discounted_orders=("is_discounted", "sum"),
        )
        .reset_index()
    )

    return [create_product_text(row) for _, row in product_rows.iterrows()]


def create_year_text(row: pd.Series) -> tuple[str, dict]:
    profit_margin = (
        (row["total_profit"] / row["total_sales"] * 100) if row["total_sales"] else 0
    )
    text = (
        f"Annual summary for {row['year']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}, "
        f"Profit margin {profit_margin:.2f}%."
    )
    metadata = {"type": "year_summary", "year": int(row["year"])}
    return text, metadata


def create_year_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    year_rows = (
        df.groupby(df["Order Date"].dt.year.rename("year"))
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_year_text(row) for _, row in year_rows.iterrows()]


def create_year_category_text(row: pd.Series) -> tuple[str, dict]:
    text = (
        f"Annual summary for {row['year']} - {row['Category']}: "
        f"Total sales ${row['total_sales']:.2f}, "
        f"Total orders {row['total_orders']}, "
        f"Total profit ${row['total_profit']:.2f}."
    )
    metadata = {
        "type": "year_category_summary",
        "year": int(row["year"]),
        "category": row["Category"],
    }
    return text, metadata


def create_year_category_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    year_category_rows = (
        df.groupby([df["Order Date"].dt.year.rename("year"), "Category"])
        .agg(
            total_sales=("Sales", "sum"),
            total_orders=("Order ID", "nunique"),
            total_profit=("Profit", "sum"),
        )
        .reset_index()
    )

    return [create_year_category_text(row) for _, row in year_category_rows.iterrows()]


def create_texts(df: pd.DataFrame) -> list[tuple[str, dict]]:
    texts: list[tuple[str, dict]] = []
    texts += create_row_texts(df)
    texts += create_month_texts(df)
    texts += create_month_aggregate_texts(df)
    texts += create_year_texts(df)
    texts += create_year_category_texts(df)
    texts += create_region_texts(df)
    texts += create_state_texts(df)
    texts += create_city_texts(df)
    texts += create_category_texts(df)
    texts += create_subcategory_texts(df)
    texts += create_product_texts(df)
    texts += create_city_ranking_texts(df)
    texts += create_state_ranking_texts(df)
    return texts


def chunk_texts(
    texts: list[tuple[str, dict]], chunk_size: int = 500
) -> list[tuple[str, dict]]:
    result: list[tuple[str, dict]] = []
    for text, metadata in texts:
        if len(text) <= chunk_size:
            result.append((text, metadata))
        else:
            current = []
            current_length = 0
            for word in text.split():
                if current_length + len(word) + 1 > chunk_size:
                    result.append((" ".join(current), metadata))
                    current = []
                    current_length = 0
                current.append(word)
                current_length += len(word) + 1
            if current:
                result.append((" ".join(current), metadata))
    return result
