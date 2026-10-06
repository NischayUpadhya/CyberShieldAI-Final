"""
File        : train_ppo.py
Project     : CyberShield AI
Description : PPO training pipeline for the CyberShield AI
              autonomous cyber-defense system.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path


# =============================================================================
# Project Path
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[3]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# =============================================================================
# Stable Baselines
# =============================================================================

from stable_baselines3 import PPO


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# =============================================================================
# Paths
# =============================================================================

MODEL_DIR = (
    BASE_DIR
    / "ai"
    / "models"
    / "saved"
    / "rl"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_PATH = MODEL_DIR / "cybershield_ppo_v5"


# =============================================================================
# V5 Training Configuration
# =============================================================================

TOTAL_TIMESTEPS = 500_000

LEARNING_RATE = 3e-4

N_STEPS = 2048

BATCH_SIZE = 64

N_EPOCHS = 10

GAMMA = 0.99

GAE_LAMBDA = 0.95

CLIP_RANGE = 0.2

ENT_COEF = 0.01

SEED = 42


# =============================================================================
# Environment Loader
# =============================================================================

def create_environment():
    """
    Create the integrated CyberShield V5 RL environment.
    """

    try:

        from ai.rl.environment.cyber_defense_env import (
            CyberDefenseEnv,
        )

    except ImportError as exc:

        raise ImportError(
            "\nCyberDefenseEnv could not be imported.\n\n"
            "Expected file:\n"
            "ai/rl/environment/cyber_defense_env.py\n\n"
            "Make sure the training command is executed "
            "from the backend directory."
        ) from exc

    return CyberDefenseEnv(
        max_steps=100,
        seed=SEED,
    )


# =============================================================================
# Environment Validation
# =============================================================================

def validate_environment(env) -> None:
    """
    Validate that the V5 environment follows the required RL interface.
    """

    logging.info(
        "Validating CyberShield V5 environment..."
    )

    # -------------------------------------------------------------------------
    # Observation space
    # -------------------------------------------------------------------------

    expected_observation_shape = (26,)

    if env.observation_space.shape != expected_observation_shape:

        raise ValueError(
            "Invalid observation space.\n"
            f"Expected shape: {expected_observation_shape}\n"
            f"Received: {env.observation_space.shape}"
        )

    # -------------------------------------------------------------------------
    # Action space
    # -------------------------------------------------------------------------

    if env.action_space.n != 5:

        raise ValueError(
            "Invalid action space.\n"
            "Expected 5 actions.\n"
            f"Received: {env.action_space.n}"
        )

    logging.info(
        "Observation space: %s",
        env.observation_space,
    )

    logging.info(
        "Action space: %s",
        env.action_space,
    )

    # -------------------------------------------------------------------------
    # Reset test
    # -------------------------------------------------------------------------

    observation, info = env.reset(
        seed=SEED
    )

    if observation.shape != expected_observation_shape:

        raise ValueError(
            "Invalid reset observation shape.\n"
            f"Expected: {expected_observation_shape}\n"
            f"Received: {observation.shape}"
        )

    logging.info(
        "Environment reset test: PASSED"
    )

    # -------------------------------------------------------------------------
    # Step test
    # -------------------------------------------------------------------------

    observation, reward, terminated, truncated, info = (
        env.step(0)
    )

    if observation.shape != expected_observation_shape:

        raise ValueError(
            "Invalid step observation shape.\n"
            f"Expected: {expected_observation_shape}\n"
            f"Received: {observation.shape}"
        )

    if not isinstance(
        reward,
        (int, float),
    ):

        raise TypeError(
            "Environment reward must be numeric."
        )

    if not isinstance(
        terminated,
        bool,
    ):

        raise TypeError(
            "terminated must be bool."
        )

    if not isinstance(
        truncated,
        bool,
    ):

        raise TypeError(
            "truncated must be bool."
        )

    logging.info(
        "Environment step test: PASSED"
    )

    logging.info(
        "Environment validation: PASSED"
    )


# =============================================================================
# Train PPO
# =============================================================================

def train() -> None:

    start_time = time.time()

    logging.info(
        "Starting CyberShield AI V5 PPO training..."
    )

    # -------------------------------------------------------------------------
    # Create environment
    # -------------------------------------------------------------------------

    env = create_environment()

    # -------------------------------------------------------------------------
    # Validate environment
    # -------------------------------------------------------------------------

    validate_environment(
        env
    )

    # -------------------------------------------------------------------------
    # Create PPO model
    # -------------------------------------------------------------------------

    logging.info(
        "Creating PPO V5 model..."
    )

    model = PPO(
        policy="MlpPolicy",
        env=env,

        learning_rate=LEARNING_RATE,

        n_steps=N_STEPS,

        batch_size=BATCH_SIZE,

        n_epochs=N_EPOCHS,

        gamma=GAMMA,

        gae_lambda=GAE_LAMBDA,

        clip_range=CLIP_RANGE,

        ent_coef=ENT_COEF,

        seed=SEED,

        verbose=1,
    )

    logging.info(
        "PPO V5 model created successfully."
    )

    # -------------------------------------------------------------------------
    # Training
    # -------------------------------------------------------------------------

    logging.info(
        "Training PPO V5 for %d timesteps...",
        TOTAL_TIMESTEPS,
    )

    model.learn(
        total_timesteps=TOTAL_TIMESTEPS,
    )

    logging.info(
        "PPO V5 training completed."
    )

    # -------------------------------------------------------------------------
    # Save model
    # -------------------------------------------------------------------------

    model.save(
        MODEL_PATH
    )

    logging.info(
        "PPO V5 model saved to: %s",
        MODEL_PATH,
    )

    # -------------------------------------------------------------------------
    # Close environment
    # -------------------------------------------------------------------------

    env.close()

    execution_time = (
        time.time()
        - start_time
    )

    # -------------------------------------------------------------------------
    # Final output
    # -------------------------------------------------------------------------

    print()

    print(
        "=" * 80
    )

    print(
        "CYBERSHIELD AI - PPO V5 TRAINING"
    )

    print(
        "=" * 80
    )

    print(
        f"Training Timesteps : "
        f"{TOTAL_TIMESTEPS:,}"
    )

    print(
        f"Observation Size   : "
        f"26"
    )

    print(
        f"Action Count       : "
        f"5"
    )

    print(
        f"Learning Rate      : "
        f"{LEARNING_RATE}"
    )

    print(
        f"Batch Size         : "
        f"{BATCH_SIZE}"
    )

    print(
        f"Gamma              : "
        f"{GAMMA}"
    )

    print(
        f"GAE Lambda         : "
        f"{GAE_LAMBDA}"
    )

    print(
        f"Entropy Coefficient: "
        f"{ENT_COEF}"
    )

    print(
        f"Model Path         : "
        f"{MODEL_PATH}"
    )

    print(
        f"Execution Time     : "
        f"{execution_time:.2f} seconds"
    )

    print(
        "=" * 80
    )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    train()