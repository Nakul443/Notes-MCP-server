import sys
from typing import Optional
from pathlib import Path

# MCP and LangChain Imports
from mcp.server.fastmcp import FastMCP
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# New Import for Reranking
from flashrank import Ranker, RerankRequest

# Central MCP server
mcp = FastMCP("notes-mcp-server")

# --- PATH ADJUSTMENT FOR SRC/ STRUCTURE ---
# Since this file is in 'src/', we go up one level to reach the root
BASE_DIR = Path(__file__).parent.parent.resolve()
CHROMA_PATH = BASE_DIR / "chroma_db"

# --- GLOBAL INITIALIZATION (Load once on startup) ---
# This ensures fast responses when Gemini calls the tool
print("Loading models and database...", file=sys.stderr)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize DB once
# str(CHROMA_PATH) ensures compatibility with Chroma's interface
db = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=embeddings)

# Initialize Ranker once
# Using a specific cache_dir is good for WSL stability
ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/tmp/flashrank")

@mcp.tool()
async def search_my_notes(query: str, filename: Optional[str] = None) -> str:
    """
    Search through my notes and return the most accurate relevant information.
    
    Args:
        query (str): The search query or question.
        filename (str, optional): If provided, search will be restricted to this specific file name.
    """
    
    # 2. Setup Metadata Filter (if filename is provided)
    search_filter = None
    if filename:
        # We use the 'source_file' key created in seeder.py
        search_filter = {"source_file": filename}

    # Stage 1: Retrieval (Fetch top 10 candidates)
    # Since 'db' is global, this call is now much faster
    docs = db.similarity_search(query, k=10, filter=search_filter)
    
    if not docs:
        return "No relevant notes found for your query."

    # Stage 2: Reranking (Cross-Encoding for High Precision)
    passages = [
        {"id": i, "text": d.page_content, "meta": d.metadata} 
        for i, d in enumerate(docs)
    ]
    
    rerank_request = RerankRequest(query=query, passages=passages)
    # Using the global ranker
    reranked_results = ranker.rerank(rerank_request)

    # take the top 3 results, but ONLY if they are actually relevant
    THRESHOLD = 0.1  # If score is below 0.1, it's probably junk
    final_docs = [res for res in reranked_results[:3] if res['score'] >= THRESHOLD]
    
    if not final_docs:
        return "I found some notes, but none of them seem relevant enough to answer your question accurately."
    
    formatted_results = []
    for d in final_docs:
        source = d['meta'].get('source_file', 'Unknown')
        score = round(d.get('score', 0), 3) # Reliability score
        formatted_results.append(
            f"--- Result (Relevance Score: {score}) ---\n"
            f"Source: {source}\n"
            f"Content: {d['text']}"
        )
    
    return "\n\n".join(formatted_results)

# Basic math tools remain the same
@mcp.tool()
async def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
async def subtract_numbers(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b

def main():
    print(f"Server root: {BASE_DIR}", file=sys.stderr)
    print("Notes MCP Server with Reranking is running...", file=sys.stderr)
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()