"""
CyberShield AI - Blockchain API Routes

Provides API endpoints for:
- Recording security events
- Retrieving blockchain records
- Verifying blockchain integrity
- Checking blockchain status
"""

from fastapi import APIRouter

from app.models.blockchain import BlockchainEventRequest
from blockchain.event import SecurityEvent
from blockchain.service import BlockchainService


router = APIRouter(
    prefix="/api/blockchain",
    tags=["Blockchain"]
)

blockchain_service = BlockchainService()


@router.post("/record")
def record_event(event: BlockchainEventRequest):
    """Record a security event on the blockchain."""

    security_event = SecurityEvent(
        attack_type=event.attack_type,
        source_ip=event.source_ip,
        severity=event.severity,
        xgboost_confidence=event.xgboost_confidence,
        ppo_action=event.ppo_action
    )

    return blockchain_service.record_event(security_event)


@router.get("/records")
def get_records():
    """Return all blockchain records."""

    return blockchain_service.get_records()


@router.get("/verify")
def verify_blockchain():
    """Verify blockchain integrity."""

    return {
        "valid": blockchain_service.verify_chain()
    }


@router.get("/status")
def blockchain_status():
    """Return blockchain network status."""

    return blockchain_service.get_status()