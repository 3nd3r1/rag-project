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
