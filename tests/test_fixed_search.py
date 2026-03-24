# simulates how the real MCP server behaves

import asyncio
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from flashrank import Ranker, RerankRequest

async def test_search():
    # 1. Initialize Paths - Adjusted for src/ structure
    BASE_DIR = Path(__file__).parent.parent.resolve()
    CHROMA_PATH = BASE_DIR / "chroma_db"
    
    print(f"🔍 Searching database at: {CHROMA_PATH}")
    
    # 1. Initialize Embeddings and DB
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=embeddings)

    query = "employment requirements"
    
    # Stage 1: Retrieval
    docs = db.similarity_search(query, k=10)
    
    if not docs:
        print("No relevant notes found for your query.")
        return

    print(f"Stage 1 found {len(docs)} documents.")

    # Stage 2: Reranking
    passages = [
        {"id": i, "text": d.page_content, "meta": d.metadata} 
        for i, d in enumerate(docs)
    ]
    
    ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/tmp/flashrank")
    rerank_request = RerankRequest(query=query, passages=passages)
    reranked_results = ranker.rerank(rerank_request)

    THRESHOLD = 0.1
    final_docs = [res for res in reranked_results[:3] if res['score'] >= THRESHOLD]
    
    if not final_docs:
        print("I found some notes, but none of them seem relevant enough to answer your question accurately.")
        return
    
    for d in final_docs:
        source = d['meta'].get('source_file', 'Unknown')
        score = round(d.get('score', 0), 3)
        print(f"--- Result (Relevance Score: {score}) ---")
        print(f"Source: {source}")
        print(f"Content: {d['text']}")

if __name__ == "__main__":
    asyncio.run(test_search())