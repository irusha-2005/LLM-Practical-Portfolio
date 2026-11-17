import os
import streamlit as st
from rag_pipeline import ingest_pdf, list_documents
from hybrid_rag import ask, MODES

st.set_page_config(page_title="University AI Assistant", page_icon="🎓")
st.title("🎓 University AI Assistant")
st.caption("Ask questions based on university documents")

os.makedirs("data", exist_ok=True)

with st.sidebar:
    st.header("⚙️ Retrieval method")
    mode = st.selectbox("Method", list(MODES.keys()),
                        index=2, format_func=lambda m: MODES[m])

    st.header("📄 Documents")
    uploaded = st.file_uploader("Upload your own PDFs", type="pdf",
                                accept_multiple_files=True)
    if st.button("Add to knowledge base") and uploaded:
        for f in uploaded:
            path = os.path.join("data", f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            with st.spinner(f"Reading {f.name}..."):
                n = ingest_pdf(path)
            st.success(f"{f.name}: {n} chunks added")

    st.subheader("Available documents")
    for name in list_documents():
        st.write("•", name)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

question = st.chat_input("Ask your university question...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, sources, secs = ask(question, mode)
        st.markdown(answer)
        st.caption(f"Method: {MODES[mode]} | Time: {secs:.1f}s")
        with st.expander("Sources"):
            for s in sources:
                st.write("•", s)

    st.session_state.messages.append({"role": "assistant", "content": answer})
