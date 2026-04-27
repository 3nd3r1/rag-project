import logging

from langchain_core.prompts import PromptTemplate

from llm_provider import create_llm, invoke_llm
from vector_store import VectorStore


logger = logging.getLogger(__name__)


TYPE_KEYWORDS: list[tuple[list[str], list[str]]] = [
    (
        ["trend", "over the year", "4-year", "four-year", "year-over-year"],
        ["year_summary", "year_category_summary"],
    ),
    (["season", "which month", "monthly"], ["month_aggregate_summary"]),
    (["discount"], ["subcategory_summary"]),
    (["category"], ["category_summary"]),
    (["sub-category", "subcategory"], ["subcategory_summary"]),
    (["state"], ["state_summary"]),
    (["city", "cities"], ["city_summary"]),
    (["region"], ["region_summary"]),
]


TYPE_MAX_CHUNKS: dict[str, int] = {
    "month_aggregate_summary": 12,
    "subcategory_summary": 17,
    "category_summary": 3,
    "region_summary": 4,
    "year_summary": 4,
    "year_category_summary": 12,
    "state_summary": 50,
    "city_summary": 30,
}


def extract_types(query: str) -> list[str]:
    q = query.lower()
    result: list[str] = []
    for keywords, chunk_types in TYPE_KEYWORDS:
        if any(keyword in q for keyword in keywords):
            result.extend(chunk_types)
    return list(dict.fromkeys(result))


RANK_KEYWORDS = [
    "top",
    "best",
    "highest",
    "most",
    "lowest",
    "worst",
    "least",
    "rank",
    "compare",
]

SORT_KEYWORDS: list[tuple[list[str], str]] = [
    (["sales", "revenue", "sales?", "revenue?"], "total_sales"),
]


def extract_sort_key(query: str) -> str | None:
    q = query.lower()
    if not any(keyword in q for keyword in RANK_KEYWORDS):
        return None
    for keywords, field in SORT_KEYWORDS:
        if any(keyword in q for keyword in keywords):
            return field
    return None


SYSTEM_PROMPT = """You are a data analyst assistant.
You answer questions about the Superstore dataset.
Use only the provided context to answer.
If the context doesn't contain enough information, say that there is not enough information.
Always cite specific data."""

RAG_TEMPLATE = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer based on the context above:"
)


class RAGPipeline:
    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = 20,
    ):
        self._store = vector_store
        self._top_k = top_k

        self._llm = create_llm()

    def retrieve(self, query: str) -> list[dict]:
        types = extract_types(query)
        where = {"type": {"$in": types}} if len(types) > 0 else None
        top_k = (
            max(
                (TYPE_MAX_CHUNKS.get(t, self._top_k) for t in types),
                default=self._top_k,
            )
            if len(types) > 0
            else self._top_k
        )
        docs = self._store.search(query, n_results=top_k, where=where)
        sort_key = extract_sort_key(query)
        if sort_key:
            docs.sort(key=lambda d: d["metadata"].get(sort_key, 0), reverse=True)
        logger.debug(
            f"Retrieved {len(docs)} docs (route={types}), distances: {[round(d['distance'], 3) for d in docs]}"
        )
        return docs

    def query(self, question: str) -> str:
        docs = self.retrieve(question)
        if not docs:
            return "No relevant documents found."

        context = "\n\n".join(f"{doc['text']}" for doc in docs)
        prompt = RAG_TEMPLATE.format(context=context, question=question)
        logger.debug("Sending prompt to LLM")
        return invoke_llm(self._llm, prompt)
