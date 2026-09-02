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

MODEL_PATH = MODEL_DIR / "cybershield_ppo"


# =============================================================================
# Training Configuration
# =============================================================================

TOTAL_TIMESTEPS = 100_000

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
    Create the integrated CyberShield RL environment.
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
    Validate that the environment follows the agreed RL interface.
    """

    logging.info(
        "Validating CyberShield environment..."
    )

    # -------------------------------------------------------------------------
    # Observation space
    # -------------------------------------------------------------------------

    if env.observation_space.shape != (8,):

        raise ValueError(
            "Invalid observation space.\n"
            "Expected shape: (8,)\n"
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

    if observation.shape != (8,):

        raise ValueError(
            "Invalid reset observation shape.\n"
            "Expected: (8,)\n"
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

    if observation.shape != (8,):

        raise ValueError(
            "Invalid step observation shape."
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
        "Starting CyberShield PPO training..."
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
        "Creating PPO model..."
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
        "PPO model created successfully."
    )

    # -------------------------------------------------------------------------
    # Training
    # -------------------------------------------------------------------------

    logging.info(
        "Training PPO for %d timesteps...",
        TOTAL_TIMESTEPS,
    )

    model.learn(
        total_timesteps=TOTAL_TIMESTEPS,
    )

    logging.info(
        "PPO training completed."
    )

    # -------------------------------------------------------------------------
    # Save model
    # -------------------------------------------------------------------------

    model.save(
        MODEL_PATH
    )

    logging.info(
        "PPO model saved to: %s",
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
        "CYBERSHIELD AI - PPO TRAINING"
    )

    print(
        "=" * 80
    )

    print(
        f"Training Timesteps : "
        f"{TOTAL_TIMESTEPS:,}"
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