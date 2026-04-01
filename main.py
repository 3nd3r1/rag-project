import argparse
import logging

from preparation import chunk_texts, create_texts, read_data
from vector_store import VectorStore


def prepare():
    df = read_data("data/superstore.csv")

    texts = create_texts(df)

    chunks = chunk_texts(texts)

    store = VectorStore()
    store.add_chunks(chunks)


def search(query: str):
    store = VectorStore()
    results = store.search(query)

    for result in results:
        print(result)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
    )

    parser = argparse.ArgumentParser(description="LLM-RAG Project CLI")
    subparser = parser.add_subparsers(dest="command", required=True)

    subparser.add_parser("prepare", help="Run data preparation steps")

    search_parser = subparser.add_parser("search", help="Search the vector store")
    search_parser.add_argument("query", type=str, help="The search query")

    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "search":
        search(args.query)


if __name__ == "__main__":
    main()
