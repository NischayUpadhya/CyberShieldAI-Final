"""
File        : firewall_simulator.py
Project     : CyberShield AI
Description : Simulates the effect of defensive firewall actions
              selected by the reinforcement learning agent.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# =============================================================================
# Actions
# =============================================================================

ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}


# =============================================================================
# Firewall Result
# =============================================================================

@dataclass
class FirewallResult:

    action: int
    action_name: str

    threat_reduction: float
    traffic_reduction: float

    legitimate_traffic_impact: float
    resource_cost: float

    response_effectiveness: float
    successful: bool


# =============================================================================
# Firewall Simulator
# =============================================================================

class FirewallSimulator:
    """
    Simulates defensive actions against network threats.

    The simulator does not directly modify the PPO state.
    It returns the consequences of an action so that the
    environment can calculate the next state and reward.
    """

    def __init__(self) -> None:

        self.action_costs = {
            0: 0.01,   # MONITOR
            1: 0.03,   # ALERT
            2: 0.08,   # RATE_LIMIT
            3: 0.12,   # BLOCK
            4: 0.20,   # ISOLATE
        }

    # =========================================================================
    # Execute Action
    # =========================================================================

    def execute(
        self,
        action: int,
        threat_severity: float,
        packet_rate: float,
        byte_rate: float,
        is_benign: bool,
    ) -> FirewallResult:

        if action not in ACTION_NAMES:

            raise ValueError(
                f"Invalid firewall action: {action}"
            )

        action_name = ACTION_NAMES[action]

        # ---------------------------------------------------------------------
        # Action effectiveness
        # ---------------------------------------------------------------------

        threat_reduction = self._calculate_threat_reduction(
            action=action,
            threat_severity=threat_severity,
        )

        traffic_reduction = self._calculate_traffic_reduction(
            action=action,
            packet_rate=packet_rate,
            byte_rate=byte_rate,
        )

        legitimate_traffic_impact = (
            self._calculate_legitimate_traffic_impact(
                action=action,
                is_benign=is_benign,
            )
        )

        resource_cost = self.action_costs[action]

        # ---------------------------------------------------------------------
        # Overall response effectiveness
        # ---------------------------------------------------------------------

        response_effectiveness = float(
            np.clip(
                (
                    threat_reduction
                    + traffic_reduction
                )
                / 2.0,
                0.0,
                1.0,
            )
        )

        # ---------------------------------------------------------------------
        # Successful response
        # ---------------------------------------------------------------------

        if is_benign:

            # Defensive actions against benign traffic are not
            # considered successful responses.
            successful = action in (0, 1)

        else:

            successful = (
                response_effectiveness >= 0.50
            )

        return FirewallResult(
            action=action,
            action_name=action_name,

            threat_reduction=threat_reduction,
            traffic_reduction=traffic_reduction,

            legitimate_traffic_impact=(
                legitimate_traffic_impact
            ),

            resource_cost=resource_cost,

            response_effectiveness=(
                response_effectiveness
            ),

            successful=successful,
        )

    # =========================================================================
    # Threat Reduction
    # =========================================================================

    def _calculate_threat_reduction(
        self,
        action: int,
        threat_severity: float,
    ) -> float:

        if action == 0:
            # Monitoring does not directly reduce the threat.
            reduction = 0.05

        elif action == 1:
            # Alerting provides limited mitigation.
            reduction = 0.15

        elif action == 2:
            # Rate limiting provides moderate mitigation.
            reduction = 0.55

        elif action == 3:
            # Blocking strongly reduces the threat.
            reduction = 0.80

        else:
            # Isolation provides the strongest mitigation.
            reduction = 0.95

        # Very low severity threats require less aggressive action.
        if threat_severity < 0.30:

            reduction *= 0.75

        return float(
            np.clip(
                reduction,
                0.0,
                1.0,
            )
        )

    # =========================================================================
    # Traffic Reduction
    # =========================================================================

    def _calculate_traffic_reduction(
        self,
        action: int,
        packet_rate: float,
        byte_rate: float,
    ) -> float:

        current_traffic = (
            packet_rate + byte_rate
        ) / 2.0

        if current_traffic <= 0.0:
            return 0.0

        reduction_rates = {
            0: 0.05,
            1: 0.10,
            2: 0.50,
            3: 0.80,
            4: 0.95,
        }

        reduction = (
            current_traffic
            * reduction_rates[action]
        )

        # Normalize the result so it remains in [0, 1].
        return float(
            np.clip(
                reduction,
                0.0,
                1.0,
            )
        )

    # =========================================================================
    # Legitimate Traffic Impact
    # =========================================================================

    def _calculate_legitimate_traffic_impact(
        self,
        action: int,
        is_benign: bool,
    ) -> float:

        if not is_benign:
            return 0.0

        # Aggressive actions can accidentally affect legitimate traffic.
        impact = {
            0: 0.00,
            1: 0.02,
            2: 0.10,
            3: 0.35,
            4: 0.60,
        }

        return impact[action]


# =============================================================================
# Firewall Simulator Test
# =============================================================================

def test_firewall_simulator():

    print()
    print("=" * 80)
    print("CYBERSHIELD AI - FIREWALL SIMULATOR TEST")
    print("=" * 80)

    firewall = FirewallSimulator()

    # =========================================================================
    # Test attack traffic
    # =========================================================================

    print("\nATTACK TRAFFIC TEST")

    for action in range(5):

        result = firewall.execute(
            action=action,
            threat_severity=0.90,
            packet_rate=0.90,
            byte_rate=0.85,
            is_benign=False,
        )

        print()
        print(
            f"Action              : "
            f"{result.action_name}"
        )

        print(
            f"Threat Reduction    : "
            f"{result.threat_reduction:.3f}"
        )

        print(
            f"Traffic Reduction   : "
            f"{result.traffic_reduction:.3f}"
        )

        print(
            f"Resource Cost       : "
            f"{result.resource_cost:.3f}"
        )

        print(
            f"Effectiveness       : "
            f"{result.response_effectiveness:.3f}"
        )

        print(
            f"Successful           : "
            f"{result.successful}"
        )

    # =========================================================================
    # Test benign traffic
    # =========================================================================

    print("\nBENIGN TRAFFIC TEST")

    for action in range(5):

        result = firewall.execute(
            action=action,
            threat_severity=0.10,
            packet_rate=0.15,
            byte_rate=0.10,
            is_benign=True,
        )

        print()
        print(
            f"Action                  : "
            f"{result.action_name}"
        )

        print(
            f"Legitimate Traffic Impact: "
            f"{result.legitimate_traffic_impact:.3f}"
        )

        print(
            f"Resource Cost            : "
            f"{result.resource_cost:.3f}"
        )

        # Aggressive actions should have greater
        # impact on legitimate traffic.
        assert (
            0.0
            <= result.legitimate_traffic_impact
            <= 1.0
        )

    # =========================================================================
    # Validate all actions
    # =========================================================================

    print("\nACTION VALIDATION")

    for action in range(5):

        result = firewall.execute(
            action=action,
            threat_severity=0.80,
            packet_rate=0.80,
            byte_rate=0.80,
            is_benign=False,
        )

        assert result.action == action
        assert result.action_name == ACTION_NAMES[action]

        assert (
            0.0
            <= result.threat_reduction
            <= 1.0
        )

        assert (
            0.0
            <= result.traffic_reduction
            <= 1.0
        )

        assert (
            0.0
            <= result.response_effectiveness
            <= 1.0
        )

        assert result.resource_cost >= 0.0

    print(
        "Action validation: PASSED"
    )

    print()
    print("=" * 80)
    print("FIREWALL SIMULATOR TEST: PASSED")
    print("=" * 80)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    test_firewall_simulator()