"""
Generic JSON Log Parser

Parses generic JSON log files into LogEntry domain objects.
"""

import json
import hashlib
from typing import List, Dict, Any
from ...domain.models.log_entry import LogEntry


class JSONParser:
    """Parse generic JSON logs."""

    def parse_file(self, file_path: str) -> List[LogEntry]:
        """Parse JSON log file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            return self.parse_records(data)
        elif isinstance(data, dict) and "logs" in data:
            return self.parse_records(data["logs"])
        else:
            return [self._parse_single_record(data)]

    def parse_records(self, records: List[Dict[str, Any]]) -> List[LogEntry]:
        """Parse list of log records."""
        log_entries = []

        for record in records:
            try:
                log_entry = self._parse_single_record(record)
                log_entries.append(log_entry)
            except Exception as e:
                print(f"Error parsing record: {e}")
                continue

        return log_entries

    def _parse_single_record(self, record: Dict[str, Any]) -> LogEntry:
        """Parse a single JSON record into LogEntry."""

        log_id = record.get("id", self._generate_id(record))
        event_name = record.get("event", record.get("action", "Unknown Event"))
        event_time = record.get("timestamp", record.get("time", ""))

        return LogEntry(
            id=log_id,
            event_name=event_name,
            event_time=event_time,
            source="json",
            user_identity=record.get("user"),
            source_ip=record.get("ip", record.get("source_ip")),
            resource=record.get("resource"),
            action=record.get("action", event_name),
            result=record.get("status", record.get("result")),
            error_message=record.get("error"),
            raw_data=record
        )

    def _generate_id(self, record: Dict[str, Any]) -> str:
        """Generate unique ID for log entry."""
        content = json.dumps(record, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
