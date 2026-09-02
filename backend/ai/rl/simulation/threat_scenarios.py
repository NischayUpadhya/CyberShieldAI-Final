"""
CyberShield AI - Threat Scenario Library

Provides predefined and systematic cybersecurity scenarios
for RL simulation and testing.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ThreatScenario:
    name: str
    attack_type: int
    severity: Severity
    packet_rate: float
    byte_rate: float
    active_threats: int
    attack_frequency: float
    duration: int


# Attack type IDs used by the existing NetworkSimulator
ATTACK_TYPES = {
    "BENIGN": 0,
    "BOT": 1,
    "DDoS": 2,
    "DOS_GOLDENEYE": 3,
    "DOS_HULK": 4,
    "DOS_SLOWHTTPTEST": 5,
    "DOS_SLOWLORIS": 6,
    "FTP_PATATOR": 7,
    "HEARTBLEED": 8,
    "INFILTRATION": 9,
    "PORTSCAN": 10,
    "SSH_PATATOR": 11,
    "WEB_BRUTE_FORCE": 12,
    "WEB_SQL_INJECTION": 13,
    "WEB_XSS": 14,
}


class ThreatScenarioLibrary:

    def __init__(self):
        self.scenarios = self._create_scenarios()

    def _create_scenarios(self) -> List[ThreatScenario]:

        return [

            # -------------------------------------------------------------
            # BENIGN
            # -------------------------------------------------------------

            ThreatScenario(
                name="Benign Traffic",
                attack_type=0,
                severity=Severity.LOW,
                packet_rate=0.10,
                byte_rate=0.10,
                active_threats=0,
                attack_frequency=0.0,
                duration=30,
            ),

            # -------------------------------------------------------------
            # DDoS
            # -------------------------------------------------------------

            ThreatScenario(
                name="DDoS - High",
                attack_type=2,
                severity=Severity.HIGH,
                packet_rate=0.90,
                byte_rate=0.85,
                active_threats=8,
                attack_frequency=0.90,
                duration=60,
            ),

            ThreatScenario(
                name="DDoS - Critical",
                attack_type=2,
                severity=Severity.CRITICAL,
                packet_rate=1.00,
                byte_rate=0.95,
                active_threats=10,
                attack_frequency=1.00,
                duration=90,
            ),

            # -------------------------------------------------------------
            # DoS
            # -------------------------------------------------------------

            ThreatScenario(
                name="DoS - High",
                attack_type=4,
                severity=Severity.HIGH,
                packet_rate=0.80,
                byte_rate=0.75,
                active_threats=7,
                attack_frequency=0.85,
                duration=60,
            ),

            # -------------------------------------------------------------
            # Port Scan
            # -------------------------------------------------------------

            ThreatScenario(
                name="Port Scan - Medium",
                attack_type=10,
                severity=Severity.MEDIUM,
                packet_rate=0.50,
                byte_rate=0.30,
                active_threats=4,
                attack_frequency=0.60,
                duration=45,
            ),

            # -------------------------------------------------------------
            # Bot
            # -------------------------------------------------------------

            ThreatScenario(
                name="Bot Attack - High",
                attack_type=1,
                severity=Severity.HIGH,
                packet_rate=0.65,
                byte_rate=0.60,
                active_threats=6,
                attack_frequency=0.75,
                duration=60,
            ),

            # -------------------------------------------------------------
            # Brute Force
            # -------------------------------------------------------------

            ThreatScenario(
                name="Brute Force - High",
                attack_type=12,
                severity=Severity.HIGH,
                packet_rate=0.55,
                byte_rate=0.40,
                active_threats=5,
                attack_frequency=0.80,
                duration=60,
            ),

            # -------------------------------------------------------------
            # SQL Injection
            # -------------------------------------------------------------

            ThreatScenario(
                name="SQL Injection - Critical",
                attack_type=13,
                severity=Severity.CRITICAL,
                packet_rate=0.45,
                byte_rate=0.50,
                active_threats=6,
                attack_frequency=0.90,
                duration=60,
            ),

            # -------------------------------------------------------------
            # Infiltration
            # -------------------------------------------------------------

            ThreatScenario(
                name="Infiltration - Critical",
                attack_type=9,
                severity=Severity.CRITICAL,
                packet_rate=0.70,
                byte_rate=0.65,
                active_threats=8,
                attack_frequency=0.95,
                duration=90,
            ),

            # -------------------------------------------------------------
            # Heartbleed
            # -------------------------------------------------------------

            ThreatScenario(
                name="Heartbleed - Critical",
                attack_type=8,
                severity=Severity.CRITICAL,
                packet_rate=0.40,
                byte_rate=0.45,
                active_threats=5,
                attack_frequency=0.85,
                duration=60,
            ),
        ]

    def get_all(self) -> List[ThreatScenario]:
        return self.scenarios

    def get_by_name(self, name: str) -> ThreatScenario | None:

        for scenario in self.scenarios:

            if scenario.name.lower() == name.lower():
                return scenario

        return None

    def get_by_attack_type(self, attack_type: int) -> List[ThreatScenario]:

        return [
            scenario
            for scenario in self.scenarios
            if scenario.attack_type == attack_type
        ]

    def get_by_severity(
        self,
        severity: Severity
    ) -> List[ThreatScenario]:

        return [
            scenario
            for scenario in self.scenarios
            if scenario.severity == severity
        ]


if __name__ == "__main__":

    library = ThreatScenarioLibrary()

    print("=" * 60)
    print("CYBERSHIELD AI - THREAT SCENARIO LIBRARY")
    print("=" * 60)

    for scenario in library.get_all():

        print(
            f"{scenario.name:30} | "
            f"{scenario.severity.value:8} | "
            f"Attack ID: {scenario.attack_type}"
        )

    print("=" * 60)
    print(f"Total scenarios: {len(library.get_all())}")