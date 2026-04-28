# Evaluation Reports

The RAG system is iteratively evaluated using an LLM-as-judge approach.
Each version is tested against 11 queries covering trend analysis, category performance and regional comparisons.
The judge scores each answer 1–5 against ground truth references and criteria that define what a good answer looks like.
Each version has the changes made, issues found and links to the full evaluation report.

## Version 1

### Changes

- Cosine search only

### Issues

- Bad judge prompt led to incorrect scoring
- Missing sub-category texts
- Comparative queries performed poorly

Commit: https://github.com/3nd3r1/ledger/commit/c8903ea04f53b93f885123cf5f9104801cad145

Result: [evaluation-reports/report1.md](./evaluation-reports/report1.md)

## Version 2

### Changes

- Fixed the judge prompt

### Issues

- Missing sub-category texts
- Comparative queries performed poorly
- A lot of missing data in the context

Commit: https://github.com/3nd3r1/ledger/commit/86aa0fb6ea532154bd1576cec096c170f0a62984

Result: [evaluation-reports/report2.md](./evaluation-reports/report2.md)

## Version 3

### Changes

- Added sub-category summary texts
- Added product summary texts

### Issues

- Missing state and city texts
- Missing yearly and year × category texts
- Comparative and trend queries performed poorly

Commit: https://github.com/3nd3r1/ledger/commit/e0d9cb11c7b1231c92a03903dfb1dc056b9bf8bc
Result: [evaluation-reports/report3.md](./evaluation-reports/report3.md)

## Version 4

### Changes

- Added state and city summary texts
- Added yearly summary texts with profit margin
- Added year × category summary texts
- Added metadata to all chunks
- Fixed product name missing from product summaries
- Fixed discounted orders count using vectorized aggregation

### Issues

- Year summaries not included in trend queries
- Bad monthly aggregation over the years. The queries only get individual months so no seasonality is detected
- Discount query gets product-level chunks instead of sub-category
- State and city retrieval returns wrong results

Commit: https://github.com/3nd3r1/ledger/commit/ffd1879e037c990a51d61c2dd27f82d2af772c71
Result: [evaluation-reports/report4.md](./evaluation-reports/report4.md)

## Version 5

### Changes

- Added cross-year monthly aggregate texts
- Improved month text clarity
- Increased top_k to 20 so region and state results fit in context

### Issues

- Category and sub-category queries failed
- Trend queries still fail
- Discount query still retrieves product-level chunks instead of sub-category
- State and city retrieval improved but incomplete

Commit: https://github.com/3nd3r1/ledger/commit/1e533a00ef8dfd1227a2fc89f4fa09aa4f3b569f
Result: [evaluation-reports/report5.md](./evaluation-reports/report5.md)

## Version 6

### Changes

- Added keyword-based metadata routing to filter chunks by type per query

### Issues

- Seasonality query still partially wrong
- Sub-category profit margin ranking incorrect
- State and city retrieval still incomplete

Commit: https://github.com/3nd3r1/ledger/commit/d8f549cfb0812fb3771c1e9a170457774011b8af
Result: [evaluation-reports/report6.md](./evaluation-reports/report6.md)

## Version 7

### Changes

- Added criteria-based evaluation alongside ground truth scoring
- Fixed chunk_texts bug where chunks were not split correctly
- Added ranking texts

### Issues

- Sub-category profit margin query scored 2/5. Create ranking text for profit margins·
- Seasonality query scored 3/5. Correct data but LLM says "not enough information to confirm seasonality".
- West vs East profit comparison scored 4/5. Small error ($16,095.67 instead of $16,895.67)

Commit: https://github.com/3nd3r1/ledger/commit/c660d3f
Result: [evaluation-reports/report7.md](./evaluation-reports/report7.md)

## Version 8

### Changes

- Added subcategory ranking texts
- Switched from llama-3.1-8b-instant to openai/gpt-oss-20b

### Issues

- Discount query scored 3/5. The answer was still correct but the criteria was unclear.

Commit: https://github.com/3nd3r1/ledger/commit/b4c8733
Result: [evaluation-reports/report8.md](./evaluation-reports/report8.md)
