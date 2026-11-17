import os
import json
import urllib.request
import chromadb
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "qwen3-embedding:0.6b"


def embed(texts):
    request = urllib.request.Request(
        EMBED_URL,
        data=json.dumps({"model": EMBED_MODEL, "input": texts}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())["embeddings"]


def split_text(text, size=800, overlap=100):
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def ingest_pdf(path, collection):
    name = os.path.basename(path)
    reader = PdfReader(path)
    ids, documents, metadatas = [], [], []
    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for i, piece in enumerate(split_text(text)):
            if len(piece.strip()) > 30:
                ids.append(f"{name}-p{page_no}-c{i}")
                documents.append(piece)
                metadatas.append({"source": name, "page": page_no})

    for i in range(0, len(documents), 16):
        batch_docs = documents[i:i + 16]
        collection.upsert(
            ids=ids[i:i + 16],
            documents=batch_docs,
            embeddings=embed(batch_docs),
            metadatas=metadatas[i:i + 16],
        )
        print(f"  {name}: stored {min(i + 16, len(documents))} of {len(documents)} chunks")
    return len(documents)


if __name__ == "__main__":
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(
        "university", metadata={"hnsw:space": "cosine"}
    )
    pdfs = sorted(f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf"))
    if not pdfs:
        print("No PDF found. Put a PDF in the data folder first.")
    total = 0
    for pdf in pdfs:
        print("Reading", pdf)
        total += ingest_pdf(os.path.join(DATA_DIR, pdf), collection)
    print(f"Done. {total} chunks stored. Database size: {collection.count()}")