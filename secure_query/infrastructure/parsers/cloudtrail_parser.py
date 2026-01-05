"""
CloudTrail Log Parser

Parses AWS CloudTrail JSON logs into LogEntry domain objects.
"""

import json
import hashlib
from typing import List, Dict, Any
from ...domain.models.log_entry import LogEntry


class CloudTrailParser:
    """Parse AWS CloudTrail logs."""

    def parse_file(self, file_path: str) -> List[LogEntry]:
        """Parse CloudTrail log file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        return self.parse_records(data.get("Records", []))

    def parse_records(self, records: List[Dict[str, Any]]) -> List[LogEntry]:
        """Parse list of CloudTrail records."""
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
        """Parse a single CloudTrail record into LogEntry."""

        event_id = record.get("eventID", self._generate_id(record))
        event_name = record.get("eventName", "Unknown")
        event_time = record.get("eventTime", "")

        user_identity = self._extract_user_identity(record)
        source_ip = record.get("sourceIPAddress")
        resource = self._extract_resource(record)
        result = self._extract_result(record)
        error_message = record.get("errorMessage")

        return LogEntry(
            id=event_id,
            event_name=event_name,
            event_time=event_time,
            source="cloudtrail",
            user_identity=user_identity,
            source_ip=source_ip,
            resource=resource,
            action=event_name,
            result=result,
            error_message=error_message,
            raw_data=record
        )

    def _extract_user_identity(self, record: Dict[str, Any]) -> str:
        """Extract user identity from record."""
        user_identity = record.get("userIdentity", {})

        if isinstance(user_identity, dict):
            user_name = user_identity.get("userName")
            user_type = user_identity.get("type")

            if user_name:
                return user_name
            elif user_type:
                return f"{user_type} user"

        return "Unknown"

    def _extract_resource(self, record: Dict[str, Any]) -> str:
        """Extract resource ARN or name."""
        resources = record.get("resources", [])

        if resources and isinstance(resources, list) and len(resources) > 0:
            first_resource = resources[0]
            if isinstance(first_resource, dict):
                return first_resource.get("ARN", "Unknown resource")

        request_params = record.get("requestParameters", {})
        if isinstance(request_params, dict):
            bucket = request_params.get("bucketName")
            table = request_params.get("tableName")
            if bucket:
                return f"s3://{bucket}"
            if table:
                return f"dynamodb:{table}"

        return "Unknown resource"

    def _extract_result(self, record: Dict[str, Any]) -> str:
        """Extract result (success/failure)."""
        response_elements = record.get("responseElements")
        error_code = record.get("errorCode")
        error_message = record.get("errorMessage")

        if error_code or error_message:
            return "Failure"
        elif response_elements:
            if isinstance(response_elements, dict):
                console_login = response_elements.get("ConsoleLogin")
                if console_login:
                    return console_login
            return "Success"
        else:
            return "Success"

    def _generate_id(self, record: Dict[str, Any]) -> str:
        """Generate unique ID for log entry."""
        content = json.dumps(record, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
