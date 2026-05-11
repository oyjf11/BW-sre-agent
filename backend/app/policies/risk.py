"""Risk Policy for action risk assessment."""
from typing import Dict, Literal

from app.models.action import ActionSpec

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class RiskPolicy:

    HIGH_RISK_ACTIONS = {"delete", "terminate", "force-stop", "drop-table"}
    MEDIUM_RISK_ACTIONS = {"restart", "scale", "update-config", "rollback"}
    LOW_RISK_ACTIONS = {"read", "query", "list", "describe", "get"}

    CRITICAL_SERVICES = {"database", "redis", "kafka", "etcd"}
    HIGH_RISK_SERVICES = {"api-gateway", "auth-service", "payment-service"}

    def assess_risk(self, action: ActionSpec) -> RiskLevel:
        action_type = action.action_type.lower()
        service = action.service.lower()
        env = action.env.lower()

        if action_type in self.HIGH_RISK_ACTIONS:
            return "CRITICAL"
        if action_type in self.MEDIUM_RISK_ACTIONS:
            if service in self.CRITICAL_SERVICES:
                return "HIGH"
            return "MEDIUM"
        if action_type in self.LOW_RISK_ACTIONS:
            return "LOW"

        if service in self.CRITICAL_SERVICES:
            return "HIGH"
        if service in self.HIGH_RISK_SERVICES:
            return "MEDIUM"

        if env == "prod":
            return "HIGH"

        return "LOW"

    def requires_approval(self, action: ActionSpec) -> bool:
        risk = self.assess_risk(action)
        return risk in {"HIGH", "CRITICAL"}
