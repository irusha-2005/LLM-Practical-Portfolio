"""Group 1 - Hybrid Retrieval (BM25 + Vector), Rank Fusion (RRF) and LLM Reranking."""
import re
import time
from rank_bm25 import BM25Okapi
from rag_pipeline import get_vectorstore, embeddings, llm, PROMPT

MODES = {
    "baseline": "Baseline (vector only)",
    "bm25": "BM25 only",
    "hybrid": "Hybrid (BM25 + vector + RRF)",
    "hybrid_rerank": "Hybrid + LLM reranking",
}

_cache = {"count": -1, "bm25": None, "chunks": []}


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def _index():
    """Build the BM25 index from all chunks stored in ChromaDB (rebuilt when documents change)."""
    data = get_vectorstore().get(include=["documents", "metadatas"])
    n = len(data["ids"])
    if n != _cache["count"]:
        _cache["chunks"] = [
            {"id": i, "text": d, "meta": m}
            for i, d, m in zip(data["ids"], data["documents"], data["metadatas"])
        ]
        _cache["bm25"] = BM25Okapi([tokenize(c["text"]) for c in _cache["chunks"]]) if n else None
        _cache["count"] = n
    return _cache


def dense_search(question, k):
    vs = get_vectorstore()
    emb = embeddings.embed_query(question)
    res = vs._collection.query(query_embeddings=[emb], n_results=k,
                               include=["documents", "metadatas"])
    return [{"id": i, "text": d, "meta": m}
            for i, d, m in zip(res["ids"][0], res["documents"][0], res["metadatas"][0])]


def bm25_search(question, k):
    idx = _index()
    if idx["bm25"] is None:
        return []
    scores = idx["bm25"].get_scores(tokenize(question))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [idx["chunks"][i] for i in top if scores[i] > 0]


def rrf_fuse(result_lists, c=60):
    """Reciprocal Rank Fusion: score = sum(1 / (c + rank))."""
    scores, items = {}, {}
    for results in result_lists:
        for rank, chunk in enumerate(results):
            scores[chunk["id"]] = scores.get(chunk["id"], 0) + 1 / (c + rank + 1)
            items[chunk["id"]] = chunk
    return [items[i] for i in sorted(scores, key=scores.get, reverse=True)]


def llm_rerank(question, candidates):
    """Ask the LLM to score each candidate passage 0-10, then sort by score."""
    scored = []
    for rank, c in enumerate(candidates):
        prompt = (f"Question: {question}\n\nPassage:\n{c['text'][:700]}\n\n"
                  "Rate how useful the passage is for answering the question, "
                  "from 0 (useless) to 10 (fully answers it). Reply with only the number.")
        out = llm.invoke(prompt).content
        m = re.search(r"\d+(?:\.\d+)?", out)
        score = min(float(m.group()), 10) if m else 0
        scored.append((score, -rank, c))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [c for _, _, c in scored]


def retrieve(question, mode="hybrid", k=5, pool=10):
    if mode == "baseline":
        return dense_search(question, k)
    if mode == "bm25":
        return bm25_search(question, k)
    fused = rrf_fuse([dense_search(question, pool), bm25_search(question, pool)])
    if mode == "hybrid":
        return fused[:k]
    return llm_rerank(question, fused[:8])[:k]


def answer_from(question, chunks):
    context = "\n\n".join(
        f"[{c['meta']['source']} p.{c['meta']['page']}]\n{c['text']}" for c in chunks)
    return llm.invoke(PROMPT.format(context=context, question=question)).content


def ask(question, mode="hybrid", k=5):
    t0 = time.time()
    chunks = retrieve(question, mode, k)
    answer = answer_from(question, chunks)
    sources = sorted({f"{c['meta']['source']} (page {c['meta']['page']})" for c in chunks})
    return answer, sources, time.time() - t0
