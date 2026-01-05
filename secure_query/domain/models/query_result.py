"""
Query Result Domain Model

Represents the result of querying security logs with RAG.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from .log_entry import LogEntry


@dataclass
class QueryResult:
    """Result of a RAG query against security logs."""

    query: str
    answer: str
    relevant_logs: List[LogEntry] = field(default_factory=list)
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "answer": self.answer,
            "relevant_logs": [log.to_dict() for log in self.relevant_logs],
            "confidence": self.confidence,
            "sources": self.sources,
            "metadata": self.metadata
        }

    def to_markdown(self) -> str:
        """Format as markdown for display."""
        md = f"**Query:** {self.query}\n\n"
        md += f"**Answer:** {self.answer}\n\n"

        if self.relevant_logs:
            md += f"**Found {len(self.relevant_logs)} relevant log entries:**\n\n"
            for i, log in enumerate(self.relevant_logs[:5], 1):
                md += f"{i}. **{log.event_name}** at {log.event_time}\n"
                if log.user_identity:
                    md += f"   - User: {log.user_identity}\n"
                if log.source_ip:
                    md += f"   - IP: {log.source_ip}\n"
                if log.result:
                    md += f"   - Result: {log.result}\n"
                md += "\n"

        return md
