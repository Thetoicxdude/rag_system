# RAG System with A/B Testing and Feedback Loop

This project implements a Retrieval-Augmented Generation (RAG) system with A/B testing capabilities and a feedback loop. It uses FastAPI for the backend, Weaviate for vector search, and LLaMA models for text generation.

## Features

- RAG system with Weaviate for efficient information retrieval
- A/B testing between different LLaMA model versions
- User feedback collection and analysis
- FastAPI backend for quick and easy API development
- SQLAlchemy ORM for database interactions
- Pandas for data analysis

## Prerequisites

- Python 3.7+
- PostgreSQL
- Weaviate instance
- Access to LLaMA models

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rag-system-ab-testing.git
   cd rag-system-ab-testing
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   WEAVIATE_URL=http://localhost:8080
   LLAMA_MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
   ```

4. Initialize the database and Weaviate schema:
   ```
   python database.py
   python weaviate_client.py
   ```

## Usage

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

2. Use the following endpoints:
   - POST `/query`: Submit a query to the RAG system
   - GET `/prompts/search`: Search for existing prompts
   - POST `/feedback`: Submit feedback for a response

3. Analyze A/B testing results:
   ```
   python analyze_ab_testing.py
   ```

## API Examples

### Query the RAG System

```python
import requests

response = requests.post("http://localhost:8000/query", json={
    "prompt": "What are the benefits of RAG systems?"
})
print(response.json())
```

### Submit Feedback

```python
import requests

