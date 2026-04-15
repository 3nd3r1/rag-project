import argparse
import logging

from preparation import chunk_texts, create_texts, read_data
from rag_pipeline import RAGPipeline
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


def chat():
    store = VectorStore()
    rag = RAGPipeline(store)

    while True:
        try:
            query = input("Enter your question (or '/exit'): ")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if query.lower() == "/exit":
            print("\nExiting...")
            break

        if not query:
            continue

        answer = rag.query(query)
        print(f"Answer: {answer}\n")


def main():
    parser = argparse.ArgumentParser(description="LLM-RAG Project CLI")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    subparser = parser.add_subparsers(dest="command", required=True)

    subparser.add_parser("prepare", help="Run data preparation steps")

    search_parser = subparser.add_parser("search", help="Search the vector store")
    search_parser.add_argument("query", type=str, help="The search query")

    subparser.add_parser("chat", help="Start an interactive chat session")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
    )

    if args.command == "prepare":
        prepare()
    elif args.command == "chat":
        chat()
    elif args.command == "search":
        search(args.query)


if __name__ == "__main__":
    main()
