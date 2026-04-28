# Technical report

## System Architecture

- Kaggle Superstore Sales Dataset (9,994 transactions, 2014–2017).
- RAG: data is converted into natural language text chunks, embedded into a vector database, retrieved at query to provide context for LLM that generates the final answer.
- CSV → Pandas → text representations → chunking → ChromaDB → query → search → retrieved context → LLM → response

### Modules

- `main.py` (entrypoint)
- `preparation.py` (loading, text conversion, chunking)
- `vector_store.py` (ChromaDB wrapper)
- `rag_pipeline.py` (retrieval and LLM generation via LangChain)
- `evaluation.py` (evaluation of sample queries)
- `llm_provider.py` (LLM provider abstraction)
- `config.py` (configuration)

## Data Preprocessing and Chunking

- Loaded with Pandas, dates parser

### Text representation

Each order is converted to:

```text
Order {Order ID} on {Order Date}: Customer {Customer Name} from {City}, {State}, {Region} ordered {Quantity} '{Product Name}' with ship mode {Ship Mode}, generating ${Sales} in sales and ${Profit} in profit.
```

Example:

```text
Order CA-2016-152156 on 2016-11-08: Customer Claire Gute from Henderson, Kentucky, South ordered 2 'Bush Somerset Collection Bookcase' with ship mode Second Class, generating $261.96 in sales and $41.91 in profit.
```

In addition, aggregated summaries are generated for:

- Monthly sales totals and cross-year monthly aggregates
- Yearly summaries with profit margin and year × category breakdowns
- Regional, state, and city summaries
- Category, sub-category, and product summaries
- Ranking texts for states, cities, and sub-categories (by sales, profit, and profit margin)

### Chunking

- Character-based approach with default size of 500 characters.
- Transaction descriptions are 200-300 characters so they pass unchunked.

## Embedding Model and Vector Database

### Embedding (all-MiniLM-L6-v2)

all-MiniLM-L6-v2 from sentence-transformers was selected as the embedding model.

- 384-dimensional vectors
- Lightweight (~80 MB)
- CPU inference
- ChromaDB has a built-in adapter that handles embedding automatically
- The small dimensions and a bit lower quality wasn't an issue with the sample queries

Each chunk stores metadata (type, region, category, year, etc.) used for keyword-based routing at query time.

### ChromaDB

ChromaDB was chosen for its simplicity.

- In-process
- No external servers
- Persisted as local files in `chroma_db/`

## LLM Selection and Prompt Engineering

### LLM

- Tried Mistral 7B and Phi3 from Ollama but they were too slow on my hardware for iterative testing.
- Switched to Groq (cloud). Started with llama-3.1-8b-instant (7K TPM limit), then moved to openai/gpt-oss-20b (8K TPM).
- Also added Google Gemini as a provider option (generous free tier).
- Provider is configurable via environment variables — users can run locally with Ollama or use any cloud provider.

### Prompt Engineering

- System prompt instructs the LLM to act as a data analyst, use only the provided context, acknowledge when information is insufficient and cite specific numbers:

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

11 queries evaluated across 8 iterations. Final score: 4.82 / 5.00. Full reports: [evaluations.md](./evaluations.md)

### Trend Analysis

**Q: What is the sales trend over the 4-year period?** (5/5)

> Sales fell slightly from $484K (2014) to $471K (2015), then rose to $609K (2016) and $733K (2017). Overall upward trend with a brief 2015 dip.

**Q: Which months show the highest sales? Is there seasonality?** (5/5)

> November ($352K), December ($325K), September ($308K). Clear Q4 seasonality pattern.

**Q: How has profit margin changed over time?** (5/5)

> Rose from 10.23% (2014) to 13.43% (2016), declined slightly to 12.74% (2017).

### Category Analysis

**Q: Which product category generates the most revenue?** (5/5)

> Technology at $836,154.03.

**Q: What sub-categories have the highest profit margins?** (5/5)

> Labels (44.42%), Paper (43.39%), Envelopes (42.27%), Copiers (37.20%), Fasteners (31.40%).

**Q: Which products are frequently sold at a discount?** (3/5)

> Binders (90% discount rate), Chairs (84%), Tables (80%). LLM ranked by percentage instead of raw count — both valid interpretations.

### Regional Analysis

**Q: Which region has the best sales performance?** (5/5)

> West at $725,457.82.

**Q: Compare sales performance across different states.** (5/5)

> California dominates ($457K), followed by New York ($311K), Texas ($170K). Arizona is the only state with negative profit (-$3,428).

**Q: Which cities are the top performers in terms of sales?** (5/5)

> New York City ($256K), Los Angeles ($176K), Seattle ($120K), San Francisco ($113K), Philadelphia ($109K).

### Comparative Analysis

**Q: Compare Technology vs. Furniture sales trends over the years.** (5/5)

> Both grew 2014–2017. Technology +55% overall but dipped in 2015. Furniture +37% with steady growth. Furniture exceeded Technology only in 2015.

**Q: How does the West region compare to the East in terms of profit?** (5/5)

> West $108,418.45 vs East $91,522.78. West outperforms by $16,895.67.

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
8. Rate limiting in Groq
   - The evaluation suite makes 22 calls (11 RAG + 11 judge) per run. With llama-3.1-8b-instant the free tier limit was 7K tokens per minute, which was not enough. Switched to openai/gpt-oss-20b which had an 8K TPM.

## AI Usage

My AI mentality when doing course work is to only use it for tasks that are mundane or unrelated to the course.

Tools used: Claude.

- Evaluation test cases: After writing 2 test cases manually, I prompted Claude to generate the remaining 9 based on the dataset and query categories.
  - Prompt: "Here are 2 example test cases for my RAG evaluation. Generate 9 more from the sample queries in the guide. For each case compute the truth using python from the dataset and make it similar to the already existing cases."
- Debugging: Used Claude to debug LangChain logging configuration and ChromaDB embedding function type errors.
  - Prompt: "How do I disable the verbose logging from transformers and LangChain in my CLI app"
- Chunking bug: Asked Claude to investigate why ranking texts were not appearing in search results.
  - Prompt: "Why are ranking texts not visible when I search"

### Problem Analysis

- When debugging LangChain logging, Claude first suggested wrong environment variables.
  After pointing this out it searched for the correct approach using `transformers.logging.set_verbosity_error()`.
- The AI-generated test cases had correct facts but some had overly strict criteria (e.g. requiring all three categories listed for a "which is the best" question). These had to be manually relaxed.
- When ranking texts weren't showing up in search Claude correctly identified that searching just "top" was too broad semantically. More specific queries like "top states by sales" worked fine.

### Running Results

The AI-generated test cases ([commit](https://github.com/3nd3r1/ledger/commit/6211d6bdc7c746642eca2bb250af38ccf889e2fc)) were used to run the first evaluation: [evaluation-reports/report1.md](./evaluation-reports/report1.md).

### Student Contribution

I designed the whole system myself: RAG pipeline, keyword routing, text representations and evaluation approach.
Claude was used mostly for tedious tasks like generating test cases and debugging library issues.
When it came to actual decisions like how to structure the eval, what ranking texts to add, or how to fix retrieval problems, those were all mine.

## Appendix

Full RAG answers for all 11 queries: [evaluation-reports/report8.md](./evaluation-reports/report8.md)
