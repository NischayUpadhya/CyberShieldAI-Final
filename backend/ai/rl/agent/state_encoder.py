"""
File        : state_encoder.py
Project     : CyberShield AI
Description : Converts cybersecurity information into a normalized
              numerical state vector for the reinforcement learning agent.

V5:
    - Attack type is one-hot encoded.
    - Previous action is one-hot encoded.
    - Continuous features are normalized to [0, 1].
"""

from __future__ import annotations

import numpy as np


class CyberDefenseStateEncoder:
    """
    Encodes the current cybersecurity environment state.

    State layout:

        0 - 13   : Attack type (14 one-hot features)
        14       : XGBoost confidence
        15       : Threat severity
        16       : Packet rate
        17       : Byte rate
        18       : Active threats
        19 - 23  : Previous action (5 one-hot features)
        24       : Available resources

    Total state size = 26
    """

    NUM_ATTACK_TYPES = 15
    NUM_ACTIONS = 5

    # 15 attack types:
    # 0 = Benign
    # 1 = Bot
    # 2 = DDoS
    # ...
    # 14 = Web Attack - XSS

    STATE_SIZE = (
        NUM_ATTACK_TYPES
        + 1                       # XGBoost confidence
        + 1                       # Threat severity
        + 1                       # Packet rate
        + 1                       # Byte rate
        + 1                       # Active threats
        + NUM_ACTIONS             # Previous action
        + 1                       # Available resources
    )

    def __init__(self) -> None:
        self.packet_rate_max = 100000.0
        self.byte_rate_max = 100000000.0
        self.active_threats_max = 100.0
        self.resources_max = 100.0

    def encode(
        self,
        attack_type: int,
        xgboost_confidence: float,
        threat_severity: float,
        packet_rate: float,
        byte_rate: float,
        active_threats: int,
        previous_action: int,
        available_resources: float,
    ) -> np.ndarray:
        """
        Convert raw cybersecurity information into a normalized
        state vector.

        Returns:
            np.ndarray with shape (25,)
        """

        # ---------------------------------------------------------
        # Attack type: one-hot encoding
        # ---------------------------------------------------------
        attack_vector = np.zeros(
            self.NUM_ATTACK_TYPES,
            dtype=np.float32,
        )

        attack_type = int(
            np.clip(
                attack_type,
                0,
                self.NUM_ATTACK_TYPES - 1,
            )
        )

        attack_vector[attack_type] = 1.0

        # ---------------------------------------------------------
        # Previous action: one-hot encoding
        # ---------------------------------------------------------
        action_vector = np.zeros(
            self.NUM_ACTIONS,
            dtype=np.float32,
        )

        previous_action = int(
            np.clip(
                previous_action,
                0,
                self.NUM_ACTIONS - 1,
            )
        )

        action_vector[previous_action] = 1.0

        # ---------------------------------------------------------
        # Continuous state features
        # ---------------------------------------------------------
        continuous_features = np.array(
            [
                self._clip(
                    xgboost_confidence,
                    0.0,
                    1.0,
                ),
                self._clip(
                    threat_severity,
                    0.0,
                    1.0,
                ),
                self._normalize(
                    packet_rate,
                    0.0,
                    self.packet_rate_max,
                ),
                self._normalize(
                    byte_rate,
                    0.0,
                    self.byte_rate_max,
                ),
                self._normalize(
                    active_threats,
                    0.0,
                    self.active_threats_max,
                ),
                self._normalize(
                    available_resources,
                    0.0,
                    self.resources_max,
                ),
            ],
            dtype=np.float32,
        )

        # ---------------------------------------------------------
        # Final state
        # ---------------------------------------------------------
        state = np.concatenate(
            [
                attack_vector,
                continuous_features[:5],
                action_vector,
                continuous_features[5:],
            ]
        ).astype(np.float32)

        return state

    @staticmethod
    def _clip(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Clip a value to the specified range."""

        return float(
            np.clip(
                value,
                minimum,
                maximum,
            )
        )

    @staticmethod
    def _normalize(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Normalize a value to the range [0, 1]."""

        if maximum <= minimum:
            raise ValueError(
                "Maximum value must be greater than minimum value."
            )

        value = float(
            np.clip(
                value,
                minimum,
                maximum,
            )
        )

        return (
            (value - minimum)
            / (maximum - minimum)
        )


def main() -> None:
    """Run a basic V5 state encoder test."""

    encoder = CyberDefenseStateEncoder()

    state = encoder.encode(
        attack_type=2,             # DDoS
        xgboost_confidence=0.97,
        threat_severity=0.85,
        packet_rate=5000,
        byte_rate=5000000,
        active_threats=5,
        previous_action=2,         # RATE_LIMIT
        available_resources=75,
    )

    print("=" * 70)
    print("CYBERSHIELD AI - V5 STATE ENCODER TEST")
    print("=" * 70)

    print("\nEncoded State:")
    print(state)

    print("\nState Shape:")
    print(state.shape)

    print("\nData Type:")
    print(state.dtype)

    print("\nMinimum Value:")
    print(state.min())

    print("\nMaximum Value:")
    print(state.max())

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    attack_sum = state[:encoder.NUM_ATTACK_TYPES].sum()

    action_start = (
        encoder.NUM_ATTACK_TYPES + 5
    )

    action_end = (
        action_start + encoder.NUM_ACTIONS
    )

    action_sum = state[
        action_start:action_end
    ].sum()

    valid_shape = (
        state.shape
        == (CyberDefenseStateEncoder.STATE_SIZE,)
    )

    valid_attack_encoding = (
        attack_sum == 1.0
    )

    valid_action_encoding = (
        action_sum == 1.0
    )

    if (
        valid_shape
        and valid_attack_encoding
        and valid_action_encoding
    ):
        print("\nV5 state encoder test: PASSED")
    else:
        print("\nV5 state encoder test: FAILED")

        print(
            f"Expected shape: "
            f"({CyberDefenseStateEncoder.STATE_SIZE},)"
        )

        print(
            f"Actual shape: {state.shape}"
        )

        print(
            f"Attack one-hot sum: {attack_sum}"
        )

        print(
            f"Action one-hot sum: {action_sum}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()