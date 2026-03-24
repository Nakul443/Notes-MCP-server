# Notes MCP Server

MCP server for personal note search with retrieval + reranking, plus simple calculator tools.

## What This Project Does

This repository provides:

- **Semantic note search** via `search_my_notes`
  - ChromaDB vector retrieval (`k=10`) + FlashRank reranking
  - Optional file-level filtering by filename
  - Top 3 relevant chunks returned with score and source
- **Basic math tools**
  - `add_numbers(a, b)`
  - `subtract_numbers(a, b)`
- **Standalone weather tool module**
  - `src/services/weather_service.py` defines `get_alerts` and `get_forecast`
  - This module is not currently wired into `src/mcp_server.py`

## Repository Layout

```text
Notes-MCP-server/
├── src/
│   ├── mcp_server.py              # Main MCP server (search + math tools)
│   ├── seeder.py                  # Ingest data -> chunk -> embed -> store
│   └── services/
│       └── weather_service.py     # Separate weather MCP server/tools
├── tests/
│   ├── test_rag.py                # Retrieval/reranking behavior check
│   └── test_fixed_search.py       # Async search pipeline simulation
├── data/                          # Put .txt and .pdf files here
├── chroma_db/                     # Generated vector database (git-ignored)
├── requirements.txt
├── tools.json                     # Tool schema reference
├── run_tests.sh
├── Dockerfile
└── docker-compose.yml
```

## Requirements

- Python 3.11+ recommended
- `pip`
- Internet access for first-time model downloads (HuggingFace + FlashRank)

## Quick Start

1) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Add your notes to `data/` (`.txt` and/or `.pdf`).

4) Build the vector DB:

```bash
python3 src/seeder.py
```

5) Run the MCP server:

```bash
python3 src/mcp_server.py
```

The server uses MCP `stdio` transport.

## Search Pipeline

`src/seeder.py` performs:

1. Load docs from `data/` (currently `.txt`, `.pdf`)
2. Split with `RecursiveCharacterTextSplitter`
   - `chunk_size=1000`
   - `chunk_overlap=200`
3. Embed with `sentence-transformers/all-MiniLM-L6-v2`
4. Persist to `chroma_db/`

`src/mcp_server.py` search flow:

1. Similarity retrieval from Chroma (`k=10`)
2. Reranking with FlashRank model `ms-marco-MiniLM-L-12-v2`
3. Keep up to top 3 results with score threshold `>= 0.1`

## MCP Tools Exposed by Main Server

From `src/mcp_server.py`:

- `search_my_notes(query: str, filename: Optional[str] = None) -> str`
- `add_numbers(a: float, b: float) -> float`
- `subtract_numbers(a: float, b: float) -> float`

## Weather Tools

`src/services/weather_service.py` includes:

- `get_alerts(state: str)`
- `get_forecast(latitude: float, longitude: float)`

These call the National Weather Service API via `httpx`.

Important: these tools are not registered in the main server process in `src/mcp_server.py`; they are implemented in a separate FastMCP instance.

## MCP Client Configuration Example

Use this in your MCP client (example shape):

```json
{
  "mcpServers": {
    "notes-mcp-server": {
      "command": "python3",
      "args": ["/absolute/path/to/Notes-MCP-server/src/mcp_server.py"]
    }
  }
}
```

## Running Tests

Run both test scripts:

```bash
./run_tests.sh
```

Or run individually:

```bash
python3 tests/test_rag.py
python3 tests/test_fixed_search.py
```

## Docker

Build and start:

```bash
docker compose up --build
```

Notes:

- `docker-compose.yml` mounts `./data` and `./chroma_db` into the container
- `Dockerfile` starts `python3 src/mcp_server.py`
- Make sure `chroma_db/` has been seeded if you want immediate search results

## Common Issues

- **No results / weak results**
  - Re-run `python3 src/seeder.py`
  - Verify files exist in `data/`
  - Check query quality and optional filename filter value
- **Model load delays on first run**
  - Expected; embedding/reranker models are downloaded and cached
- **DB missing**
  - `chroma_db/` is created by `src/seeder.py`

## Development Notes

- Keep embedding model names aligned between seeder and server for consistent retrieval behavior.
- To support new file types, extend the `loaders` mapping in `src/seeder.py`.
- `tools.json` is a schema/reference artifact and may include tools not currently active in the main server runtime.

