# Notes MCP Server

A Model Context Protocol (MCP) server that provides tools for searching personal notes using vector embeddings, performing basic calculations, and accessing weather information.

## Overview

This project implements an MCP server that combines multiple tools:
- **Note Search**: Semantic search through your notes using ChromaDB and HuggingFace embeddings
- **Math Operations**: Basic arithmetic functions (add, subtract)
- **Weather Services**: Get weather alerts and forecasts via the National Weather Service API

## Project Structure

```
notes-mcp-server/
├── mcp_server.py          # Main MCP server with all tools
├── seeder.py              # Script to process and embed documents
├── tools.json             # Tool definitions (for external MCP clients)
├── data/                  # Directory containing your notes/documents
│   ├── note1.txt
│   └── note2.txt
├── chroma_db/             # ChromaDB vector database (generated)
└── weather/               # Weather service module
    ├── __init__.py
    └── weather_service.py
```

## Features

### 1. Note Search (`search_my_notes`)
- Searches through your notes using semantic similarity
- Returns the top 3 most relevant chunks with source information
- Uses HuggingFace embeddings (`all-MiniLM-L6-v2`) for vector search

### 2. Math Operations
- `add_numbers(a, b)`: Add two numbers
- `subtract_numbers(a, b)`: Subtract two numbers

### 3. Weather Services
- `get_alerts(state)`: Get active weather alerts for a US state
- `get_forecast(latitude, longitude)`: Get 5-day weather forecast for a location

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd notes-mcp-server
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install mcp fastmcp langchain-community langchain-huggingface chromadb httpx
   ```

   Or install individually:
   ```bash
   pip install mcp
   pip install fastmcp
   pip install langchain-community
   pip install langchain-huggingface
   pip install chromadb
   pip install httpx
   ```

## Usage

### Step 1: Add Your Notes

Place your text files (`.txt`) or PDF files (`.pdf`) in the `data/` directory:

```bash
# Example: Copy your notes
cp ~/my-notes/*.txt data/
cp ~/documents/*.pdf data/
```

### Step 2: Seed the Vector Database

Run the seeder script to process your documents:

```bash
python seeder.py
```

This script will:
1. Load all `.txt` and `.pdf` files from the `data/` directory
2. Split them into chunks (1000 characters with 200 character overlap)
3. Generate embeddings using HuggingFace's `all-MiniLM-L6-v2` model
4. Store them in ChromaDB at `chroma_db/`

**Note:** The seeder will delete and recreate the database each time it runs. To update your notes, simply add/modify files in `data/` and run the seeder again.

### Step 3: Start the MCP Server

Run the main server:

```bash
python mcp_server.py
```

The server runs using stdio transport, which is compatible with MCP clients like Cursor, Claude Desktop, etc.

## How It Works

### Document Processing Pipeline

1. **Loading** (`load_documents()`):
   - Scans the `data/` folder for `.txt` and `.pdf` files
   - Uses LangChain loaders to extract text
   - Attaches metadata (source file, etc.)

2. **Chunking** (`chunk_documents()`):
   - Splits documents into smaller chunks (1000 chars, 200 overlap)
   - Uses `RecursiveCharacterTextSplitter` with smart separators
   - Adds chunk IDs to metadata

3. **Embedding & Storage** (`embed_and_store()`):
   - Generates embeddings using HuggingFace's sentence transformer
   - Stores vectors in ChromaDB with persistence
   - Database is saved to `chroma_db/` directory

### Search Functionality

When you call `search_my_notes(query)`:
- The query is embedded using the same model
- ChromaDB performs similarity search
- Returns top 3 most relevant chunks with source information

## Configuration

### Changing Chunk Size

Edit `seeder.py` to modify chunking parameters:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Change this
    chunk_overlap=200,    # Change this
    separators=["\n\n", "\n", " ", ""],
)
```

### Changing Embedding Model

Edit the model name in both `seeder.py` and `mcp_server.py`:

```python
# In seeder.py (line 89)
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Change this
)

# In mcp_server.py (line 35)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Change this
```

**Important:** Use the same model in both files for consistent search results.

### Supported File Types

Currently supported:
- `.txt` files (via `TextLoader`)
- `.pdf` files (via `PyPDFLoader`)

To add more file types, modify `load_documents()` in `seeder.py`:

```python
loaders = {
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".md": MarkdownLoader,  # Add new types here
}
```

## MCP Client Configuration

### For Cursor/Claude Desktop

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "notes-mcp-server": {
      "command": "python",
      "args": ["/path/to/notes-mcp-server/mcp_server.py"]
    }
  }
}
```

### Using tools.json

The `tools.json` file provides tool definitions for external MCP clients. Note that the weather tools are defined here but not currently integrated into the main server. To use them, you would need to import the weather module in `mcp_server.py`.

## Troubleshooting

### Database Not Found Error

If you see errors about the database not existing:
1. Make sure you've run `seeder.py` first
2. Check that `chroma_db/` directory exists
3. Verify files exist in the `data/` directory

### Import Errors

If you get import errors:
- Ensure all dependencies are installed: `pip install -r requirements.txt` (if available)
- Activate your virtual environment
- Check Python version: `python --version` (should be 3.8+)

### No Search Results

If searches return no results:
- Verify documents were processed: check `chroma_db/` exists and has files
- Re-run `seeder.py` to rebuild the database
- Check that your query is relevant to the content in your notes

### Weather API Issues

Weather services use the National Weather Service API (no API key required):
- Ensure you have internet connectivity
- Check that state codes are valid (e.g., "CA", "NY", "TX")
- Verify coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)

## Development

### Adding New Tools

To add a new tool to the MCP server:

1. Open `mcp_server.py`
2. Add a new function with the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Description of what the tool does."""
    # Your implementation
    return result
```

3. The tool will automatically be available to MCP clients

### Testing

Test individual components:

```python
# Test seeder
python seeder.py

# Test server (will run until interrupted)
python mcp_server.py
```

## File Descriptions

- **`mcp_server.py`**: Main server file that defines all MCP tools and runs the server
- **`seeder.py`**: Processes documents from `data/` and creates the vector database
- **`tools.json`**: Tool schema definitions for external MCP clients
- **`weather/weather_service.py`**: Weather API integration (currently separate module)
- **`data/`**: Directory for your notes and documents
- **`chroma_db/`**: Generated vector database (do not edit manually)

## Notes

- The vector database (`chroma_db/`) is persistent and will be reused between runs
- Running `seeder.py` will delete and recreate the database
- The embedding model is downloaded automatically on first use
- Weather services require internet connectivity
- The server uses stdio transport for MCP communication

## License

This project appears to be for personal use. Modify as needed for your requirements.

## Contributing

Feel free to extend this project with:
- Additional file type support
- More sophisticated search features
- Additional tools and integrations
- Better error handling and logging

