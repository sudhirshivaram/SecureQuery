"""
Ingest Logs Use Case

Parses log files, generates embeddings, and stores in vector database.
"""

from typing import List
from ...domain.models.log_entry import LogEntry
from ...infrastructure.parsers.cloudtrail_parser import CloudTrailParser
from ...infrastructure.parsers.json_parser import JSONParser
from ...infrastructure.embeddings.openai_embeddings import EmbeddingService
from ...infrastructure.vector_stores.chromadb_store import ChromaDBStore


class IngestLogsUseCase:
    """Use case for ingesting security logs into the RAG system."""

    def __init__(
        self,
        vector_store: ChromaDBStore,
        embedding_service: EmbeddingService
    ):
        """
        Initialize use case with dependencies.

        This is Dependency Injection - we inject the services we need.
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.cloudtrail_parser = CloudTrailParser()
        self.json_parser = JSONParser()

    def execute(self, file_path: str, log_type: str = "cloudtrail") -> int:
        """
        Ingest log file into the RAG system.

        Args:
            file_path: Path to log file
            log_type: "cloudtrail" or "json"

        Returns:
            Number of logs ingested
        """
        # Step 1: Parse logs
        if log_type == "cloudtrail":
            logs = self.cloudtrail_parser.parse_file(file_path)
        elif log_type == "json":
            logs = self.json_parser.parse_file(file_path)
        else:
            raise ValueError(f"Unknown log type: {log_type}")

        if not logs:
            return 0

        # Step 2: Convert logs to text for embedding
        log_texts = [log.to_text() for log in logs]

        # Step 3: Generate embeddings
        embeddings = self.embedding_service.embed_texts(log_texts)

        # Step 4: Store in vector database
        self.vector_store.add_logs(logs, embeddings)

        return len(logs)

    def clear_database(self):
        """Clear all logs from the vector store."""
        self.vector_store.clear()

    def get_log_count(self) -> int:
        """Get number of logs in the database."""
        return self.vector_store.count()
