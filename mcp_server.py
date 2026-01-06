import sys

# Combine all MCP tools into a single server
from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Central MCP server
mcp = FastMCP("notes-mcp-server")

@mcp.tool()
async def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
async def subtract_numbers(a: float, b: float) -> float:
    """Subtract two numbers.""" # this comment is read by gemini and then it uses the relevant function
    return a - b

@mcp.tool()
async def search_my_notes(query: str) -> str:
    """Search through my notes and return relevant information.
    Use this tool whenever user prefixes the query with 'search my notes'.
    Args :
        query (str): The search query.
    Returns:
        str: The search results.
    
    Example: 
        user input: "search my notes about project deadlines"
        function call: search_my_notes("project deadlines")
        returns: "Source: notes.txt
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

    # Retrieve the top 3 most relevant chunks
    docs = db.similarity_search(query, k=3)
    
    results = [f"Source: {d.metadata.get('source')}\nContent: {d.page_content}" for d in docs]
    return "\n---\n".join(results)


def main():
    print("Notes MCP Server is running...", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
