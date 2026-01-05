"""
Log Entry Domain Model

Represents a single log entry from security logs (CloudTrail, access logs, etc.)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class LogEntry:
    """Domain model for a security log entry."""

    id: str
    event_name: str
    event_time: str
    source: str
    raw_data: Dict[str, Any]

    user_identity: Optional[str] = None
    source_ip: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    error_message: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_text(self) -> str:
        """Convert to searchable text for embedding."""
        parts = [
            f"Event: {self.event_name}",
            f"Time: {self.event_time}",
            f"Source: {self.source}"
        ]

        if self.user_identity:
            parts.append(f"User: {self.user_identity}")
        if self.source_ip:
            parts.append(f"IP: {self.source_ip}")
        if self.resource:
            parts.append(f"Resource: {self.resource}")
        if self.action:
            parts.append(f"Action: {self.action}")
        if self.result:
            parts.append(f"Result: {self.result}")
        if self.error_message:
            parts.append(f"Error: {self.error_message}")

        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_name": self.event_name,
            "event_time": self.event_time,
            "source": self.source,
            "user_identity": self.user_identity,
            "source_ip": self.source_ip,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "error_message": self.error_message,
            "raw_data": self.raw_data,
            "metadata": self.metadata
        }
