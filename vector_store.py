import chromadb
from chromadb.utils import embedding_functions


class VectorStore:
    def __init__(self):
        self._embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        self._client = chromadb.PersistentClient(path="./chromadb")
        self._collection = self._client.get_or_create_collection(
            name="superstore",
            embedding_function=self._embedding_function,  # type: ignore
        )
