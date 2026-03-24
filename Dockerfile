# Use a slim Python image to keep the size down
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (needed for some vector DB components)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your structured project
COPY src/ ./src/
COPY data/ ./data/

# We copy the DB so the container is "ready to search"
COPY chroma_db/ ./chroma_db/

# Set the PYTHONPATH so imports inside /src work correctly
ENV PYTHONPATH=/app/src

# Default command to run your MCP server
CMD ["python3", "src/mcp_server.py"]