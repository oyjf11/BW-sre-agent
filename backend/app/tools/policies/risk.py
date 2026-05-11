from typing import Dict, Any, Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskPolicy:
    ACTION_RISK_MAP: Dict[str, RiskLevel] = {
        "restart": RiskLevel.LOW,
        "scale_up": RiskLevel.LOW,
        "scale_down": RiskLevel.MEDIUM,
        "rollback": RiskLevel.HIGH,
        "deploy": RiskLevel.HIGH,
        "delete": RiskLevel.CRITICAL,
        "update_config": RiskLevel.MEDIUM,
        "execute_script": RiskLevel.HIGH,
    }

    SEVERITY_RISK_MAP: Dict[str, RiskLevel] = {
        "P1": RiskLevel.CRITICAL,
        "P2": RiskLevel.HIGH,
        "P3": RiskLevel.MEDIUM,
        "P4": RiskLevel.LOW,
    }

    @classmethod
    def get_action_risk(cls, action_type: str) -> RiskLevel:
        return cls.ACTION_RISK_MAP.get(action_type, RiskLevel.MEDIUM)

    @classmethod
    def get_severity_risk(cls, severity: str) -> RiskLevel:
        return cls.SEVERITY_RISK_MAP.get(severity, RiskLevel.MEDIUM)

    @classmethod
    def requires_approval(cls, risk_level: RiskLevel) -> bool:
        return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    @classmethod
    def assess_risk(
        cls,
        action_type: str,
        severity: str,
        service: str,
        env: str,
    ) -> Dict[str, Any]:
        action_risk = cls.get_action_risk(action_type)
        severity_risk = cls.get_severity_risk(severity)
        
        risk_scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }
        
        combined_score = risk_scores[action_risk] + risk_scores[severity_risk]
        
        if combined_score >= 6 or action_risk == RiskLevel.CRITICAL:
            final_risk = RiskLevel.CRITICAL
        elif combined_score >= 4:
            final_risk = RiskLevel.HIGH
        elif combined_score >= 2:
            final_risk = RiskLevel.MEDIUM
        else:
            final_risk = RiskLevel.LOW

        return {
            "risk_level": final_risk.value,
            "action_risk": action_risk.value,
            "severity_risk": severity_risk.value,
            "requires_approval": cls.requires_approval(final_risk),
            "score": combined_score,
        }
