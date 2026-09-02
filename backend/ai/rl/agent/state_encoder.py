"""
File        : state_encoder.py
Project     : CyberShield AI
Description : Converts cybersecurity information into a normalized
              numerical state vector for the reinforcement learning agent.
"""

from __future__ import annotations

import numpy as np


class CyberDefenseStateEncoder:
    """
    Encodes the current cybersecurity environment state into
    a fixed-size numerical vector.

    State:
        0 - Attack type
        1 - XGBoost confidence
        2 - Threat severity
        3 - Packet rate
        4 - Byte rate
        5 - Active threats
        6 - Previous action
        7 - Available resources
    """

    STATE_SIZE = 8

    def __init__(self) -> None:
        self.attack_type_max = 14.0
        self.packet_rate_max = 100000.0
        self.byte_rate_max = 100000000.0
        self.active_threats_max = 100.0
        self.action_max = 4.0
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
        Convert raw cybersecurity state information into
        a normalized NumPy state vector.

        Returns:
            np.ndarray with shape (8,)
        """

        state = np.array(
            [
                self._normalize(
                    attack_type,
                    0.0,
                    self.attack_type_max,
                ),
                self._clip(xgboost_confidence, 0.0, 1.0),
                self._clip(threat_severity, 0.0, 1.0),
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
                    previous_action,
                    0.0,
                    self.action_max,
                ),
                self._normalize(
                    available_resources,
                    0.0,
                    self.resources_max,
                ),
            ],
            dtype=np.float32,
        )

        return state

    @staticmethod
    def _clip(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Clip a value to the specified range."""

        return float(np.clip(value, minimum, maximum))

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

        value = float(np.clip(value, minimum, maximum))

        return (value - minimum) / (maximum - minimum)


def main() -> None:
    """Run a basic state encoder test."""

    encoder = CyberDefenseStateEncoder()

    state = encoder.encode(
        attack_type=10,
        xgboost_confidence=0.97,
        threat_severity=0.85,
        packet_rate=5000,
        byte_rate=5000000,
        active_threats=5,
        previous_action=2,
        available_resources=75,
    )

    print("=" * 70)
    print("CYBERSHIELD AI - STATE ENCODER TEST")
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

    if state.shape == (CyberDefenseStateEncoder.STATE_SIZE,):
        print("\nState encoder test: PASSED")
    else:
        print("\nState encoder test: FAILED")

    print("=" * 70)


if __name__ == "__main__":
    main()