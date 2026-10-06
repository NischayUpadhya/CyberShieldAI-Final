"""
CyberShield AI - Blockchain Security Event

Defines the standard security event stored on the blockchain.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SecurityEvent:

    attack_type: str
    source_ip: str
    severity: str
    xgboost_confidence: float
    ppo_action: Optional[str] = None

    timestamp: str = ""

    def __post_init__(self):

        if not self.timestamp:
            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()

    def to_dict(self) -> dict:

        return {
            "attack_type": self.attack_type,
            "source_ip": self.source_ip,
            "severity": self.severity,
            "xgboost_confidence": self.xgboost_confidence,
            "ppo_action": self.ppo_action,
            "timestamp": self.timestamp
        }