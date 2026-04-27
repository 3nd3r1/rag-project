# Technical report

## System Architecture

- Kaggle Superstore Sales Dataset (9,994 transactions, 2014–2017).
- RAG: data is converted into natural language text chunks, embedded into a vector database, retrieved at query to provide context for LLM that generates the final answer.
- CSV → Pandas → text representations → chunking → ChromaDB → query → search → retrieved context → LLM → response

### Modules

- `main.py` (entrypoint)
- `data_preparation.py` (loading, text conversion, chunking),
- `vector_store.py` (ChromaDB wrapper),
- `rag_pipeline.py` (retrieval and LLM generation via LangChain).
- `evaluation.py` (Evaluation of sample queries).

## Data Preprocessing and Chunking

- Loaded with Pandas, dates parser

### Text representation

Each order is converted to:

```text
Order {Order ID} on {Order Date}: Customer {Customer Name} ({Customer Segment}) from {City}, {State} ({Region}). Ordered '{Product Name}' in category {Category}/{Sub-Category}. Sales: ${Sales}, Quantity: {Quantity}, Discount: {Discount}%, Profit: ${Profit}.
```

Example:

```text
Order CA-2016-152156 on 2016-11-08: Customer Claire Gute (Consumer segment) from Henderson, Kentucky (South region). Ordered 'Bush Somerset Collection Bookcase' in category Furniture/Bookcases. Sales: $261.96, Quantity: 2, Discount: 0%, Profit: $41.91.
```

In addition summaries are generated for monthly sales totals, category/sub-category performance statistics and regional breakdowns by state.

### Chunking

- Character-based approach with default size of 1,000 characters.
- Transaction descriptions are 200-300 characters so they pass unchunked.

## Embedding Model and Vector Database

### Embedding (all-MiniLM-L6-v2)

all-MiniLM-L6-v2 from sentence-transformers was selected as the embedding model.

- 384-dimensional vectors
- Lightweight (~80 MB)
- CPU inference
- ChromaDB has a built-in adapter that handles embedding automatically
- The small dimensions and a bit lower quality wasn't an issue with the sample queries

TODO: Something about metadata

### ChromaDB

ChromaDB was chosen for its simplicity.

- In-process
- No external servers
- Persisted as local files in `chroma_db/`

## LLM Selection and Prompt Engineering

### LLM

- We tried Mistral 7B and Phi3 from Ollama but they took a very long time to respond on my minimal hardware making testing impossible.
- Switched to llama-3.1-8b-instant from Groq which is much faster due to being external.
- Still kept a flag to switch model providers very easily for users who want to run locally.

### Prompt Engineering

- System prompt instructs the LLM to act as a data anlyst, use only the provided context, acknowledge when information is insufficient and cite specific numbers:

```text
You are a data analyst assistant.
You answer questions about the Superstore dataset.
Use only the provided context to answer.
If the context doesn't contain enough information, say that there is not enough information.
Always cite specific data.
```

- The chunks are numbered and inserted into the prompt as context followed by the query:

```python
RAG_TEMPLATE = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer based on the context above:"
)
```

## Sample Queries and Responses

### Trend Analysis:

- What is the sales trend over the 4-year period?
- Which months show the highest sales? Is there seasonality?
- How has profit margin changed over time?

### Category Analysis:

- Which product category generates the most revenue?
- What sub-categories have the highest profit margins?
- Which products are frequently sold at a discount?

### Regional Analysis:

- Which region has the best sales performance?
- Compare sales performance across different states.
- Which cities are the top performers?

### Comparative Analysis:

- Compare Technology vs. Furniture sales trends.
- How does the West region compare to the East in terms of profit?

## Challenges and Solutions

1. UTF-8 didn't work
   - Use latin-1
2. Type-checker issues
   - Ignore
3. Langchain changes
4. Local models being unusable on my hardware
   - I uses Groq
5. Using a jupyter notebook or CLi executable
   - I went with a CLI executable since I am not fond of Jupyter notebooks.
6. Too small top_k to get state and city chunks
   - Increase top_k to 20 so all queries fit
7. Vector search cannot rank by numeric values
   - Cosine similarity ranks by text relevance, not by metrics like sales or profit. Queries like "top cities by sales" retrieve semantically similar chunks, not the highest-value ones. ChromaDB does not support ordering by metadata fields.
     The workaround is pre-computed ranking summaries at index time (Top cities by sales) so the answer exists as a single retrievable chunk.

## AI Usage

My AI mentality when doing course work is to only use it for tasks that are mundane or unrelated to the course.

- After generating 2 test cases manually I asked Claude to generate the rest of the test cases for me.
- Debugging how to disable logs generated by LangChain.
