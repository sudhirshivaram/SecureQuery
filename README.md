---
title: SecureQuery - AI Log Analyzer
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.0.0"
app_file: app.py
pinned: false
---

# SecureQuery

**AI-Powered Security Log Analyzer using RAG (Retrieval-Augmented Generation)**

Query your security logs in natural language using vector search and LLMs.

## 🚀 What Does This Do?

SecureQuery allows security teams to analyze logs by asking questions in plain English:
- "Show all failed login attempts in the last hour"
- "What IPs accessed the production database?"
- "Find unusual access patterns"
- "Which users modified S3 buckets?"

## 🛠️ Tech Stack

- **Backend**: Python 3.9+
- **UI**: Gradio
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers (local, free) / OpenAI
- **LLM**: Google Gemini (free tier) / OpenAI GPT-4
- **Architecture**: Clean Architecture

## 📝 How to Use This Demo

1. **Upload Logs**:
   - Select log type: CloudTrail or Generic JSON
   - Upload your log file
   - Click "Upload & Ingest"

2. **Ask Questions**:
   - Type your question in natural language
   - Get AI-powered answers with source citations

3. **API Key** (Required for querying):
   - **Gemini** (Recommended): Free at https://makersuite.google.com/app/apikey
   - **OpenAI**: GPT-4 key from https://platform.openai.com
   - Add as Space secret or enter in UI

## 🏗️ Architecture

Built with Clean Architecture:
```
Domain Layer      → Log models, business logic
Application Layer → Use cases (ingest logs, query logs)
Infrastructure    → Vector DB (ChromaDB), LLM, Embeddings
API Layer         → Gradio chat interface
```

## 🔍 How It Works

1. **Upload Logs**: JSON, CloudTrail, or generic logs
2. **Embedding**: Convert logs to vectors using sentence transformers
3. **Storage**: Store in ChromaDB vector database
4. **Query**: Ask questions in natural language
5. **Retrieval**: Find relevant log entries using semantic search
6. **Analysis**: LLM analyzes retrieved logs and answers question

## 📊 Use Cases

- **Security Incident Response**: Quick log analysis during incidents
- **Compliance Auditing**: Answer audit questions from logs
- **Threat Hunting**: Find suspicious patterns
- **Access Review**: Analyze who accessed what and when
- **CloudTrail Analysis**: Query AWS API calls and changes

## 🔗 Links

- **GitHub**: https://github.com/sudhirshivaram/SecureQuery
- **Portfolio**: https://github.com/sudhirshivaram

## 💡 Example Queries

- "Show me all authentication failures"
- "What are the most common errors?"
- "List API calls from IP 192.168.1.100"
- "Which users made changes today?"
- "Find all DeleteBucket operations"

---

Built with Clean Architecture to demonstrate AI-powered security operations.
