# RAG System with A/B Testing and Feedback Loop

This project implements a Retrieval-Augmented Generation (RAG) system with A/B testing capabilities and a feedback loop. It uses FastAPI for the backend, Weaviate for vector storage, and integrates LLaMA models for text generation.

## Features

- RAG system for enhanced text generation
- A/B testing between different LLaMA model versions
- User feedback collection and analysis
- Weaviate integration for efficient similarity search
- SQLAlchemy for database management

## Prerequisites

- Python 3.8+
- PostgreSQL
- Weaviate instance

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

3. Set up environment variables:
   Create a `.env` file in the project root and add the following:
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

2. Access the API documentation at `http://localhost:8000/docs`

3. Use the `/query` endpoint to interact with the RAG system
4. Submit feedback using the `/feedback` endpoint
5. Search for prompts using the `/prompts/search` endpoint

## Analysis

Run the analysis script to get insights on model performance and user feedback:
```
python analyze_ab_testing.py
```

## Project Structure

- `main.py`: FastAPI application and main logic
- `database.py`: SQLAlchemy models and database setup
- `weaviate_client.py`: Weaviate client setup and schema initialization
- `analyze_ab_testing.py`: Script for analyzing A/B test results and feedback
- `requirements.txt`: List of Python dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
