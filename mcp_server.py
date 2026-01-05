import sys

# Combine all MCP tools into a single server
from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]

# Central MCP server
mcp = FastMCP("notes-mcp-server")

@mcp.tool()
async def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
async def subtract_numbers(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b

@mcp.tool()
async def findRelevantNotes(query: str) -> str:
    """Find relevant notes based on a query string."""
    # Placeholder implementation
    return f"Relevant notes for query: {query}"

def main():
    print("Notes MCP Server is running...", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()