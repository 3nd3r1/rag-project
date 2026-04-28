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
    (["sub-category", "subcategory"], ["subcategory_summary", "subcategory_ranking"]),
    (["state"], ["state_summary", "states_ranking"]),
    (["city", "cities"], ["city_summary", "cities_ranking"]),
    (["region"], ["region_summary"]),
]


def extract_types(query: str) -> list[str]:
    q = query.lower()
    result: list[str] = []
    for keywords, chunk_types in TYPE_KEYWORDS:
        if any(keyword in q for keyword in keywords):
            result.extend(chunk_types)
    return list(dict.fromkeys(result))


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
        docs = self._store.search(query, n_results=self._top_k, where=where)
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
