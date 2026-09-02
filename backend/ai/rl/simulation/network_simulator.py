"""
File        : network_simulator.py
Project     : CyberShield AI
Description : Simulates network traffic and cybersecurity threat scenarios
              for the reinforcement learning environment.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# =============================================================================
# Threat Definitions
# =============================================================================

ATTACK_NAMES = {
    0: "BENIGN",
    1: "Bot",
    2: "DDoS",
    3: "DoS GoldenEye",
    4: "DoS Hulk",
    5: "DoS Slowhttptest",
    6: "DoS slowloris",
    7: "FTP-Patator",
    8: "Heartbleed",
    9: "Infiltration",
    10: "PortScan",
    11: "SSH-Patator",
    12: "Web Attack - Brute Force",
    13: "Web Attack - SQL Injection",
    14: "Web Attack - XSS",
}


# =============================================================================
# Network Scenario
# =============================================================================

@dataclass
class NetworkScenario:

    attack_type: int
    attack_name: str

    packet_rate: float
    byte_rate: float

    active_connections: float
    active_threats: int

    threat_severity: float
    attack_frequency: float

    xgboost_confidence: float


# =============================================================================
# Network Simulator
# =============================================================================

class NetworkSimulator:
    """
    Generates simulated cybersecurity network scenarios.

    All normalized values are represented in the range [0, 1].
    """

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:

        self.rng = np.random.default_rng(seed)

    # =========================================================================
    # Generate Scenario
    # =========================================================================

    def generate_scenario(
        self,
        attack_type: int | None = None,
    ) -> NetworkScenario:

        # ---------------------------------------------------------------------
        # Random attack selection
        # ---------------------------------------------------------------------

        if attack_type is None:

            attack_type = self._select_attack_type()

        if attack_type not in ATTACK_NAMES:

            raise ValueError(
                f"Invalid attack type: {attack_type}"
            )

        attack_name = ATTACK_NAMES[attack_type]

        # ---------------------------------------------------------------------
        # Generate traffic characteristics
        # ---------------------------------------------------------------------

        packet_rate = self._generate_packet_rate(
            attack_type
        )

        byte_rate = self._generate_byte_rate(
            attack_type
        )

        active_connections = self._generate_connections(
            attack_type
        )

        active_threats = self._generate_active_threats(
            attack_type
        )

        threat_severity = self._generate_severity(
            attack_type
        )

        attack_frequency = self._generate_frequency(
            attack_type
        )

        xgboost_confidence = self._generate_confidence(
            attack_type
        )

        return NetworkScenario(
            attack_type=attack_type,
            attack_name=attack_name,
            packet_rate=packet_rate,
            byte_rate=byte_rate,
            active_connections=active_connections,
            active_threats=active_threats,
            threat_severity=threat_severity,
            attack_frequency=attack_frequency,
            xgboost_confidence=xgboost_confidence,
        )

    # =========================================================================
    # Attack Selection
    # =========================================================================

    def _select_attack_type(self) -> int:

        # ---------------------------------------------------------------------
        # Approximate distribution inspired by the CICIDS2017 class imbalance.
        #
        # These probabilities are for simulation only.
        # They are NOT training labels from the dataset.
        # ---------------------------------------------------------------------

        attack_types = np.arange(
            len(ATTACK_NAMES)
        )

        probabilities = np.array(
            [
                0.70,   # BENIGN
                0.02,   # Bot
                0.08,   # DDoS
                0.02,   # DoS GoldenEye
                0.05,   # DoS Hulk
                0.01,   # DoS Slowhttptest
                0.01,   # DoS slowloris
                0.01,   # FTP-Patator
                0.005,  # Heartbleed
                0.005,  # Infiltration
                0.05,   # PortScan
                0.01,   # SSH-Patator
                0.01,   # Web Brute Force
                0.005,  # SQL Injection
                0.01,   # XSS
            ],
            dtype=np.float64,
        )

        probabilities /= probabilities.sum()

        return int(
            self.rng.choice(
                attack_types,
                p=probabilities,
            )
        )

    # =========================================================================
    # Packet Rate
    # =========================================================================

    def _generate_packet_rate(
        self,
        attack_type: int,
    ) -> float:

        ranges = {

            0: (0.05, 0.30),   # BENIGN

            1: (0.30, 0.75),   # Bot
            2: (0.75, 1.00),   # DDoS

            3: (0.55, 0.90),   # DoS GoldenEye
            4: (0.70, 1.00),   # DoS Hulk

            5: (0.40, 0.75),   # Slowhttptest
            6: (0.35, 0.70),   # slowloris

            7: (0.20, 0.55),   # FTP Patator
            8: (0.05, 0.20),   # Heartbleed

            9: (0.20, 0.60),   # Infiltration
            10: (0.45, 0.85),  # PortScan

            11: (0.20, 0.55),  # SSH Patator

            12: (0.20, 0.50),  # Web Brute Force
            13: (0.15, 0.45),  # SQL Injection
            14: (0.15, 0.45),  # XSS
        }

        low, high = ranges[attack_type]

        return float(
            self.rng.uniform(
                low,
                high,
            )
        )

    # =========================================================================
    # Byte Rate
    # =========================================================================

    def _generate_byte_rate(
        self,
        attack_type: int,
    ) -> float:

        ranges = {

            0: (0.05, 0.30),

            1: (0.25, 0.70),
            2: (0.75, 1.00),

            3: (0.50, 0.85),
            4: (0.70, 1.00),

            5: (0.30, 0.65),
            6: (0.25, 0.60),

            7: (0.15, 0.50),
            8: (0.05, 0.20),

            9: (0.20, 0.55),
            10: (0.30, 0.75),

            11: (0.15, 0.50),

            12: (0.15, 0.45),
            13: (0.10, 0.40),
            14: (0.10, 0.40),
        }

        low, high = ranges[attack_type]

        return float(
            self.rng.uniform(
                low,
                high,
            )
        )

    # =========================================================================
    # Connections
    # =========================================================================

    def _generate_connections(
        self,
        attack_type: int,
    ) -> float:

        if attack_type == 0:

            return float(
                self.rng.uniform(
                    0.05,
                    0.30,
                )
            )

        if attack_type in (2, 3, 4):

            return float(
                self.rng.uniform(
                    0.60,
                    1.00,
                )
            )

        if attack_type == 10:

            return float(
                self.rng.uniform(
                    0.50,
                    0.90,
                )
            )

        return float(
            self.rng.uniform(
                0.15,
                0.70,
            )
        )

    # =========================================================================
    # Active Threats
    # =========================================================================

    def _generate_active_threats(
        self,
        attack_type: int,
    ) -> int:

        if attack_type == 0:

            return int(
                self.rng.integers(
                    0,
                    2,
                )
            )

        return int(
            self.rng.integers(
                1,
                10,
            )
        )

    # =========================================================================
    # Threat Severity
    # =========================================================================

    def _generate_severity(
        self,
        attack_type: int,
    ) -> float:

        severity_ranges = {

            0: (0.00, 0.15),

            1: (0.30, 0.75),
            2: (0.70, 1.00),

            3: (0.55, 0.90),
            4: (0.70, 1.00),

            5: (0.35, 0.70),
            6: (0.35, 0.70),

            7: (0.30, 0.65),
            8: (0.60, 0.95),

            9: (0.65, 1.00),
            10: (0.40, 0.80),

            11: (0.30, 0.65),

            12: (0.35, 0.70),
            13: (0.50, 0.85),
            14: (0.35, 0.70),
        }

        low, high = severity_ranges[
            attack_type
        ]

        return float(
            self.rng.uniform(
                low,
                high,
            )
        )

    # =========================================================================
    # Attack Frequency
    # =========================================================================

    def _generate_frequency(
        self,
        attack_type: int,
    ) -> float:

        if attack_type == 0:

            return float(
                self.rng.uniform(
                    0.00,
                    0.15,
                )
            )

        return float(
            self.rng.uniform(
                0.20,
                1.00,
            )
        )

    # =========================================================================
    # XGBoost Confidence Simulation
    # =========================================================================

    def _generate_confidence(
        self,
        attack_type: int,
    ) -> float:

        if attack_type == 0:

            return float(
                self.rng.uniform(
                    0.85,
                    0.99,
                )
            )

        return float(
            self.rng.uniform(
                0.80,
                0.99,
            )
        )


# =============================================================================
# Simulator Test
# =============================================================================

def test_network_simulator():

    print()
    print("=" * 80)
    print("CYBERSHIELD AI - NETWORK SIMULATOR TEST")
    print("=" * 80)

    simulator = NetworkSimulator(
        seed=42
    )

    # -------------------------------------------------------------------------
    # Generate random scenarios
    # -------------------------------------------------------------------------

    print(
        "\nGenerated Network Scenarios:"
    )

    for index in range(10):

        scenario = (
            simulator.generate_scenario()
        )

        print()
        print(
            f"Scenario {index + 1}"
        )

        print(
            f"Attack Type       : "
            f"{scenario.attack_type}"
        )

        print(
            f"Attack Name       : "
            f"{scenario.attack_name}"
        )

        print(
            f"Packet Rate       : "
            f"{scenario.packet_rate:.3f}"
        )

        print(
            f"Byte Rate         : "
            f"{scenario.byte_rate:.3f}"
        )

        print(
            f"Connections       : "
            f"{scenario.active_connections:.3f}"
        )

        print(
            f"Active Threats    : "
            f"{scenario.active_threats}"
        )

        print(
            f"Threat Severity   : "
            f"{scenario.threat_severity:.3f}"
        )

        print(
            f"Attack Frequency  : "
            f"{scenario.attack_frequency:.3f}"
        )

        print(
            f"XGBoost Confidence: "
            f"{scenario.xgboost_confidence:.3f}"
        )

    # -------------------------------------------------------------------------
    # Test every attack class
    # -------------------------------------------------------------------------

    print()
    print(
        "Testing all attack classes..."
    )

    for attack_type in ATTACK_NAMES:

        scenario = (
            simulator.generate_scenario(
                attack_type=attack_type
            )
        )

        assert (
            scenario.attack_type
            == attack_type
        )

        assert (
            scenario.attack_name
            == ATTACK_NAMES[attack_type]
        )

        assert 0.0 <= scenario.packet_rate <= 1.0
        assert 0.0 <= scenario.byte_rate <= 1.0
        assert 0.0 <= scenario.active_connections <= 1.0
        assert 0.0 <= scenario.threat_severity <= 1.0
        assert 0.0 <= scenario.attack_frequency <= 1.0
        assert 0.0 <= scenario.xgboost_confidence <= 1.0

    print(
        "Attack class validation: PASSED"
    )

    print()
    print("=" * 80)
    print(
        "NETWORK SIMULATOR TEST: PASSED"
    )
    print("=" * 80)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    test_network_simulator()