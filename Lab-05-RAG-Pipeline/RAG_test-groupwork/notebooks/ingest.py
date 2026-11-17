from rag_pipeline import ingest_folder

if __name__ == "__main__":
    total = ingest_folder("data")
    print(f"Done. {total} chunks stored in chroma_db.")
