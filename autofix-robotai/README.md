# AutoFix-RobotAI

AutoFix-RobotAI is an AI-powered developer assistant that analyzes Robot Framework test logs, identifies the root cause of failed test cases, and automatically generates fixes for the repository.

## Features

- **Failure Analysis:** Parses Robot Framework `output.xml` to identify failures and extract details.
- **Repository Indexing:** Uses `sentence-transformers` and ChromaDB to index locators, keywords, and robot files.
- **Locator Validation:** Recommends alternative locators if one is broken.
- **Auto Fix Generation:** Generates Git patches for broken test cases.
- **AI Agents Orchestration:** Uses `CrewAI` to coordinate log analysis, repo understanding, and fix generation.
- **Local AI Models:** Integrates with local Ollama (`deepseek-coder`, `llama3`).

## Architecture Stack

- Python 3.11+
- CrewAI (Multi-Agent Framework)
- ChromaDB (Vector DB)
- sentence-transformers (Embeddings)
- Ollama (Local LLM Inference)
- Robot Framework & Appium

## Setup & Execution

### Using Docker (Recommended)

1. Start the environment:
   ```bash
   cd docker
   docker compose up -d
   ```

2. Inside the container, you can run the CLI:
   ```bash
   docker exec -it autofix_app bash
   python -m cli.main --help
   ```

3. Ensure you pull the required LLM model via Ollama:
   ```bash
   docker exec autofix_ollama ollama pull deepseek-coder
   ```

### Running Locally without Docker

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure you have Ollama installed and running locally.
3. Run the CLI:
   ```bash
   python -m cli.main --help
   ```

## CLI Usage

### 1. Indexing the repository
```bash
python -m cli.main repo-index --path /path/to/repo
```

### 2. Analyzing a log output
```bash
python -m cli.main analyze --output output.xml
```

### 3. Automatically generate a fix
```bash
python -m cli.main fix --log output.xml --test-name "Login Test"
```

## Folder Structure

- `agents/`: CrewAI Agent definitions
- `cli/`: CLI Application entrypoint
- `llm/`: LLM interface wrapper
- `parsers/`: Robot Log parsing utilities
- `repo_indexer/`: AST and file scanning with ChromaDB indexing
- `docker/`: Docker container definitions
