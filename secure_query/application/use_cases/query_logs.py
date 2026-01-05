"""
Query Logs Use Case

Implements RAG (Retrieval-Augmented Generation) for querying security logs.
"""

import os
from typing import Optional
from ...domain.models.query_result import QueryResult
from ...domain.models.log_entry import LogEntry
from ...infrastructure.embeddings.openai_embeddings import EmbeddingService
from ...infrastructure.vector_stores.chromadb_store import ChromaDBStore

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class QueryLogsUseCase:
    """Use case for querying security logs using RAG."""

    def __init__(
        self,
        vector_store: ChromaDBStore,
        embedding_service: EmbeddingService,
        llm_provider: str = "gemini",
        api_key: Optional[str] = None
    ):
        """
        Initialize use case.

        Args:
            vector_store: ChromaDB vector store
            embedding_service: Embedding service for query
            llm_provider: "openai" or "gemini"
            api_key: API key for LLM
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_provider = llm_provider

        if llm_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not installed")
            self.llm_client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o-mini"

        elif llm_provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("Google Generative AI not installed")
            genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
            self.llm_client = genai.GenerativeModel("gemini-2.5-flash")

    def execute(self, query: str, n_results: int = 5) -> QueryResult:
        """
        Query security logs using RAG.

        Steps:
        1. Embed the user's question
        2. Retrieve relevant log entries from vector DB
        3. Pass logs + question to LLM
        4. Return answer

        Args:
            query: User's natural language question
            n_results: Number of relevant logs to retrieve

        Returns:
            QueryResult with answer and relevant logs
        """
        # Step 1: Embed the query
        query_embedding = self.embedding_service.embed_text(query)

        # Step 2: Retrieve relevant logs
        matches = self.vector_store.query(query_embedding, n_results)

        if not matches:
            return QueryResult(
                query=query,
                answer="No relevant log entries found. Please upload logs first.",
                relevant_logs=[],
                confidence=0.0
            )

        # Step 3: Build context from retrieved logs
        context = self._build_context(matches)

        # Step 4: Generate answer with LLM
        answer = self._generate_answer(query, context)

        # Step 5: Convert matches to LogEntry objects
        relevant_logs = self._matches_to_log_entries(matches)

        return QueryResult(
            query=query,
            answer=answer,
            relevant_logs=relevant_logs,
            confidence=1.0 - (matches[0].get('distance', 0) if matches else 1.0),
            sources=[match['id'] for match in matches],
            metadata={"n_results": len(matches)}
        )

    def _build_context(self, matches) -> str:
        """Build context string from retrieved log entries."""
        context_parts = []

        for i, match in enumerate(matches, 1):
            doc = match['document']
            metadata = match.get('metadata', {})

            context_parts.append(f"Log Entry {i}:")
            context_parts.append(doc)

            if metadata:
                context_parts.append(f"Metadata: {metadata}")

            context_parts.append("")  # Blank line

        return "\n".join(context_parts)

    def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using LLM."""
        prompt = f"""You are a security analyst assistant. Answer the user's question based on the provided security log entries.

Log Entries:
{context}

User Question: {query}

Provide a clear, concise answer based on the log entries above. If the logs don't contain enough information to answer, say so."""

        if self.llm_provider == "openai":
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content

        elif self.llm_provider == "gemini":
            response = self.llm_client.generate_content(prompt)
            return response.text

    def _matches_to_log_entries(self, matches) -> list[LogEntry]:
        """Convert vector store matches to LogEntry objects."""
        log_entries = []

        for match in matches:
            metadata = match.get('metadata', {})

            log_entry = LogEntry(
                id=match['id'],
                event_name=metadata.get('event_name', 'Unknown'),
                event_time=metadata.get('event_time', ''),
                source=metadata.get('source', 'unknown'),
                user_identity=metadata.get('user_identity'),
                source_ip=metadata.get('source_ip'),
                result=metadata.get('result'),
                raw_data={"document": match['document']}
            )
            log_entries.append(log_entry)

        return log_entries
