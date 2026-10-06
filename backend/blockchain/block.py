"""
CyberShield AI - Blockchain Block

Defines the structure of a single block used to store
security events in the private blockchain.
"""

import hashlib
import json
from datetime import datetime, timezone


class Block:

    def __init__(
        self,
        index: int,
        event: dict,
        previous_hash: str = "0"
    ):
        self.index = index
        self.timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        self.event = event
        self.previous_hash = previous_hash

        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculate SHA-256 hash for the block.
        """

        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "event": self.event,
            "previous_hash": self.previous_hash
        }

        encoded_data = json.dumps(
            block_data,
            sort_keys=True
        ).encode()

        return hashlib.sha256(
            encoded_data
        ).hexdigest()

    def to_dict(self) -> dict:
        """
        Convert the block into a dictionary.
        """

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event": self.event,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }