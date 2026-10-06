"""
CyberShield AI - Blockchain API Models

Defines the request structure for blockchain security events.
"""

from typing import Optional

from pydantic import BaseModel, Field


class BlockchainEventRequest(BaseModel):

    attack_type: str
    source_ip: str
    severity: str

    xgboost_confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    ppo_action: Optional[str] = None