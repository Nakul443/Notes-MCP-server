# all the files in 'data', are processed by the seeder
# this file is responsible for seeding the data into the vector database
# it reads the files, processes them, and stores them in the database

# file → extract text → chunk → embed → store in ChromaDB

# TOOLS.JSON only needed if we use different app (like cursor) but want to use the same server

import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Base project directory (safe even when script runs from elsewhere)
# BASE_DIR represents the directory where seeder.py is located
BASE_DIR = Path(__file__).parent


DATA_PATH = BASE_DIR / "data" # folder containing files to be processed
CHROMA_PATH = BASE_DIR / "chroma_db" # folder to store ChromaDB

# finds all relevant files in the 'data' folder
# loads them into documents with metadata
# and package it into a format that the AI can understand
def load_documents():
    if not DATA_PATH.exists():
        print(f" Data folder not found: {DATA_PATH}")
        return []

    loaders = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
    }

    print(f"--- Loading documents from {DATA_PATH} ---")
    documents = []

    for ext, loader_cls in loaders.items():
        loader = DirectoryLoader(
            str(DATA_PATH),
            glob=f"**/*{ext}",
            loader_cls=loader_cls,
            show_progress=True,
        )
        docs = loader.load()

        # Attach filename metadata (useful for retrieval later)
        for d in docs:
            d.metadata["source_file"] = Path(d.metadata.get("source", "")).name

        documents.extend(docs)
        # takes the list of documents found for one file type (like all the PDFs)
        # and adds them to the master list (documents) before returning everything to be chunked

    return documents

# take files from 'data'
# process them into chunks
# store them in the vector database

