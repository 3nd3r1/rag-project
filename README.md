<p align="center">
    <img src="docs/images/logo-dark.png" alt="Ledger logo" width="500"/>
</p>
<p align="center">
    RAG LLM CLI for querying the Superstore dataset.
</p>

## About

Ledger is a RAG chatbot for analyzing sales data.
It processes the [Superstore dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final), creates vector embeddings of aggregated sales texts and lets you chat about sales trends, regional performance, product categories and more.

The system has been iteratively evaluated using an LLM-as-judge approach with truth references and criteria-based scoring.
See the [evaluation reports](./docs/evaluations.md) for details.

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure an LLM provider (see Providers section below)
cp .env.example .env  # edit with your provider/key

# 3. Prepare the vector store
python main.py prepare

# 4. Start chatting
python main.py chat
```

## Usage

```bash
# Search the vector store directly
python main.py search "top selling products"

# Run the evaluation suite
python main.py evaluate --report report.md

# Enable debug logging
python main.py --debug chat
```

## Providers

Ledger currently supports [Ollama](https://ollama.com) and [Groq](https://groq.com)

Configure via environment variables:

```bash
# Ollama (default)
LLM_PROVIDER=ollama
LLM_MODEL=phi3

# Groq
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=your_key
```

## Documentation

Read the technical report here: [./docs/technical-report.md](./docs/technical-report.md).
