# purpose of this file is to test the retrieval and reranking accuracy of the RAG system implemented in mcp_server.py
# 2 stages
# stage 1: standard vector search using Chroma and HuggingFaceEmbeddings
# stage 2: reranking using FlashRank to ensure the most relevant results are returned

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from flashrank import Ranker, RerankRequest
import time

def test_retrieval_accuracy(query):
    print(f"\n TESTING QUERY: '{query}'")
    print("="*50)

    # 1. Setup
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    
    # 2. Measure Standard Retrieval (Stage 1)
    start_time = time.time()
    initial_docs = db.similarity_search_with_relevance_scores(query, k=5)
    retrieval_time = time.time() - start_time
    
    print(f" Stage 1 (Vector Search) found {len(initial_docs)} candidates in {retrieval_time:.4f}s")
    for i, (doc, score) in enumerate(initial_docs):
        print(f"   [{i+1}] Score: {score:.4f} | Source: {doc.metadata.get('source_file')} | Text: {doc.page_content[:60]}...")

    # 3. Measure Reranking (Stage 2)
    passages = [{"id": i, "text": d.page_content, "meta": d.metadata} for i, (d, s) in enumerate(initial_docs)]
    ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
    rerank_request = RerankRequest(query=query, passages=passages)
    
    start_time = time.time()
    reranked_results = ranker.rerank(rerank_request)
    rerank_time = time.time() - start_time

    print(f"\n Stage 2 (FlashRank Reranking) completed in {rerank_time:.4f}s")
    for i, res in enumerate(reranked_results[:3]):
        print(f"    Top {i+1}: Score: {res['score']:.4f} | Source: {res['meta'].get('source_file')} | Text: {res['text'][:60]}...")

if __name__ == "__main__":
    # Change this query to something that exists in your notes!
    test_query = "What are the project deadlines?" 
    test_retrieval_accuracy(test_query)