"""
CyberShield AI - Blockchain Service

Provides a simple interface for recording and
retrieving cybersecurity events from the blockchain.
"""

from .blockchain import Blockchain
from .event import SecurityEvent


class BlockchainService:

    def __init__(self):
        self.blockchain = Blockchain()

    def record_event(self, event: SecurityEvent):
        """Record a security event on the blockchain."""

        block = self.blockchain.add_security_event(event)

        return block.to_dict()

    def get_records(self):
        """Return all blockchain records."""

        return self.blockchain.get_chain()

    def verify_chain(self):
        """Verify blockchain integrity."""

        return self.blockchain.is_chain_valid()

    def get_status(self):
        """Return blockchain status."""

        return {
            "status": "Operational",
            "network": "CyberShield Private Chain",
            "consensus": "Single-Node Private Chain",
            "integrity": self.verify_chain()
        }