"""
ChromaDB Vector Store

Stores log embeddings and performs similarity search for RAG.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from ...domain.models.log_entry import LogEntry


class ChromaDBStore:
    """Vector store using ChromaDB for log embeddings."""

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "security_logs"):
        """
        Initialize ChromaDB client.

        Args:
            persist_directory: Where to store the database
            collection_name: Name of the collection (like a table)
        """
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Security log embeddings"}
        )

    def add_logs(self, logs: List[LogEntry], embeddings: List[List[float]]):
        """
        Add log entries with their embeddings to the vector store.

        Args:
            logs: List of LogEntry objects
            embeddings: List of embedding vectors (one per log)
        """
        if len(logs) != len(embeddings):
            raise ValueError("Number of logs must match number of embeddings")

        ids = [log.id for log in logs]
        documents = [log.to_text() for log in logs]

        metadatas = []
        for log in logs:
            metadata = {
                "event_name": log.event_name,
                "event_time": log.event_time,
                "source": log.source,
            }
            if log.user_identity:
                metadata["user_identity"] = log.user_identity
            if log.source_ip:
                metadata["source_ip"] = log.source_ip
            if log.result:
                metadata["result"] = log.result

            metadatas.append(metadata)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar log entries.

        Args:
            query_embedding: Embedding vector of the user's question
            n_results: Number of similar logs to return

        Returns:
            List of matching log entries with metadata
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        matches = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                match = {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                }
                matches.append(match)

        return matches

    def clear(self):
        """Clear all logs from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Security log embeddings"}
        )

    def count(self) -> int:
        """Get number of logs in the store."""
        return self.collection.count()
