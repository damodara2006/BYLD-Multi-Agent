import os
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from portfolio_ask.indexer import load_and_split_documents

CHROMA_PATH = "chroma_db"

def get_vector_store() -> Chroma:
    """Returns a connected Chroma vector store instance."""
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

def build_vector_store():
    """Initializes the vector store and adds documents if empty."""
    print("Initializing document embedding and indexing...")
    docs = load_and_split_documents("data")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    if not os.path.exists(CHROMA_PATH):
        db = Chroma.from_documents(docs, embeddings, persist_directory=CHROMA_PATH)
        print(f"Indexed {len(docs)} chunks successfully.")
    else:
        print("Vector store already exists. Skipping rebuild.")

if __name__ == "__main__":
    build_vector_store()
