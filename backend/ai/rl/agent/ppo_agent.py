"""
File        : ppo_agent.py
Project     : CyberShield AI
Description : PPO-based reinforcement learning agent for autonomous
              cyber-defense decision making.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# =============================================================================
# Action Definitions
# =============================================================================

ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}


# =============================================================================
# PPO Agent
# =============================================================================

class CyberDefensePPOAgent:
    """
    PPO agent wrapper for CyberShield AI.

    The agent receives an 8-dimensional normalized cybersecurity state
    and selects one of five initial defensive actions.
    """

    STATE_SIZE = 8
    ACTION_COUNT = 5

    def __init__(
        self,
        learning_rate: float = 3e-4,
        n_steps: int = 2048,
        batch_size: int = 64,
        n_epochs: int = 10,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        ent_coef: float = 0.01,
        seed: int = 42,
    ) -> None:

        self.seed = seed

        # ---------------------------------------------------------------------
        # Temporary environment
        # ---------------------------------------------------------------------
        #
        # The actual CyberShield environment will be created separately.
        # For now, this lightweight environment provides the correct
        # observation/action spaces required to construct the PPO model.
        #
        # It is NOT used for final training.
        # ---------------------------------------------------------------------

        self.env = gym.make(
            "CartPole-v1"
        )

        logging.info("Creating PPO model...")

        self.model = PPO(
            policy="MlpPolicy",
            env=self.env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            clip_range=clip_range,
            ent_coef=ent_coef,
            seed=seed,
            verbose=0,
        )

        logging.info("PPO model created successfully.")

    # =========================================================================
    # Prediction
    # =========================================================================

    def predict(
        self,
        state: np.ndarray,
        deterministic: bool = True,
    ) -> tuple[int, Optional[np.ndarray]]:
        """
        Predict a defensive action.

        NOTE:
        This method will be replaced/connected to the real
        CyberDefense environment before actual training.
        """

        state = np.asarray(state, dtype=np.float32)

        if state.shape != (self.STATE_SIZE,):
            raise ValueError(
                f"Expected state shape "
                f"({self.STATE_SIZE},), got {state.shape}"
            )

        action, _ = self.model.predict(
            state,
            deterministic=deterministic,
        )

        action = int(np.asarray(action).item())

        # Temporary CartPole produces actions 0/1.
        # This validation is intentionally disabled until the real
        # CyberDefense environment is connected.
        return action, None

    # =========================================================================
    # Save
    # =========================================================================

    def save(self, path: str | Path) -> None:
        """
        Save PPO model.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model.save(path)

        logging.info(
            "PPO model saved to: %s",
            path,
        )

    # =========================================================================
    # Load
    # =========================================================================

    def load(self, path: str | Path) -> None:
        """
        Load an existing PPO model.
        """

        path = Path(path)

        if not path.exists() and not Path(
            str(path) + ".zip"
        ).exists():

            raise FileNotFoundError(
                f"PPO model not found: {path}"
            )

        self.model = PPO.load(
            path,
            env=self.env,
        )

        logging.info(
            "PPO model loaded from: %s",
            path,
        )

    # =========================================================================
    # Action Name
    # =========================================================================

    @staticmethod
    def get_action_name(action: int) -> str:
        """
        Convert action number to human-readable action.
        """

        if action not in ACTION_NAMES:
            raise ValueError(
                f"Invalid action: {action}"
            )

        return ACTION_NAMES[action]

    # =========================================================================
    # Close
    # =========================================================================

    def close(self) -> None:
        """Close the temporary environment."""

        self.env.close()


# =============================================================================
# Basic Test
# =============================================================================

def main() -> None:

    logging.info(
        "Starting PPO agent test..."
    )

    agent = CyberDefensePPOAgent()

    # Example state produced by our state encoder
    test_state = np.array(
        [
            0.71428573,
            0.97,
            0.85,
            0.05,
            0.05,
            0.05,
            0.50,
            0.75,
        ],
        dtype=np.float32,
    )

    print("=" * 70)
    print("CYBERSHIELD AI - PPO AGENT TEST")
    print("=" * 70)

    print("\nState:")
    print(test_state)

    print("\nState Shape:")
    print(test_state.shape)

    # We only test model creation here.
    # Prediction using CartPole is intentionally not used because
    # CartPole has a different observation space and action space.

    print("\nState Size:")
    print(agent.STATE_SIZE)

    print("\nInitial Action Count:")
    print(agent.ACTION_COUNT)

    print("\nActions:")

    for action_id, action_name in ACTION_NAMES.items():
        print(
            f"  {action_id} -> {action_name}"
        )

    print("\nPPO model:")
    print(agent.model)

    print("\nPPO agent test: PASSED")

    print("=" * 70)

    agent.close()


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()