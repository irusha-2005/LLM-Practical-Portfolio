import os
import hashlib
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama

CHROMA_DIR = "chroma_db"
COLLECTION = "university_docs"
LLM_MODEL = "llama3.2:3b"
EMBED_MODEL = "qwen3-embedding:0.6b"

embeddings = OllamaEmbeddings(model=EMBED_MODEL)
llm = ChatOllama(model=LLM_MODEL, temperature=0)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def get_vectorstore():
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


def load_pdf(path):
    """Read a PDF page by page and return LangChain Documents."""
    docs = []
    name = os.path.basename(path)
    with fitz.open(path) as pdf:
        for i, page in enumerate(pdf):
            text = page.get_text().strip()
            if text:
                docs.append(Document(page_content=text,
                                     metadata={"source": name, "page": i + 1}))
    return docs


def ingest_pdf(path):
    """Add one PDF to the vector database. Same file = no duplicates."""
    with open(path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:12]
    chunks = splitter.split_documents(load_pdf(path))
    if not chunks:
        return 0
    ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
    get_vectorstore().add_documents(chunks, ids=ids)
    return len(chunks)


def ingest_folder(folder="data"):
    total = 0
    for file in sorted(os.listdir(folder)):
        if file.lower().endswith(".pdf"):
            n = ingest_pdf(os.path.join(folder, file))
            print(f"{file}: {n} chunks")
            total += n
    return total


def list_documents():
    data = get_vectorstore().get(include=["metadatas"])
    return sorted({m["source"] for m in data["metadatas"]})


PROMPT = """You are a university assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I could not find this in the documents."

Context:
{context}

Question: {question}

Answer:"""


def ask(question, k=5):
    results = get_vectorstore().similarity_search(question, k=k)
    context = "\n\n".join(
        f"[{d.metadata['source']} p.{d.metadata['page']}]\n{d.page_content}"
        for d in results
    )
    answer = llm.invoke(PROMPT.format(context=context, question=question)).content
    sources = sorted({f"{d.metadata['source']} (page {d.metadata['page']})" for d in results})
    return answer, sources


if __name__ == "__main__":
    while True:
        q = input("\nAsk a university question (or exit): ")
        if q.strip().lower() == "exit":
            break
        a, s = ask(q)
        print("\nAnswer:", a)
        print("Sources:", ", ".join(s))
