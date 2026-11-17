| Method | Recall@5 | MRR | Answer correctness | Avg retrieval latency (s) |
|---|---|---|---|---|
| Baseline (vector only) | 0.94 | 0.77 | 0.88 | 0.14 |
| BM25 only | 0.94 | 0.77 | 0.81 | 0.01 |
| Hybrid (BM25 + vector + RRF) | 0.94 | 0.94 | 0.88 | 0.53 |
| Hybrid + LLM reranking | 0.94 | 0.88 | 0.94 | 35.14 |