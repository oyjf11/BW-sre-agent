"""IntakeService: normalize and convert different input modes into IncidentTicket."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.incident import IncidentTicket
from app.normalizers.env import normalize_env
from app.normalizers.service_alias import normalize_service
from app.normalizers.time_range import normalize_time_range
from app.tools import ToolRequest, gateway

logger = logging.getLogger(__name__)


class IntakeService:
    def __init__(self, db: Session):
        self.db = db

    def from_ticket_payload(self, payload: Dict[str, Any]) -> IncidentTicket:
        payload["env"] = normalize_env(payload["env"])
        payload["service"] = normalize_service(payload["service"])
        payload["time_range"] = normalize_time_range(payload.get("time_range"))
        return IncidentTicket(**payload)

    def from_ticket_id(self, ticket_id: str) -> IncidentTicket:
        import asyncio
        req = ToolRequest(tool_name="query_ticket_by_id", params={"ticket_id": ticket_id}, run_id=f"intake-{ticket_id}")
        try:
            result = asyncio.get_event_loop().run_until_complete(gateway.call_tool(req))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(gateway.call_tool(req))
            loop.close()

        if result.success and result.result:
            data = result.result
            return IncidentTicket(
                ticket_id=ticket_id,
                title=data.get("title", f"Ticket {ticket_id}"),
                description=data.get("description", ""),
                service=normalize_service(data.get("service", "unknown")),
                env=normalize_env(data.get("env", "prod")),
                severity=data.get("severity", "P3"),
                source=data.get("source", "ticket_lookup"),
                time_range=normalize_time_range(data.get("time_range")),
                metadata=data.get("metadata"),
            )
        else:
            raise ValueError(
                f"Failed to look up ticket {ticket_id}: {result.error}. "
                f"Real mode requires a working ticket_id adapter."
            )

    def from_alert_event(self, alert: Dict[str, Any]) -> IncidentTicket:
        ticket_id = f"alert-{uuid.uuid4().hex[:8]}"
        env = normalize_env(alert.get("env", "prod"))
        service = normalize_service(alert.get("service", "unknown"))
        severity = alert.get("severity", "P3")
        alert_name = alert.get("alert_name", "Unknown Alert")
        description = alert.get("description", "")
        labels = alert.get("labels", {})

        full_description = f"Alert: {alert_name}"
        if description:
            full_description += f"\n{description}"
        if labels:
            full_description += f"\nLabels: {labels}"

        return IncidentTicket(
            ticket_id=ticket_id,
            title=f"[Alert] {alert_name}",
            description=full_description,
            service=service,
            env=env,
            severity=severity,
            source="alert_event",
            time_range=normalize_time_range(None),
            metadata={"alert_labels": labels, "started_at": alert.get("started_at")},
        )
