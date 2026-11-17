import os
import streamlit as st
import chromadb
from rag_pipeline import answer, DB_DIR
from ingest import ingest_pdf, DATA_DIR

st.set_page_config(page_title="University AI Assistant", page_icon="🎓")
st.title("🎓 University AI Assistant")
st.caption("Ask questions based on university documents")


@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection(
        "university", metadata={"hnsw:space": "cosine"}
    )


collection = get_collection()
os.makedirs(DATA_DIR, exist_ok=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "processed" not in st.session_state:
    st.session_state.processed = set()

# ---------- Sidebar: documents ----------
with st.sidebar:
    st.header("Documents")

    uploaded_files = st.file_uploader(
        "Upload your own PDFs", type="pdf", accept_multiple_files=True
    )
    for uploaded in uploaded_files or []:
        key = (uploaded.name, uploaded.size)
        if key in st.session_state.processed:
            continue
        path = os.path.join(DATA_DIR, uploaded.name)
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
        with st.spinner(f"Reading {uploaded.name}..."):
            chunks = ingest_pdf(path, collection)
        st.session_state.processed.add(key)
        st.success(f"{uploaded.name}: {chunks} chunks added")

    if st.button("Re-read all PDFs in the data folder"):
        pdfs = sorted(f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf"))
        with st.spinner("Reading all PDFs..."):
            for pdf in pdfs:
                ingest_pdf(os.path.join(DATA_DIR, pdf), collection)
        st.success(f"Done. {len(pdfs)} PDF(s) read.")

    st.subheader("Loaded documents")
    metas = collection.get(include=["metadatas"])["metadatas"]
    counts = {}
    for meta in metas:
        counts[meta["source"]] = counts.get(meta["source"], 0) + 1
    if counts:
        for name, number in sorted(counts.items()):
            st.write(f"- {name} ({number} chunks)")
    else:
        st.write("No documents loaded yet.")

# ---------- Chat ----------
for role, text in st.session_state.history:
    with st.chat_message(role):
        st.write(text)

question = st.chat_input("Ask your university question...")
if question:
    st.session_state.history.append(("user", question))
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            text, sources = answer(question, collection)
        st.write(text)
        if sources:
            st.caption("Sources: " + "; ".join(sources))
    st.session_state.history.append(("assistant", text))