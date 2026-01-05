"""
Gradio Chat Interface for SecureQuery

AI-powered security log analysis using RAG (Retrieval-Augmented Generation)
"""

import os
from dotenv import load_dotenv
import gradio as gr

# Load environment variables from .env file
load_dotenv()
from secure_query.infrastructure.vector_stores.chromadb_store import ChromaDBStore
from secure_query.infrastructure.embeddings.openai_embeddings import EmbeddingService
from secure_query.application.use_cases.ingest_logs import IngestLogsUseCase
from secure_query.application.use_cases.query_logs import QueryLogsUseCase


# Global state
vector_store = None
embedding_service = None
ingest_use_case = None
query_use_case = None
uploaded_file_path = None


def initialize_services(api_key: str = None):
    """Initialize RAG services."""
    global vector_store, embedding_service, ingest_use_case, query_use_case

    # Initialize vector store (ChromaDB)
    vector_store = ChromaDBStore(persist_directory="./chroma_db")

    # Initialize embedding service - use env vars only, not UI api_key
    # (UI api_key is for LLM, not embeddings)
    embedding_service = EmbeddingService.create_auto(api_key=None)

    # Initialize use cases
    ingest_use_case = IngestLogsUseCase(vector_store, embedding_service)

    # Initialize query use case with LLM (requires API key)
    # Try Gemini first (free tier), then OpenAI
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    openai_key = api_key or os.getenv("OPENAI_API_KEY")

    if gemini_key:
        try:
            query_use_case = QueryLogsUseCase(
                vector_store,
                embedding_service,
                llm_provider="gemini",
                api_key=gemini_key
            )
            return
        except Exception as e:
            print(f"Gemini initialization failed: {e}")

    if openai_key:
        try:
            query_use_case = QueryLogsUseCase(
                vector_store,
                embedding_service,
                llm_provider="openai",
                api_key=openai_key
            )
            return
        except Exception as e:
            print(f"OpenAI initialization failed: {e}")

    # No LLM available - user can still ingest but not query
    query_use_case = None


def upload_logs(file, log_type, api_key):
    """Handle log file upload and ingestion."""
    global uploaded_file_path

    if not file:
        return "Please select a file to upload.", 0

    try:
        # Initialize services if needed
        if ingest_use_case is None:
            initialize_services(api_key)

        # Ingest logs
        log_type_map = {"CloudTrail": "cloudtrail", "Generic JSON": "json"}
        count = ingest_use_case.execute(file, log_type_map[log_type])

        uploaded_file_path = file

        return f"✅ Successfully ingested {count} log entries!", count

    except Exception as e:
        return f"❌ Error ingesting logs: {str(e)}", 0


def query_logs(message, history, api_key):
    """Process user query against uploaded logs."""
    global query_use_case

    if not uploaded_file_path:
        history.append((message, "⚠️ Please upload a log file first."))
        return history

    if not message.strip():
        return history

    try:
        # Initialize services if needed
        if query_use_case is None:
            initialize_services(api_key)

        # Check if LLM is available after initialization
        if query_use_case is None:
            api_key_warning = (
                "⚠️ **API Key Required for Querying**\n\n"
                "Please provide a Gemini or OpenAI API key to ask questions.\n\n"
                "**Get a FREE Gemini API key:**\n"
                "1. Go to https://makersuite.google.com/app/apikey\n"
                "2. Create a new API key\n"
                "3. Paste it in the 'API Key' field above\n\n"
                "Note: Sentence-transformers (free) is only for embeddings. "
                "The LLM needs an API key to generate answers."
            )
            history.append((message, api_key_warning))
            return history

        # Query logs using RAG
        result = query_use_case.execute(message, n_results=5)

        # Format response
        response = result.to_markdown()

        history.append((message, response))
        return history

    except Exception as e:
        history.append((message, f"❌ Error: {str(e)}"))
        return history


def clear_chat():
    """Clear chat history."""
    return []


# Gradio interface
with gr.Blocks(title="SecureQuery - AI Log Analyzer") as demo:
    gr.Markdown("""
    # SecureQuery
    ## AI-Powered Security Log Analyzer using RAG

    Upload security logs (CloudTrail, access logs) and ask questions in natural language.
    """)

    with gr.Row():
        # Left panel: File upload
        with gr.Column(scale=1):
            gr.Markdown("### 1. Upload Logs")

            file_input = gr.File(
                label="Select Log File",
                file_types=[".json"],
                type="filepath"
            )

            log_type = gr.Radio(
                choices=["CloudTrail", "Generic JSON"],
                value="CloudTrail",
                label="Log Type"
            )

            api_key_input = gr.Textbox(
                label="LLM API Key (Optional - uses .env if empty)",
                placeholder="Leave empty to use keys from .env file",
                type="password"
            )

            upload_btn = gr.Button("Upload & Ingest", variant="primary")

            upload_status = gr.Textbox(
                label="Status",
                interactive=False
            )

            log_count = gr.Number(
                label="Logs Ingested",
                value=0,
                interactive=False
            )

            gr.Markdown("""
            ### Example Questions:
            - "Show all failed login attempts"
            - "What users accessed the system?"
            - "Find suspicious IP addresses"
            - "Show console login failures"
            """)

        # Right panel: Chat
        with gr.Column(scale=2):
            gr.Markdown("### 2. Ask Questions")

            chatbot = gr.Chatbot(
                height=500,
                label="Chat with your logs"
            )

            with gr.Row():
                msg = gr.Textbox(
                    label="Your question",
                    placeholder="Example: Show all failed login attempts",
                    scale=4
                )
                submit_btn = gr.Button("Send", scale=1, variant="primary")

            clear_btn = gr.Button("Clear Chat")

    # Event handlers
    upload_btn.click(
        fn=upload_logs,
        inputs=[file_input, log_type, api_key_input],
        outputs=[upload_status, log_count]
    )

    msg.submit(
        fn=query_logs,
        inputs=[msg, chatbot, api_key_input],
        outputs=chatbot
    ).then(
        fn=lambda: "",
        outputs=msg
    )

    submit_btn.click(
        fn=query_logs,
        inputs=[msg, chatbot, api_key_input],
        outputs=chatbot
    ).then(
        fn=lambda: "",
        outputs=msg
    )

    clear_btn.click(
        fn=clear_chat,
        outputs=chatbot
    )

    gr.Markdown("""
    ---
    ### How It Works

    **RAG (Retrieval-Augmented Generation):**
    1. **Ingest**: Parse logs → Generate embeddings → Store in vector DB (ChromaDB)
    2. **Query**: Embed question → Find similar logs → Send to LLM → Get answer

    **Tech Stack:**
    - **Embeddings**: Sentence Transformers (free, local) or OpenAI
    - **Vector DB**: ChromaDB (local, persistent)
    - **LLM**: Google Gemini (free tier) or OpenAI GPT-4

    **Cost**: $0 with sentence-transformers + Gemini free tier!
    """)


if __name__ == "__main__":
    demo.launch()
