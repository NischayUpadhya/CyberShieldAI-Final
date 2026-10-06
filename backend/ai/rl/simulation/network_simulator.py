"""
File        : network_simulator.py
Project     : CyberShield AI
Description : Simulates network traffic and cybersecurity threat scenarios
              for the reinforcement learning environment.

V5:
    - Balanced attack exposure for PPO training.
    - Every attack class is guaranteed to appear within each scenario cycle.
    - Benign traffic remains represented.
    - Severity levels are sampled across low, medium, high and critical.
    - Existing traffic, connection, frequency and confidence generation
      are preserved.
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
    """Represents one simulated network-security scenario."""

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

    V5 uses a balanced scenario schedule so PPO receives sufficient
    exposure to every attack class during training.

    All normalized values are represented in the range [0, 1].
    """

    # Number of benign scenarios in each complete cycle.
    #
    # One complete cycle contains:
    #   4 benign scenarios
    #   1 of each of the 14 attack classes
    #
    # Total = 18 scenarios.
    BENIGN_PER_CYCLE = 4

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:

        self.rng = np.random.default_rng(seed)

        # ---------------------------------------------------------------------
        # V5 balanced scenario schedule
        # ---------------------------------------------------------------------
        #
        # Every cycle contains every attack exactly once and benign traffic
        # four times.
        #
        # The schedule is shuffled before use so PPO does not learn a fixed
        # scenario ordering.
        # ---------------------------------------------------------------------

        self._scenario_schedule: list[int] = []

        self._scenario_index = 0

        self._reset_scenario_schedule()

    # =========================================================================
    # Scenario Schedule
    # =========================================================================

    def _reset_scenario_schedule(self) -> None:
        """
        Create and shuffle a new balanced scenario cycle.

        Each cycle contains:
            BENIGN x4
            Every attack class x1
        """

        schedule = (
            [0] * self.BENIGN_PER_CYCLE
            + list(range(1, len(ATTACK_NAMES)))
        )

        self.rng.shuffle(schedule)

        self._scenario_schedule = schedule

        self._scenario_index = 0

    def _select_attack_type(self) -> int:
        """
        Select the next attack type from the balanced schedule.

        This guarantees that every attack class appears at least once
        during every complete scenario cycle.
        """

        # Create a new shuffled cycle when the previous cycle is exhausted.
        if (
            self._scenario_index
            >= len(self._scenario_schedule)
        ):
            self._reset_scenario_schedule()

        attack_type = self._scenario_schedule[
            self._scenario_index
        ]

        self._scenario_index += 1

        return int(attack_type)

    # =========================================================================
    # Generate Scenario
    # =========================================================================

    def generate_scenario(
        self,
        attack_type: int | None = None,
    ) -> NetworkScenario:

        # ---------------------------------------------------------------------
        # Attack selection
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

            5: (0.40, 0.75),   # DoS Slowhttptest
            6: (0.35, 0.70),   # DoS slowloris

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

        # ---------------------------------------------------------------------
        # Benign traffic
        # ---------------------------------------------------------------------

        if attack_type == 0:

            return float(
                self.rng.uniform(
                    0.00,
                    0.15,
                )
            )

        # ---------------------------------------------------------------------
        # V5 severity distribution
        # ---------------------------------------------------------------------
        #
        # Every attack receives exposure to:
        #
        #   LOW       : 0.20 - 0.40
        #   MEDIUM    : 0.40 - 0.70
        #   HIGH      : 0.70 - 0.90
        #   CRITICAL  : 0.90 - 1.00
        #
        # This is independent of attack type, ensuring that every attack
        # class can be encountered at every severity level.
        # ---------------------------------------------------------------------

        severity_level = self.rng.choice(
            [
                "low",
                "medium",
                "high",
                "critical",
            ],
            p=[
                0.15,
                0.30,
                0.35,
                0.20,
            ],
        )

        if severity_level == "low":

            low, high = 0.20, 0.40

        elif severity_level == "medium":

            low, high = 0.40, 0.70

        elif severity_level == "high":

            low, high = 0.70, 0.90

        else:

            low, high = 0.90, 1.00

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
    print("=" * 80)
    print("CYBERSHIELD AI - V5 NETWORK SIMULATOR TEST")
    print("=" * 80)

    simulator = NetworkSimulator(seed=42)

    print("\nGenerated Network Scenarios:")

    for i in range(10):
        scenario = simulator.generate_scenario()

        print(f"\nScenario {i + 1}")
        print(f"Attack Type       : {scenario.attack_type}")
        print(f"Attack Name       : {scenario.attack_name}")
        print(f"Packet Rate       : {scenario.packet_rate:.3f}")
        print(f"Byte Rate         : {scenario.byte_rate:.3f}")
        print(f"Active Threats    : {scenario.active_threats}")
        print(f"Threat Severity   : {scenario.threat_severity:.3f}")
        print(f"Attack Frequency  : {scenario.attack_frequency:.3f}")
        print(f"XGBoost Confidence: {scenario.xgboost_confidence:.3f}")

    # ------------------------------------------------------------------
    # Test 1: All attack classes
    # ------------------------------------------------------------------
    print("\nTesting all attack classes...")

    for attack_type in range(len(ATTACK_NAMES)):
        scenario = simulator.generate_scenario(
            attack_type=attack_type
        )

        assert scenario.attack_type == attack_type, (
            f"Expected attack type {attack_type}, "
            f"got {scenario.attack_type}"
        )

    print("Attack class validation: PASSED")

    # ------------------------------------------------------------------
    # Test 2: Balanced scenario cycle
    # ------------------------------------------------------------------
    print("\nTesting balanced scenario cycle...")

    # Start from a fresh cycle.
    simulator._reset_scenario_schedule()

    cycle_size = (
        NetworkSimulator.BENIGN_PER_CYCLE
        + (len(ATTACK_NAMES) - 1)
    )

    generated_types = []

    for _ in range(cycle_size):
        scenario = simulator.generate_scenario()
        generated_types.append(scenario.attack_type)

    # Every attack type must appear exactly once.
    for attack_type in range(1, len(ATTACK_NAMES)):
        assert generated_types.count(attack_type) == 1, (
            f"Attack type {attack_type} "
            f"did not appear exactly once "
            f"in the balanced cycle."
        )

    # Benign traffic must appear BENIGN_PER_CYCLE times.
    assert (
        generated_types.count(0)
        == NetworkSimulator.BENIGN_PER_CYCLE
    ), (
        "Incorrect number of benign scenarios "
        "in the balanced cycle."
    )

    print("Balanced exposure validation: PASSED")

    # ------------------------------------------------------------------
    # Test 3: Severity coverage
    # ------------------------------------------------------------------
    print("\nTesting severity coverage...")

    simulator._reset_scenario_schedule()

    severity_bands = {
        "low": False,
        "medium": False,
        "high": False,
        "critical": False,
    }

    for _ in range(200):
        scenario = simulator.generate_scenario()

        if scenario.attack_type == 0:
            continue

        severity = scenario.threat_severity

        if severity < 0.40:
            severity_bands["low"] = True
        elif severity < 0.70:
            severity_bands["medium"] = True
        elif severity < 0.90:
            severity_bands["high"] = True
        else:
            severity_bands["critical"] = True

        if all(severity_bands.values()):
            break

    for band, found in severity_bands.items():
        assert found, (
            f"Severity band '{band}' "
            f"was not generated."
        )

    print("Severity coverage validation: PASSED")

    print("\n" + "=" * 80)
    print("V5 NETWORK SIMULATOR TEST: PASSED")
    print("=" * 80)


if __name__ == "__main__":
    test_network_simulator()