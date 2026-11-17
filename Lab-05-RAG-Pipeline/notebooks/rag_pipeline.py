import os
import json
import urllib.request
import chromadb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
CHAT_URL = "http://localhost:11434/api/chat"
EMBED_URL = "http://localhost:11434/api/embed"
LLM_MODEL = "llama3.2:3b"
EMBED_MODEL = "qwen3-embedding:0.6b"


def post_json(url, payload):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def embed(texts):
    return post_json(EMBED_URL, {"model": EMBED_MODEL, "input": texts})["embeddings"]


def retrieve(question, collection, k=4):
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_embeddings=embed([question]), n_results=min(k, count)
    )
    return list(zip(results["documents"][0], results["metadatas"][0]))


def answer(question, collection):
    found = retrieve(question, collection)
    if not found:
        return "The knowledge base is empty. Run ingest.py first.", []

    context = "\n\n".join(
        f"[Source: {meta['source']}, page {meta['page']}]\n{doc}" for doc, meta in found
    )
    messages = [
        {
            "role": "system",
            "content": "You are a university assistant. Answer the question using ONLY the "
                       "context below. If the answer is not in the context, say that you "
                       "cannot find it in the provided documents. Be clear and concise.\n\n"
                       f"CONTEXT:\n{context}",
        },
        {"role": "user", "content": question},
    ]
    reply = post_json(
        CHAT_URL,
        {"model": LLM_MODEL, "messages": messages, "stream": False, "options": {"temperature": 0}},
    )
    sources = sorted({f"{meta['source']} (page {meta['page']})" for _, meta in found})
    return reply["message"]["content"], sources


if __name__ == "__main__":
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(
        "university", metadata={"hnsw:space": "cosine"}
    )
    print(f"Knowledge base: {collection.count()} chunks")
    while True:
        question = input("\nAsk a university question (or exit): ").strip()
        if question.lower() in ["exit", "quit"]:
            break
        if not question:
            continue
        text, sources = answer(question, collection)
        print("\nAnswer:", text)
        if sources:
            print("\nSources:", "; ".join(sources))