import logging

from preparation import create_texts, read_data
from vector_store import VectorStore


def main():
    logging.basicConfig(
        level=logging.DEBUG,
    )

    df = read_data("data/superstore.csv")

    texts = create_texts(df)

    store = VectorStore()


if __name__ == "__main__":
    main()
