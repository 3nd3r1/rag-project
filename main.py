import argparse
import logging

import transformers
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.rule import Rule

from preparation import chunk_texts, create_texts, read_data
from rag_pipeline import RAGPipeline
from test_queries import run_tests
from vector_store import VectorStore


def prepare():
    console = Console()

    with console.status("Reading data..."):
        df = read_data("data/superstore.csv")
    console.print(f"[green]✓[/green] Loaded {len(df)} rows")

    with console.status("Creating texts..."):
        texts = create_texts(df)
    console.print(f"[green]✓[/green] Created {len(texts)} texts")

    with console.status("Chunking texts..."):
        chunks = chunk_texts(texts)
    console.print(f"[green]✓[/green] Chunked into {len(chunks)} chunks")

    with console.status("Storing embeddings..."):
        store = VectorStore()
        store.clear()
        store.add_chunks(chunks)
    console.print(f"[green]✓[/green] Stored {len(chunks)} chunks in vector store")


def search(query: str):
    console = Console()

    with console.status("Loading vector store..."):
        store = VectorStore()
    console.print("[green]✓[/green] Loaded vector store")

    results = store.search(query)

    console.print(f"\n[bold]Search results for:[/bold] {query}\n")
    console.print(Rule(style="dim"))
    for result in results:
        console.print(Markdown(result["text"]))
    console.print(Rule(style="dim"))


def chat():
    console = Console()

    with console.status("Loading vector store..."):
        store = VectorStore()
    console.print("[green]✓[/green] Loaded vector store")

    rag = RAGPipeline(store)

    console.print("\n[bold]Ledger[/bold] - type [dim]/exit[/dim] to exit\n")

    while True:
        try:
            query = console.input("[bold cyan]You:[/bold cyan] ")
        except KeyboardInterrupt:
            console.print("\n[dim]Exiting...[/dim]")
            break

        if query.lower() == "/exit":
            console.print("[dim]Exiting...[/dim]")
            break

        if not query:
            continue

        answer = rag.query(query)
        console.print(Rule(style="dim"))
        console.print(Markdown(answer))
        console.print(Rule(style="dim"))
        console.print()


def test(report_path: str | None = None):
    run_tests(report_path=report_path)


def main():
    parser = argparse.ArgumentParser(description="Ledger CLI")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    subparser = parser.add_subparsers(dest="command", required=True)

    subparser.add_parser("prepare", help="Run data preparation steps")

    search_parser = subparser.add_parser("search", help="Search the vector store")
    search_parser.add_argument("query", type=str, help="The search query")

    subparser.add_parser("chat", help="Start an interactive chat session")

    test_parser = subparser.add_parser("test", help="Run evaluation queries with LLM-as-judge")
    test_parser.add_argument("--report", metavar="FILE", help="Save markdown report to FILE")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        handlers=[RichHandler(markup=True, rich_tracebacks=True)],
    )

    if not args.debug:
        transformers.logging.set_verbosity_error()
        transformers.logging.disable_progress_bar()

    if args.command == "prepare":
        prepare()
    elif args.command == "chat":
        chat()
    elif args.command == "search":
        search(args.query)
    elif args.command == "test":
        test(report_path=getattr(args, "report", None))


if __name__ == "__main__":
    main()
