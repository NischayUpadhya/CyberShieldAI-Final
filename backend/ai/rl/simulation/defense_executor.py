"""
File        : defense_executor.py
Project     : CyberShield AI
Description : Executes and records defensive actions selected by PPO.
"""

from dataclasses import dataclass
from typing import Optional
from ai.rl.simulation.firewall_simulator import (
    FirewallSimulator,
    FirewallResult,
    ACTION_NAMES,
)

@dataclass
class DefenseExecutionResult:
    action: int
    action_name: str

    successful: bool

    threat_reduction: float
    traffic_reduction: float

    legitimate_traffic_impact: float
    resource_cost: float

    response_effectiveness: float

    message: str


class DefenseExecutor:

    def __init__(self) -> None:
        self.firewall = FirewallSimulator()

    def execute(
        self,
        action: int,
        threat_severity: float,
        packet_rate: float,
        byte_rate: float,
        is_benign: bool,
    ) -> DefenseExecutionResult:

        if action not in ACTION_NAMES:
            raise ValueError(
                f"Invalid defense action: {action}"
            )

        result: FirewallResult = self.firewall.execute(
            action=action,
            threat_severity=threat_severity,
            packet_rate=packet_rate,
            byte_rate=byte_rate,
            is_benign=is_benign,
        )

        if result.successful:
            message = (
                f"{result.action_name} executed successfully"
            )
        else:
            message = (
                f"{result.action_name} executed with limited effectiveness"
            )

        return DefenseExecutionResult(
            action=result.action,
            action_name=result.action_name,

            successful=result.successful,

            threat_reduction=result.threat_reduction,
            traffic_reduction=result.traffic_reduction,

            legitimate_traffic_impact=(
                result.legitimate_traffic_impact
            ),

            resource_cost=result.resource_cost,

            response_effectiveness=(
                result.response_effectiveness
            ),

            message=message,
        )


def test_defense_executor():

    print()
    print("=" * 80)
    print("CYBERSHIELD AI - DEFENSE EXECUTOR TEST")
    print("=" * 80)

    executor = DefenseExecutor()

    print("\nATTACK SCENARIO")

    for action in range(5):

        result = executor.execute(
            action=action,
            threat_severity=0.90,
            packet_rate=0.90,
            byte_rate=0.85,
            is_benign=False,
        )

        print()
        print(f"Action            : {result.action_name}")
        print(f"Threat Reduction  : {result.threat_reduction:.3f}")
        print(f"Traffic Reduction : {result.traffic_reduction:.3f}")
        print(
            f"Effectiveness     : "
            f"{result.response_effectiveness:.3f}"
        )
        print(f"Resource Cost     : {result.resource_cost:.3f}")
        print(f"Successful        : {result.successful}")
        print(f"Message           : {result.message}")

    print("\nBENIGN SCENARIO")

    for action in range(5):

        result = executor.execute(
            action=action,
            threat_severity=0.10,
            packet_rate=0.15,
            byte_rate=0.10,
            is_benign=True,
        )

        print()
        print(f"Action                    : {result.action_name}")
        print(
            f"Legitimate Traffic Impact: "
            f"{result.legitimate_traffic_impact:.3f}"
        )
        print(f"Resource Cost              : {result.resource_cost:.3f}")
        print(f"Successful                 : {result.successful}")

    print()
    print("=" * 80)
    print("DEFENSE EXECUTOR TEST: PASSED")
    print("=" * 80)


if __name__ == "__main__":
    test_defense_executor()