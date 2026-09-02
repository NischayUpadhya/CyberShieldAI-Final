"""
File        : resource_manager.py
Project     : CyberShield AI
Description : Manages limited cybersecurity resources used by
              defensive actions in the reinforcement learning system.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# =============================================================================
# Resource Costs
# =============================================================================

ACTION_RESOURCE_COSTS = {
    0: 0.01,   # MONITOR
    1: 0.03,   # ALERT
    2: 0.08,   # RATE_LIMIT
    3: 0.12,   # BLOCK
    4: 0.20,   # ISOLATE
}


ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}


# =============================================================================
# Resource Result
# =============================================================================

@dataclass
class ResourceResult:

    action: int
    action_name: str

    resource_before: float
    resource_after: float

    resource_cost: float
    recovery: float

    action_allowed: bool
    resource_utilization: float


# =============================================================================
# Resource Manager
# =============================================================================

class ResourceManager:
    """
    Simulates a limited cybersecurity resource pool.

    Resource level:
        1.0 -> 100% resources available
        0.0 -> no resources available

    More aggressive defense actions consume more resources.
    """

    def __init__(
        self,
        initial_resources: float = 1.0,
        recovery_rate: float = 0.02,
    ) -> None:

        self.initial_resources = float(
            np.clip(
                initial_resources,
                0.0,
                1.0,
            )
        )

        self.recovery_rate = float(
            np.clip(
                recovery_rate,
                0.0,
                1.0,
            )
        )

        self.available_resources = (
            self.initial_resources
        )

    # =========================================================================
    # Reset
    # =========================================================================

    def reset(
        self,
        resources: float | None = None,
    ) -> float:

        if resources is None:

            resources = (
                self.initial_resources
            )

        self.available_resources = float(
            np.clip(
                resources,
                0.0,
                1.0,
            )
        )

        return self.available_resources

    # =========================================================================
    # Execute Resource Request
    # =========================================================================

    def execute(
        self,
        action: int,
    ) -> ResourceResult:

        if action not in ACTION_RESOURCE_COSTS:

            raise ValueError(
                f"Invalid action: {action}"
            )

        action_name = ACTION_NAMES[action]

        resource_before = (
            self.available_resources
        )

        resource_cost = (
            ACTION_RESOURCE_COSTS[action]
        )

        # ---------------------------------------------------------------------
        # Check whether enough resources are available
        # ---------------------------------------------------------------------

        action_allowed = (
            resource_before >= resource_cost
        )

        if action_allowed:

            self.available_resources -= (
                resource_cost
            )

        # ---------------------------------------------------------------------
        # Resource recovery
        # ---------------------------------------------------------------------

        recovery = self._recover_resources()

        resource_after = (
            self.available_resources
        )

        # ---------------------------------------------------------------------
        # Resource utilization
        # ---------------------------------------------------------------------

        resource_utilization = float(
            np.clip(
                1.0 - resource_after,
                0.0,
                1.0,
            )
        )

        return ResourceResult(
            action=action,
            action_name=action_name,

            resource_before=resource_before,
            resource_after=resource_after,

            resource_cost=resource_cost,
            recovery=recovery,

            action_allowed=action_allowed,

            resource_utilization=(
                resource_utilization
            ),
        )

    # =========================================================================
    # Resource Recovery
    # =========================================================================

    def _recover_resources(self) -> float:

        before_recovery = (
            self.available_resources
        )

        self.available_resources = float(
            np.clip(
                self.available_resources
                + self.recovery_rate,
                0.0,
                1.0,
            )
        )

        return float(
            self.available_resources
            - before_recovery
        )

    # =========================================================================
    # Availability Check
    # =========================================================================

    def can_execute(
        self,
        action: int,
    ) -> bool:

        if action not in ACTION_RESOURCE_COSTS:

            raise ValueError(
                f"Invalid action: {action}"
            )

        return (
            self.available_resources
            >= ACTION_RESOURCE_COSTS[action]
        )

    # =========================================================================
    # Get Current Resources
    # =========================================================================

    def get_available_resources(self) -> float:

        return self.available_resources


# =============================================================================
# Resource Manager Test
# =============================================================================

def test_resource_manager():

    print()
    print("=" * 80)
    print("CYBERSHIELD AI - RESOURCE MANAGER TEST")
    print("=" * 80)

    manager = ResourceManager(
        initial_resources=1.0,
        recovery_rate=0.02,
    )

    # =========================================================================
    # Initial State
    # =========================================================================

    print(
        "\nInitial Resources:"
    )

    print(
        f"{manager.get_available_resources():.3f}"
    )

    assert (
        manager.get_available_resources()
        == 1.0
    )

    print(
        "Initial resource test: PASSED"
    )

    # =========================================================================
    # Test Every Action
    # =========================================================================

    print(
        "\nTesting defensive actions..."
    )

    for action in range(5):

        before = (
            manager.get_available_resources()
        )

        result = manager.execute(
            action
        )

        print()

        print(
            f"Action              : "
            f"{result.action_name}"
        )

        print(
            f"Resource Before     : "
            f"{result.resource_before:.3f}"
        )

        print(
            f"Resource Cost       : "
            f"{result.resource_cost:.3f}"
        )

        print(
            f"Recovery            : "
            f"{result.recovery:.3f}"
        )

        print(
            f"Resource After      : "
            f"{result.resource_after:.3f}"
        )

        print(
            f"Action Allowed      : "
            f"{result.action_allowed}"
        )

        print(
            f"Resource Utilization: "
            f"{result.resource_utilization:.3f}"
        )

        assert (
            0.0
            <= result.resource_after
            <= 1.0
        )

        assert (
            result.resource_cost
            == ACTION_RESOURCE_COSTS[action]
        )

        assert (
            0.0
            <= result.resource_utilization
            <= 1.0
        )

        assert (
            result.resource_after
            <= 1.0
        )

        assert before >= result.resource_before

    print(
        "\nAction resource tests: PASSED"
    )

    # =========================================================================
    # Test Resource Exhaustion
    # =========================================================================

    print(
        "\nTesting resource exhaustion..."
    )

    manager.reset(
        resources=0.05
    )

    print(
        f"Available Resources: "
        f"{manager.get_available_resources():.3f}"
    )

    # ISOLATE requires 0.20 resources.
    assert not manager.can_execute(4)

    result = manager.execute(4)

    print(
        f"ISOLATE allowed: "
        f"{result.action_allowed}"
    )

    assert (
        result.action_allowed
        is False
    )

    print(
        "Resource exhaustion test: PASSED"
    )

    # =========================================================================
    # Test Recovery
    # =========================================================================

    print(
        "\nTesting resource recovery..."
    )

    manager.reset(
        resources=0.50
    )

    before = (
        manager.get_available_resources()
    )

    result = manager.execute(3)

    after = (
        manager.get_available_resources()
    )

    print(
        f"Before : {before:.3f}"
    )

    print(
        f"After  : {after:.3f}"
    )

    assert (
        after
        <= 1.0
    )

    print(
        "Resource recovery test: PASSED"
    )

    # =========================================================================
    # Final
    # =========================================================================

    print()
    print("=" * 80)
    print("RESOURCE MANAGER TEST: PASSED")
    print("=" * 80)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    test_resource_manager()