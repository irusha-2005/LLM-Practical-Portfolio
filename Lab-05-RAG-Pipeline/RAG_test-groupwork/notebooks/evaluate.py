"""Compare retrieval methods. Run:  python evaluate.py            (retrieval metrics, fast)
                                    python evaluate.py --answers  (also answer correctness, slower)"""
import json
import re
import sys
import time
from hybrid_rag import retrieve, answer_from, MODES

WITH_ANSWERS = "--answers" in sys.argv
K = 5

data = json.load(open("eval_dataset.json", encoding="utf-8"))


def is_relevant(chunk, pages):
    m = chunk["meta"]
    return "handbook" in m["source"].lower() and m["page"] in pages


def correctness(answer, keywords):
    found = sum(1 for kw in keywords if re.search(kw, answer, re.IGNORECASE))
    return found / len(keywords)


retrieve("warm up", "baseline", 1)  # load models once so latency is fair

rows = []
for mode in MODES:
    hits, rrs, lats, cors = [], [], [], []
    for item in data:
        t0 = time.time()
        chunks = retrieve(item["question"], mode, K)
        lats.append(time.time() - t0)
        rank = next((i + 1 for i, c in enumerate(chunks)
                     if is_relevant(c, item["supporting_pages"])), None)
        hits.append(1 if rank else 0)
        rrs.append(1 / rank if rank else 0)
        if WITH_ANSWERS:
            cors.append(correctness(answer_from(item["question"], chunks), item["keywords"]))
    n = len(data)
    rows.append({
        "Method": MODES[mode],
        "Recall@5": sum(hits) / n,
        "MRR": sum(rrs) / n,
        "Answer correctness": (sum(cors) / n) if WITH_ANSWERS else None,
        "Avg retrieval latency (s)": sum(lats) / n,
    })
    print(f"done: {MODES[mode]}")

lines = ["| Method | Recall@5 | MRR | Answer correctness | Avg retrieval latency (s) |",
         "|---|---|---|---|---|"]
for r in rows:
    cor = f"{r['Answer correctness']:.2f}" if r["Answer correctness"] is not None else "-"
    lines.append(f"| {r['Method']} | {r['Recall@5']:.2f} | {r['MRR']:.2f} | {cor} | "
                 f"{r['Avg retrieval latency (s)']:.2f} |")
table = "\n".join(lines)
print("\n" + table)
open("results.md", "w", encoding="utf-8").write(table)
print("\nSaved to results.md")
