
"""
CyberShield AI - Private Blockchain

Manages blockchain operations:
- Genesis block creation
- Security event recording
- Chain validation
- Persistent storage
"""

import json
from pathlib import Path

from .block import Block
from .event import SecurityEvent


class Blockchain:

    def __init__(self, storage_path=None):
        self.storage_path = Path(
            storage_path
            if storage_path
            else Path(__file__).resolve().parent
            / "data"
            / "blockchain.json"
        )

        self.chain = []
        self._load_chain()

    def _load_chain(self):
        """Load the blockchain from persistent storage."""

        if not self.storage_path.exists():
            self.create_genesis_block()
            self._save_chain()
            return

        try:
            with open(
                self.storage_path, "r", encoding="utf-8"
            ) as file:
                stored_chain = json.load(file)

            self.chain = [
                self._block_from_dict(block_data)
                for block_data in stored_chain
            ]

            if not self.chain or not self.is_chain_valid():
                raise ValueError("Stored blockchain is invalid.")

        except (json.JSONDecodeError, OSError, ValueError, KeyError) as error:
            raise RuntimeError(
                f"Blockchain integrity check failed: {error}"
            ) from error

    def _block_from_dict(self, block_data):
        """Reconstruct a Block object from stored data."""

        block = Block(
            index=block_data["index"],
            event=block_data["event"],
            previous_hash=block_data["previous_hash"],
        )

        # Preserve the original stored values.
        block.timestamp = block_data["timestamp"]
        block.hash = block_data["hash"]

        return block

    def _save_chain(self):
        """Persist the complete blockchain to JSON."""

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.storage_path, "w", encoding="utf-8"
        ) as file:
            json.dump(
                [block.to_dict() for block in self.chain],
                file,
                indent=4,
            )

    def create_genesis_block(self):
        """Create the first block in the blockchain."""

        genesis_event = {
            "event": "Genesis Block",
            "description": "CyberShield AI Blockchain Initialized",
        }

        genesis_block = Block(
            index=0,
            event=genesis_event,
            previous_hash="0",
        )

        self.chain.append(genesis_block)

    def get_latest_block(self):
        """Return the latest block in the chain."""

        return self.chain[-1]

    def add_security_event(self, event: SecurityEvent):
        """Add a SecurityEvent to the blockchain."""

        if not isinstance(event, SecurityEvent):
            raise TypeError("event must be a SecurityEvent object")

        # Refresh persisted state before appending a new event.
        if self.storage_path.exists():
            self._load_chain()

        latest_block = self.get_latest_block()

        new_block = Block(
            index=len(self.chain),
            event=event.to_dict(),
            previous_hash=latest_block.hash,
        )

        self.chain.append(new_block)
        self._save_chain()

        return new_block

    def is_chain_valid(self) -> bool:
        """Verify the integrity of the entire blockchain."""

        if not self.chain:
            return False

        # Validate genesis block structure.
        genesis = self.chain[0]

        if genesis.index != 0:
            return False

        if genesis.previous_hash != "0":
            return False

        if genesis.hash != genesis.calculate_hash():
            return False

        # Validate remaining blocks.
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.index != i:
                return False

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_chain(self) -> list:
        """Return the latest persisted blockchain."""

        if self.storage_path.exists():
            self._load_chain()

        return [
            block.to_dict()
            for block in self.chain
        ]
