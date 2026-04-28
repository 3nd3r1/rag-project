# Technical Report

## System Architecture

The system is a RAG chatbot that answers questions about the Superstore dataset (9,994 transactions, 2014–2017). The pipeline works like this: the CSV is loaded with Pandas, converted into natural language text chunks, embedded into ChromaDB and then at query time the most relevant chunks are retrieved and passed to an LLM which generates the answer.

The codebase is split into a few modules:

- `main.py` — CLI entrypoint (prepare, search, chat, evaluate commands)
- `preparation.py` — data loading, text generation, chunking
- `vector_store.py` — ChromaDB wrapper
- `rag_pipeline.py` — retrieval + LLM generation via LangChain
- `evaluation.py` — LLM-as-judge evaluation suite
- `llm_provider.py` — provider abstraction (Ollama, Groq, Google)
- `config.py` — environment-based configuration

## Data Preprocessing and Chunking

The dataset is loaded with Pandas and dates are parsed. Each row gets converted into a natural language sentence:

```
Order CA-2016-152156 on 2016-11-08: Customer Claire Gute from Henderson,
Kentucky, South ordered 2 'Bush Somerset Collection Bookcase' with ship mode
Second Class, generating $261.96 in sales and $41.91 in profit.
```

On top of the individual rows, I generate aggregated summary texts: monthly totals, cross-year monthly aggregates, yearly summaries with profit margins, year × category breakdowns, region/state/city summaries, category and sub-category summaries, product summaries, and ranking texts for states, cities, and sub-categories by sales, profit, and profit margin.

The ranking texts were a key addition, without them the system couldn't answer questions like "top states by sales" because cosine similarity doesn't understand numeric ordering.
Pre-computing the rankings as retrievable text chunks solved this.

Chunking is character-based with a 500-character limit.
Most texts are under that so they pass through unchunked.
Longer texts (like ranking lists) get split at word boundaries.

## Embedding Model and Vector Database

I went with `all-MiniLM-L6-v2` for embeddings.
It's lightweight (~80 MB), runs on CPU, produces 384-dimensional vectors and ChromaDB has a built-in adapter for it so there's no extra setup.
The quality is good enough for the kind of queries we're doing here.

ChromaDB was chosen because it's simple: runs in-process, no external servers, just persists to local files.
Each chunk is stored with metadata (type, region, category, year, etc.) which is used later for keyword-based routing.

## LLM Selection and Prompt Engineering

I first tried running Mistral 7B and Phi3 locally through Ollama but they were painfully slow on my hardware, making iterative testing impossible.
I switched to Groq's cloud API.
Started with `llama-3.1-8b-instant` but hit the 7K tokens/minute rate limit during evaluation runs.
Moved to `openai/gpt-oss-20b` which had a slightly higher 8K TPM limit.
The provider is configurable via `.env` so anyone can switch between local and cloud.

The system prompt tells the LLM to act as a data analyst, only use the provided context and always cite specific numbers.
I also added keyword-based routing before the vector search, if the query mentions "state", it filters to state summaries and rankings, if it mentions "category", it filters to category chunks, etc.
This made a huge difference in retrieval quality.

```text
You are a data analyst assistant.
You answer questions about the Superstore dataset.
Use only the provided context to answer.
If the context doesn't contain enough information, say that there is not enough information.
Always cite specific data.
```

The retrieved chunks are inserted as context followed by the query:

```
Context:
{context}

Question: {question}

Answer based on the context above:
```

## Sample Queries and Responses

The system was evaluated with 11 queries across 4 categories using an LLM-as-judge approach.
Each answer is scored 1–5 against ground truth references and criteria.
The system went through 8 iterative versions, improving from 3.73 (v6) to 4.82 (v8).
10 out of 11 queries scored 5/5. Full evaluation history: [evaluations.md](./evaluations.md)

| Category    | Query                                | Score |
| ----------- | ------------------------------------ | ----- |
| Trend       | Sales trend over 4 years             | 5/5   |
| Trend       | Highest sales months / seasonality   | 5/5   |
| Trend       | Profit margin over time              | 5/5   |
| Category    | Top revenue category                 | 5/5   |
| Category    | Highest profit margin sub-categories | 5/5   |
| Category    | Products frequently sold at discount | 3/5   |
| Regional    | Best sales region                    | 5/5   |
| Regional    | State sales comparison               | 5/5   |
| Regional    | Top cities by sales                  | 5/5   |
| Comparative | Technology vs Furniture trends       | 5/5   |
| Comparative | West vs East profit                  | 5/5   |

The one failing query (discount ranking, 3/5) is because the LLM ranked sub-categories by discount rate (percentage) instead of raw count.
Both are valid interpretations of "frequently sold at a discount."

## Challenges and Solutions

### CSV Encoding

UTF-8 didn't work with the dataset. Switched to latin-1.

### Local Models Too Slow

Ollama models (Mistral 7B, Phi3) were unusable on my hardware. Switched to Groq cloud.

### Jupyter vs CLI

Went with a CLI since I prefer working in the terminal.

### Small top_k

State and city queries need a lot of context. Increased top_k from 10 to 20.

### Vector Search Can't Rank Numerically

Cosine similarity finds semantically similar text, not the highest sales numbers.
Solved by pre-computing ranking texts at index time so "Top 10 states by sales: 1. California $457K..." exists as a single retrievable chunk.

### Groq Rate Limits

The evaluation suite makes 22 calls (11 RAG + 11 judge) per run.
With llama-3.1-8b-instant the free tier limit was 7K tokens per minute, which was not enough.
Switched to openai/gpt-oss-20b which had an 8K TPM.

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
