# SecureQuery

**AI-Powered Security Log Analyzer using RAG**

Query your security logs in natural language using Retrieval-Augmented Generation.

## What Does This Do?

SecureQuery allows security teams to analyze logs by asking questions in plain English:
- "Show all failed login attempts in the last hour"
- "What IPs accessed the production database?"
- "Find unusual access patterns"

## Architecture

Built with Clean Architecture:
```
Domain Layer      → Log models, business logic
Application Layer → Use cases (ingest logs, query logs)
Infrastructure    → Vector DB (ChromaDB), LLM, Embeddings
API Layer         → Gradio chat interface
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key"

# Run
python app.py
```

## How It Works

1. **Upload Logs**: JSON, CloudTrail, or plain text
2. **Embedding**: Convert logs to vectors using sentence transformers
3. **Storage**: Store in ChromaDB vector database
4. **Query**: Ask questions in natural language
5. **Retrieval**: Find relevant log entries using semantic search
6. **Analysis**: LLM analyzes retrieved logs and answers question

## Tech Stack

- **Backend**: Python
- **UI**: Gradio
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers / OpenAI
- **LLM**: OpenAI GPT-4 / Google Gemini
- **Architecture**: Clean Architecture

## Use Cases

- **Security Incident Response**: Quick log analysis during incidents
- **Compliance Auditing**: Answer audit questions from logs
- **Threat Hunting**: Find suspicious patterns
- **Access Review**: Analyze who accessed what and when
