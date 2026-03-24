# all the files in 'data', are processed by the seeder
# this file is responsible for seeding the data into the vector database
# it reads the files, processes them, and stores them in the database

# file → extract text → chunk → embed → store in ChromaDB

# TOOLS.JSON only needed if we use different app (like cursor) but want to use the same server

import os
import shutil
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- PATH ADJUSTMENT FOR SRC/ STRUCTURE ---
# Since this file is in 'src/', we go up one level to reach the project root
BASE_DIR = Path(__file__).parent.parent.resolve()

DATA_PATH = BASE_DIR / "data" # folder containing files to be processed
CHROMA_PATH = BASE_DIR / "chroma_db" # folder to store ChromaDB

# finds all relevant files in the 'data' folder
# loads them into documents with metadata
# and package it into a format that the AI can understand and work with
def load_documents():
    if not DATA_PATH.exists():
        print(f" Data folder not found: {DATA_PATH}")
        return []

    loaders = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
    }

    print(f"--- Loading documents from {DATA_PATH} ---")
    all_documents = []

    for ext, loader_cls in loaders.items():
        loader = DirectoryLoader(
            str(DATA_PATH),
            glob=f"**/*{ext}",
            loader_cls=loader_cls,
            show_progress=True,
            use_multithreading=True 
        )
        
        try:
            docs = loader.load()
            
            # Attach filename metadata (useful for retrieval later)
            for d in docs:
                original_path = d.metadata.get("source", "")
                clean_filename = Path(original_path).name
                d.metadata["source_file"] = clean_filename
                
            all_documents.extend(docs)
        except Exception as e:
            print(f" Error loading {ext} files: {e}")

    return all_documents


# primary job is to take the massive strings of text extracted from your PDFs and Text files
# and break them into smaller, pieces
def chunk_documents(documents):
    """Split documents into fixed-size chunks."""

    print(f"--- Splitting {len(documents)} documents into chunks ---")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    # add chunk index metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    print(f"Created {len(chunks)} chunks.")
    return chunks

def embed_and_store(chunks):
    """Embed chunks and persist to ChromaDB."""

    print("--- Embedding and storing in ChromaDB ---")

    # Using the same model as your mcp_server.py is CRITICAL for retrieval
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(CHROMA_PATH),
    )

    if hasattr(db, 'persist'):
        db.persist()
        
    print(f"Success! Database created at '{CHROMA_PATH}'")

def main():
    # Clear existing database if you want a clean sync
    if CHROMA_PATH.exists():
        print(" Clearing existing ChromaDB for fresh sync...")
        shutil.rmtree(CHROMA_PATH)

    documents = load_documents()

    if not documents:
        print("No documents found in the data folder.")
        return

    chunks = chunk_documents(documents)

    embed_and_store(chunks)


if __name__ == "__main__":
    main()


# take files from 'data'
# process them into chunks
# store them in the vector database