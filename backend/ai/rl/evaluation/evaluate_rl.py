"""
File        : evaluate_rl.py
Project     : CyberShield AI
Description : Evaluation framework for the PPO-based cyber-defense agent.

Author      : Nischay Upadhya P
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

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
# Paths
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BASE_DIR
    / "ai"
    / "models"
    / "saved"
    / "rl"
    / "cybershield_ppo"
)

OUTPUT_DIR = (
    BASE_DIR
    / "ai"
    / "evaluation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =============================================================================
# Evaluation Configuration
# =============================================================================

DEFAULT_EPISODES = 100


# =============================================================================
# Environment
# =============================================================================

def create_environment():
    """
    Load the real CyberShield environment.

    The environment will be implemented separately.
    """

    try:
        from ai.rl.environment.cyber_defense_env import (
            CyberDefenseEnv,
        )
    except ImportError as exc:

        raise ImportError(
            "\nCyberDefenseEnv is not available yet.\n"
            "Evaluation will be enabled after the RL environment "
            "is implemented."
        ) from exc

    return CyberDefenseEnv()


# =============================================================================
# Evaluation
# =============================================================================

def evaluate(
    episodes: int = DEFAULT_EPISODES,
) -> dict:
    """
    Evaluate the trained PPO agent.

    Returns:
        Dictionary containing evaluation metrics.
    """

    start_time = time.time()

    logging.info(
        "Starting PPO evaluation..."
    )

    # -------------------------------------------------------------------------
    # Environment
    # -------------------------------------------------------------------------

    env = create_environment()

    # -------------------------------------------------------------------------
    # Load model
    # -------------------------------------------------------------------------

    logging.info(
        "Loading PPO model..."
    )

    model = PPO.load(
        MODEL_PATH,
        env=env,
    )

    logging.info(
        "PPO model loaded successfully."
    )

    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------

    episode_rewards = []
    episode_lengths = []

    successful_responses = 0
    total_threats = 0

    action_counts = {}

    # -------------------------------------------------------------------------
    # Episodes
    # -------------------------------------------------------------------------

    for episode in range(episodes):

        observation, info = env.reset()

        terminated = False
        truncated = False

        total_reward = 0.0
        episode_length = 0

        while not terminated and not truncated:

            action, _ = model.predict(
                observation,
                deterministic=True,
            )

            action = int(
                np.asarray(action).item()
            )

            action_counts[action] = (
                action_counts.get(action, 0) + 1
            )

            (
                observation,
                reward,
                terminated,
                truncated,
                info,
            ) = env.step(action)

            total_reward += float(reward)

            episode_length += 1

            # -----------------------------------------------------------------
            # Optional environment metrics
            # -----------------------------------------------------------------

            if info.get("threat_present", False):

                total_threats += 1

            if info.get("successful_response", False):

                successful_responses += 1

        episode_rewards.append(
            total_reward
        )

        episode_lengths.append(
            episode_length
        )

        logging.info(
            "Episode %d/%d | Reward: %.2f | Steps: %d",
            episode + 1,
            episodes,
            total_reward,
            episode_length,
        )

    # -------------------------------------------------------------------------
    # Calculate metrics
    # -------------------------------------------------------------------------

    mean_reward = float(
        np.mean(episode_rewards)
    )

    std_reward = float(
        np.std(episode_rewards)
    )

    mean_episode_length = float(
        np.mean(episode_lengths)
    )

    if total_threats > 0:

        response_success_rate = (
            successful_responses
            / total_threats
        )

    else:

        response_success_rate = 0.0

    execution_time = (
        time.time() - start_time
    )

    metrics = {
        "episodes": episodes,
        "mean_reward": mean_reward,
        "std_reward": std_reward,
        "mean_episode_length": mean_episode_length,
        "successful_responses": successful_responses,
        "total_threats": total_threats,
        "response_success_rate": response_success_rate,
        "execution_time_seconds": execution_time,
    }

    # -------------------------------------------------------------------------
    # Save results
    # -------------------------------------------------------------------------

    report_path = (
        OUTPUT_DIR
        / "PPO_Evaluation_Report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "=" * 70 + "\n"
        )

        file.write(
            "CYBERSHIELD AI - PPO EVALUATION REPORT\n"
        )

        file.write(
            "=" * 70 + "\n\n"
        )

        for key, value in metrics.items():

            file.write(
                f"{key}: {value}\n"
            )

        file.write(
            "\nAction Distribution\n"
        )

        file.write(
            str(action_counts)
        )
        

        file.write("\n")

    env.close()

    logging.info(
        "PPO evaluation completed."
    )

    return metrics


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:

    print("=" * 70)
    print("CYBERSHIELD AI - PPO EVALUATION")
    print("=" * 70)

    print(
        "\nEnvironment is required before evaluation can run."
    )

    print(
        "\nEvaluation metrics prepared:"
    )

    print("  • Mean episode reward")
    print("  • Reward standard deviation")
    print("  • Mean episode length")
    print("  • Successful responses")
    print("  • Total threats")
    print("  • Response success rate")
    print("  • Action distribution")

    print("=" * 70)


if __name__ == "__main__":
    main()