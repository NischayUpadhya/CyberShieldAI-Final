"""
File        : cyber_defense_env.py
Project     : CyberShield AI
Description : Integrated Gymnasium environment for autonomous
              cyber-defense using reinforcement learning.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

BACKEND_DIR = Path(__file__).resolve().parents[3]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ai.rl.simulation.network_simulator import (
    ATTACK_NAMES,
    NetworkScenario,
    NetworkSimulator,
)

from ai.rl.simulation.firewall_simulator import (
    ACTION_NAMES,
    FirewallSimulator,
)

from ai.rl.simulation.resource_manager import (
    ResourceManager,
)
from ai.rl.agent.state_encoder import (
    CyberDefenseStateEncoder,
)

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# =============================================================================
# Cyber Defense Environment
# =============================================================================

class CyberDefenseEnv(gym.Env):
    """
    Integrated CyberShield AI reinforcement-learning environment.

    Observation:

        V5 26-dimensional normalized state:
        - 15 attack-type one-hot features
        - 5 normalized continuous threat/network features
        - 5 previous-action one-hot features
        - 1 normalized resource feature

    Actions:

        0 -> MONITOR
        1 -> ALERT
        2 -> RATE_LIMIT
        3 -> BLOCK
        4 -> ISOLATE
    """

    metadata = {
        "render_modes": ["human"]
    }

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(
        self,
        max_steps: int = 100,
        render_mode: str | None = None,
        seed: int | None = None,
    ) -> None:

        super().__init__()
        self.state_encoder = CyberDefenseStateEncoder()
        self.max_steps = max_steps
        self.render_mode = render_mode

        # ---------------------------------------------------------------------
        # Gymnasium spaces
        # ---------------------------------------------------------------------

        self.observation_space = spaces.Box(
          low=0.0,
          high=1.0,
          shape=(CyberDefenseStateEncoder.STATE_SIZE,),
          dtype=np.float32,
         )
        self.action_space = spaces.Discrete(5)

        # ---------------------------------------------------------------------
        # Simulation components
        # ---------------------------------------------------------------------

        self.network_simulator = NetworkSimulator(
            seed=seed
        )

        self.firewall_simulator = FirewallSimulator()

        self.resource_manager = ResourceManager(
            initial_resources=1.0,
            recovery_rate=0.02,
        )

        # ---------------------------------------------------------------------
        # Environment state
        # ---------------------------------------------------------------------

        self.current_step = 0

        self.scenario: NetworkScenario | None = None

        self.attack_type = 0
        self.xgboost_confidence = 0.0
        self.threat_severity = 0.0
        self.packet_rate = 0.0
        self.byte_rate = 0.0
        self.active_threats = 0

        self.previous_action = 0

        self.available_resources = 1.0

        self.last_reward = 0.0

        self.last_action_allowed = True

        self.last_response_effectiveness = 0.0

        self.last_threat_reduction = 0.0

        self.last_traffic_reduction = 0.0

        self.last_legitimate_traffic_impact = 0.0
        
        self.last_resource_cost = 0.0

    # =========================================================================
    # Reset
    # =========================================================================

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ):

        super().reset(seed=seed)

        # ---------------------------------------------------------------------
        # Synchronize simulator seed when Gymnasium provides one
        # ---------------------------------------------------------------------

        if seed is not None:

            self.network_simulator = NetworkSimulator(
                seed=seed
            )

        # ---------------------------------------------------------------------
        # Reset environment
        # ---------------------------------------------------------------------

        self.current_step = 0

        self.previous_action = 0

        self.last_reward = 0.0

        self.last_action_allowed = True

        self.last_response_effectiveness = 0.0

        self.last_threat_reduction = 0.0

        self.last_traffic_reduction = 0.0

        self.last_legitimate_traffic_impact = 0.0

        # ---------------------------------------------------------------------
        # Reset resources
        # ---------------------------------------------------------------------

        self.resource_manager.reset()

        self.available_resources = (
            self.resource_manager.get_available_resources()
        )

        # ---------------------------------------------------------------------
        # Generate initial network scenario
        # ---------------------------------------------------------------------

        self.scenario = (
            self.network_simulator.generate_scenario()
        )

        self._load_scenario(
            self.scenario
        )

        observation = self._get_observation()

        info = self._get_info()

        return observation, info

    # =========================================================================
    # Load Scenario
    # =========================================================================

    def _load_scenario(
        self,
        scenario: NetworkScenario,
    ) -> None:

        self.scenario = scenario

        self.attack_type = scenario.attack_type

        self.xgboost_confidence = (
            scenario.xgboost_confidence
        )

        self.threat_severity = (
            scenario.threat_severity
        )

        self.packet_rate = (
            scenario.packet_rate
        )

        self.byte_rate = (
            scenario.byte_rate
        )

        self.active_threats = (
            scenario.active_threats
        )

    # =========================================================================
    # Step
    # =========================================================================

    def step(self, action):

        action = int(action)

        if not self.action_space.contains(action):

            raise ValueError(
                f"Invalid action: {action}"
            )

        self.current_step += 1

        self.previous_action = action

        # ---------------------------------------------------------------------
        # Determine whether current traffic is benign
        # ---------------------------------------------------------------------

        is_benign = (
            self.attack_type == 0
        )

        # ---------------------------------------------------------------------
        # Resource Manager
        # ---------------------------------------------------------------------

        resource_result = (
            self.resource_manager.execute(
                action
            )
        )
        self.last_resource_cost = (
           resource_result.resource_cost
        )                       

        self.available_resources = (
            resource_result.resource_after
        )

        self.last_action_allowed = (
            resource_result.action_allowed
        )

        # ---------------------------------------------------------------------
        # Firewall Simulator
        # ---------------------------------------------------------------------

        firewall_result = (
            self.firewall_simulator.execute(
                action=action,
                threat_severity=self.threat_severity,
                packet_rate=self.packet_rate,
                byte_rate=self.byte_rate,
                is_benign=is_benign,
            )
        )

        self.last_response_effectiveness = (
            firewall_result.response_effectiveness
        )

        self.last_threat_reduction = (
            firewall_result.threat_reduction
        )

        self.last_traffic_reduction = (
            firewall_result.traffic_reduction
        )

        self.last_legitimate_traffic_impact = (
            firewall_result.legitimate_traffic_impact
        )

        # ---------------------------------------------------------------------
        # Handle insufficient resources
        # ---------------------------------------------------------------------

        if not resource_result.action_allowed:

            reward = -10.0

            self.last_response_effectiveness = 0.0

        else:

            reward = self._calculate_reward(
                action=action,
                firewall_result=firewall_result,
                resource_result=resource_result,
            )

        self.last_reward = reward

        # ---------------------------------------------------------------------
        # Apply firewall effect to environment state
        # ---------------------------------------------------------------------

        if resource_result.action_allowed:

            self._apply_firewall_effect(
                firewall_result.threat_reduction,
                firewall_result.traffic_reduction,
            )

        # ---------------------------------------------------------------------
        # Natural network evolution
        # ---------------------------------------------------------------------

        self._update_environment()

        # ---------------------------------------------------------------------
        # Episode termination
        # ---------------------------------------------------------------------

        terminated = False

        # Attack successfully mitigated
        if (
            self.attack_type != 0
            and self.threat_severity <= 0.05
        ):

            terminated = True

        # Resource exhaustion
        if (
            self.available_resources <= 0.0
            and self.attack_type != 0
        ):

            terminated = True

        # Maximum episode length
        truncated = (
            self.current_step >= self.max_steps
        )

        observation = self._get_observation()

        info = self._get_info()

        return (
            observation,
            float(reward),
            terminated,
            truncated,
            info,
        )

    # =========================================================================
    # Reward
    # =========================================================================
       # =========================================================================
    # Reward
    # =========================================================================
    def _calculate_reward(
        self,
        action: int,
        firewall_result,
        resource_result,
    ) -> float:

        severity = self.threat_severity

        # ---------------------------------------------------------------------
        # Benign traffic
        # ---------------------------------------------------------------------

        if self.attack_type == 0:

            # MONITOR is the preferred action.
            if action == 0:
                reward = 4.0

            # ALERT is acceptable but unnecessary.
            elif action == 1:
                reward = 1.0

            # RATE_LIMIT may affect legitimate traffic.
            elif action == 2:
                reward = -4.0

            # BLOCK causes significant disruption.
            elif action == 3:
                reward = -10.0

            # ISOLATE is the most aggressive action.
            else:
                reward = -12.0

            # Penalize legitimate traffic disruption.
            reward -= (
                firewall_result.legitimate_traffic_impact
                * 12.0
            )

        # ---------------------------------------------------------------------
        # Attack traffic
        # ---------------------------------------------------------------------

        else:

            # -------------------------------------------------------------
            # Low severity
            # -------------------------------------------------------------

            if severity < 0.40:

                if action == 0:          # MONITOR
                    reward = 5.0

                elif action == 1:        # ALERT
                    reward = 3.0

                elif action == 2:        # RATE_LIMIT
                    reward = 1.0

                elif action == 3:        # BLOCK
                    reward = -3.0

                else:                    # ISOLATE
                    reward = -5.0

            # -------------------------------------------------------------
            # Medium severity
            # -------------------------------------------------------------

            elif severity < 0.70:

                if action == 0:          # MONITOR
                    reward = -4.0

                elif action == 1:        # ALERT
                    reward = 5.0

                elif action == 2:        # RATE_LIMIT
                    reward = 6.0

                elif action == 3:        # BLOCK
                    reward = 3.0

                else:                    # ISOLATE
                    reward = -1.0

            # -------------------------------------------------------------
            # High severity
            # -------------------------------------------------------------

            elif severity < 0.90:

                if action == 0:          # MONITOR
                    reward = -10.0

                elif action == 1:        # ALERT
                    reward = -1.0

                elif action == 2:        # RATE_LIMIT
                    reward = 7.0

                elif action == 3:        # BLOCK
                    reward = 10.0

                else:                    # ISOLATE
                    reward = 8.0

            # -------------------------------------------------------------
            # Critical severity
            # -------------------------------------------------------------

            else:

                if action == 0:          # MONITOR
                    reward = -15.0

                elif action == 1:        # ALERT
                    reward = -7.0

                elif action == 2:        # RATE_LIMIT
                    reward = 2.0

                elif action == 3:        # BLOCK
                    reward = 12.0

                else:                    # ISOLATE
                    reward = 15.0

            # -------------------------------------------------------------
            # Defense effectiveness
            # -------------------------------------------------------------

            reward += (
                firewall_result.response_effectiveness
                * 10.0
            )

            # Reward actual threat reduction.
            reward += (
                firewall_result.threat_reduction
                * 15.0
            )

            # Reward useful traffic reduction.
            reward += (
                firewall_result.traffic_reduction
                * 5.0
            )

        # ---------------------------------------------------------------------
        # Resource cost
        # ---------------------------------------------------------------------

        reward -= (
            resource_result.resource_cost
            * 3.0
        )

        # ---------------------------------------------------------------------
        # Successful response bonus
        # ---------------------------------------------------------------------

        if firewall_result.successful:
            reward += 5.0

        return float(reward)
    # =========================================================================
    # Apply Firewall Effect
    # =========================================================================

    def _apply_firewall_effect(
        self,
        threat_reduction: float,
        traffic_reduction: float,
    ) -> None:

        # Reduce threat severity.
        self.threat_severity *= (
            1.0 - threat_reduction
        )

        # Reduce network traffic.
        self.packet_rate *= (
            1.0 - traffic_reduction
        )

        self.byte_rate *= (
            1.0 - traffic_reduction
        )

        self.threat_severity = float(
            np.clip(
                self.threat_severity,
                0.0,
                1.0,
            )
        )

        self.packet_rate = float(
            np.clip(
                self.packet_rate,
                0.0,
                1.0,
            )
        )

        self.byte_rate = float(
            np.clip(
                self.byte_rate,
                0.0,
                1.0,
            )
        )

    # =========================================================================
    # Natural Network Evolution
    # =========================================================================

    def _update_environment(self) -> None:

        # Small random network changes.
        self.packet_rate += float(
            self.network_simulator.rng.uniform(
                -0.02,
                0.02,
            )
        )

        self.byte_rate += float(
            self.network_simulator.rng.uniform(
                -0.02,
                0.02,
            )
        )

        # Attacks can become slightly stronger naturally.
        if self.attack_type != 0:

            self.threat_severity += float(
                self.network_simulator.rng.uniform(
                    -0.01,
                    0.03,
                )
            )

        else:

            self.threat_severity += float(
                self.network_simulator.rng.uniform(
                    -0.01,
                    0.01,
                )
            )

        self.packet_rate = float(
            np.clip(
                self.packet_rate,
                0.0,
                1.0,
            )
        )

        self.byte_rate = float(
            np.clip(
                self.byte_rate,
                0.0,
                1.0,
            )
        )

        self.threat_severity = float(
            np.clip(
                self.threat_severity,
                0.0,
                1.0,
            )
        )

    # =========================================================================
    # Observation
    # =========================================================================
    def _get_observation(self) -> np.ndarray:
        """
        Encode the current environment state using the V5
        categorical + normalized state representation.
        """

        observation = self.state_encoder.encode(
        attack_type=self.attack_type,
        xgboost_confidence=self.xgboost_confidence,
        threat_severity=self.threat_severity,
        packet_rate=self.packet_rate,
        byte_rate=self.byte_rate,
        active_threats=self.active_threats,
        previous_action=self.previous_action,
        available_resources=self.available_resources,
       )

        return observation

    # =========================================================================
    # Information
    # =========================================================================

    def _get_info(self):

        attack_name = ATTACK_NAMES[
            self.attack_type
        ]

        return {
            "step": self.current_step,

            "attack_type": self.attack_type,

            "attack_name": attack_name,

            "xgboost_confidence": (
                self.xgboost_confidence
            ),

            "threat_severity": (
                self.threat_severity
            ),

            "packet_rate": (
                self.packet_rate
            ),

            "byte_rate": (
                self.byte_rate
            ),

            "active_threats": (
                self.active_threats
            ),

            "previous_action": (
                self.previous_action
            ),

            "action_name": ACTION_NAMES[
                self.previous_action
            ],

            "available_resources": (
                self.available_resources
            ),

            "action_allowed": (
                self.last_action_allowed
            ),

            "response_effectiveness": (
                self.last_response_effectiveness
            ),

            "threat_reduction": (
                self.last_threat_reduction
            ),

            "traffic_reduction": (
                self.last_traffic_reduction
            ),

            "legitimate_traffic_impact": (
                self.last_legitimate_traffic_impact
            ),
            
                        "resource_cost": self.last_resource_cost,

            "threat_present": self.attack_type != 0,

            "successful_response": (
                self.attack_type != 0
                and self.last_response_effectiveness >= 0.50
            ),

            "reward": self.last_reward,
        }

    # =========================================================================
    # Render
    # =========================================================================

    def render(self):

        print()
        print("=" * 80)
        print("CYBERSHIELD AI - INTEGRATED CYBER DEFENSE ENVIRONMENT")
        print("=" * 80)

        print(
            f"Step                : "
            f"{self.current_step}"
        )

        print(
            f"Attack              : "
            f"{ATTACK_NAMES[self.attack_type]}"
        )

        print(
            f"XGBoost Confidence  : "
            f"{self.xgboost_confidence:.3f}"
        )

        print(
            f"Threat Severity     : "
            f"{self.threat_severity:.3f}"
        )

        print(
            f"Packet Rate         : "
            f"{self.packet_rate:.3f}"
        )

        print(
            f"Byte Rate           : "
            f"{self.byte_rate:.3f}"
        )

        print(
            f"Active Threats      : "
            f"{self.active_threats}"
        )

        print(
            f"Action              : "
            f"{ACTION_NAMES[self.previous_action]}"
        )

        print(
            f"Action Allowed      : "
            f"{self.last_action_allowed}"
        )

        print(
            f"Response Effectiveness: "
            f"{self.last_response_effectiveness:.3f}"
        )

        print(
            f"Available Resources : "
            f"{self.available_resources:.3f}"
        )

        print(
            f"Reward              : "
            f"{self.last_reward:.3f}"
        )

        print("=" * 80)

    # =========================================================================
    # Close
    # =========================================================================

    def close(self):

        pass


# =============================================================================
# Integrated Environment Test
# =============================================================================

def test_environment():

    print()
    print("=" * 80)
    print("CYBERSHIELD AI - INTEGRATED ENVIRONMENT TEST")
    print("=" * 80)

    env = CyberDefenseEnv(
        max_steps=20,
        seed=42,
    )

    # =========================================================================
    # Space validation
    # =========================================================================

    print(
        f"\nObservation Space : "
        f"{env.observation_space}"
    )

    print(
        f"Action Space      : "
        f"{env.action_space}"
    )

    assert env.observation_space.shape == (26,)

    assert env.action_space.n == 5

    print(
        "\nSpace validation: PASSED"
    )

    # =========================================================================
    # Reset
    # =========================================================================

    observation, info = env.reset(
        seed=42
    )

    print(
        "\nInitial State:"
    )

    print(
        observation
    )

    print(
        "\nInitial Attack:"
    )

    print(
        info["attack_name"]
    )

    assert observation.shape == (26,)

    assert observation.dtype == np.float32

    print(
        "\nReset test: PASSED"
    )

    # =========================================================================
    # Execute all actions
    # =========================================================================

    print(
        "\nTesting all defense actions..."
    )

    for action in range(5):

        observation, reward, terminated, truncated, info = (
            env.step(action)
        )

        print()
        print(
            f"Action {action} -> "
            f"{ACTION_NAMES[action]}"
        )

        print(
            f"Reward                : "
            f"{reward:.3f}"
        )

        print(
            f"Action Allowed        : "
            f"{info['action_allowed']}"
        )

        print(
            f"Threat Reduction      : "
            f"{info['threat_reduction']:.3f}"
        )

        print(
            f"Traffic Reduction     : "
            f"{info['traffic_reduction']:.3f}"
        )

        print(
            f"Response Effectiveness: "
            f"{info['response_effectiveness']:.3f}"
        )

        print(
            f"Resources Remaining   : "
            f"{info['available_resources']:.3f}"
        )

        assert observation.shape == (26,)

        assert isinstance(
            reward,
            float,
        )

        assert isinstance(
            terminated,
            bool,
        )

        assert isinstance(
            truncated,
            bool,
        )

    print(
        "\nAction integration test: PASSED"
    )

    # =========================================================================
    # Gymnasium validation
    # =========================================================================

    from gymnasium.utils.env_checker import check_env

    check_env(
        CyberDefenseEnv()
    )

    print(
        "\nGymnasium environment check: PASSED"
    )

    env.close()

    print()
    print("=" * 80)
    print(
        "INTEGRATED ENVIRONMENT TEST: PASSED"
    )
    print("=" * 80)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    test_environment()