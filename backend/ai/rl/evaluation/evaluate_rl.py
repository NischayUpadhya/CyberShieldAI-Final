"""
CyberShield AI - PPO V5 Evaluation
Comprehensive evaluator for the 26D CyberDefenseEnv.

Reports:
- overall reward and episode statistics
- overall action distribution
- threat-only action distribution
- response success rate
- threat/traffic reduction
- benign traffic impact
- resource cost
- per-attack performance
- per-severity performance
- policy-collapse check
"""

from __future__ import annotations

import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO


# =============================================================================
# Paths
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[3]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

MODEL_PATH = (
    BASE_DIR
    / "ai"
    / "models"
    / "saved"
    / "rl"
    / "cybershield_ppo_v5"
)

OUTPUT_DIR = BASE_DIR / "ai" / "evaluation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = OUTPUT_DIR / "PPO_Evaluation_Report.txt"


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_EPISODES = 100
MAX_STEPS = 100
SEED = 42

ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}

SEVERITY_NAMES = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH",
    3: "CRITICAL",
}


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# =============================================================================
# Environment
# =============================================================================

def create_environment():
    from ai.rl.environment.cyber_defense_env import CyberDefenseEnv

    return CyberDefenseEnv(
        max_steps=MAX_STEPS,
        seed=SEED,
    )


# =============================================================================
# Helpers
# =============================================================================

def severity_bucket(severity: float) -> str:
    if severity < 0.40:
        return "LOW"
    if severity < 0.70:
        return "MEDIUM"
    if severity < 0.90:
        return "HIGH"
    return "CRITICAL"


def safe_mean(values) -> float:
    return float(np.mean(values)) if values else 0.0


def format_distribution(counts: dict[int, int], total: int) -> list[str]:
    lines = []
    for action_id, name in ACTION_NAMES.items():
        proportion = counts[action_id] / total if total else 0.0
        lines.append(
            f"  {name:12s}: {counts[action_id]:6d} "
            f"({proportion * 100:6.2f}%)"
        )
    return lines


# =============================================================================
# Evaluation
# =============================================================================

def evaluate(episodes: int = DEFAULT_EPISODES) -> dict:
    if episodes <= 0:
        raise ValueError("Number of episodes must be greater than zero.")

    start_time = time.time()

    logging.info("Starting PPO V5 evaluation for %d episodes...", episodes)

    env = create_environment()

    model_file = Path(str(MODEL_PATH) + ".zip")
    if not MODEL_PATH.exists() and not model_file.exists():
        env.close()
        raise FileNotFoundError(
            f"Trained PPO V5 model was not found:\n{model_file}\n\n"
            "Run train_ppo.py first."
        )

    logging.info("Loading PPO V5 model from: %s", MODEL_PATH)

    model = PPO.load(MODEL_PATH, env=env)

    logging.info("PPO V5 model loaded successfully.")

    # -------------------------------------------------------------------------
    # Overall metrics
    # -------------------------------------------------------------------------

    episode_rewards = []
    episode_lengths = []

    action_counts = defaultdict(int)
    threat_action_counts = defaultdict(int)

    threat_reductions = []
    traffic_reductions = []
    benign_impacts = []
    resource_costs = []

    total_threat_steps = 0
    successful_response_steps = 0

    threat_episodes = 0
    successful_threat_episodes = 0

    # -------------------------------------------------------------------------
    # Per-attack metrics
    # -------------------------------------------------------------------------

    attack_stats = defaultdict(
        lambda: {
            "steps": 0,
            "successful_steps": 0,
            "reward": [],
            "threat_reduction": [],
            "traffic_reduction": [],
            "actions": defaultdict(int),
        }
    )

    # -------------------------------------------------------------------------
    # Per-severity metrics
    # -------------------------------------------------------------------------

    severity_stats = defaultdict(
        lambda: {
            "steps": 0,
            "successful_steps": 0,
            "reward": [],
            "threat_reduction": [],
            "traffic_reduction": [],
            "actions": defaultdict(int),
        }
    )

    # -------------------------------------------------------------------------
    # Episodes
    # -------------------------------------------------------------------------

    for episode in range(episodes):

        observation, reset_info = env.reset(seed=SEED + episode)

        initial_attack_name = reset_info.get(
            "attack_name",
            "UNKNOWN",
        )
        initial_attack_type = int(
            reset_info.get(
                "attack_type",
                0,
            )
        )
        initial_severity = float(
            reset_info.get(
                "threat_severity",
                0.0,
            )
        )

        initial_severity_name = severity_bucket(initial_severity)

        is_threat_episode = initial_attack_type != 0
        episode_had_success = False

        if is_threat_episode:
            threat_episodes += 1

        terminated = False
        truncated = False
        total_reward = 0.0
        episode_length = 0

        while not terminated and not truncated:

            action, _ = model.predict(
                observation,
                deterministic=True,
            )

            action = int(np.asarray(action).item())

            if action not in ACTION_NAMES:
                raise ValueError(f"Invalid PPO action: {action}")

            action_counts[action] += 1

            (
                observation,
                reward,
                terminated,
                truncated,
                info,
            ) = env.step(action)

            reward = float(reward)
            total_reward += reward
            episode_length += 1

            # Overall metrics
            threat_present = bool(info.get("threat_present", False))
            successful = bool(info.get("successful_response", False))

            if threat_present:
                total_threat_steps += 1
                threat_action_counts[action] += 1

                if successful:
                    successful_response_steps += 1
                    episode_had_success = True

                attack_name = str(
                    info.get(
                        "attack_name",
                        initial_attack_name,
                    )
                )

                severity_name = severity_bucket(
                    initial_severity
                )

                attack = attack_stats[attack_name]
                attack["steps"] += 1
                attack["actions"][action] += 1
                attack["reward"].append(reward)
                attack["threat_reduction"].append(
                    float(info.get("threat_reduction", 0.0))
                )
                attack["traffic_reduction"].append(
                    float(info.get("traffic_reduction", 0.0))
                )

                if successful:
                    attack["successful_steps"] += 1

                sev = severity_stats[severity_name]
                sev["steps"] += 1
                sev["actions"][action] += 1
                sev["reward"].append(reward)
                sev["threat_reduction"].append(
                    float(info.get("threat_reduction", 0.0))
                )
                sev["traffic_reduction"].append(
                    float(info.get("traffic_reduction", 0.0))
                )

                if successful:
                    sev["successful_steps"] += 1

            threat_reductions.append(
                float(info.get("threat_reduction", 0.0))
            )
            traffic_reductions.append(
                float(info.get("traffic_reduction", 0.0))
            )
            benign_impacts.append(
                float(info.get("legitimate_traffic_impact", 0.0))
            )
            resource_costs.append(
                float(info.get("resource_cost", 0.0))
            )

        if is_threat_episode and episode_had_success:
            successful_threat_episodes += 1

        episode_rewards.append(total_reward)
        episode_lengths.append(episode_length)

        logging.info(
            "Episode %d/%d | Attack: %-20s | Reward: %8.3f | Steps: %3d",
            episode + 1,
            episodes,
            initial_attack_name,
            total_reward,
            episode_length,
        )

    env.close()

    # =============================================================================
    # Aggregate metrics
    # =============================================================================

    total_actions = sum(action_counts.values())
    total_threat_actions = sum(threat_action_counts.values())

    mean_reward = safe_mean(episode_rewards)
    reward_std = float(np.std(episode_rewards)) if episode_rewards else 0.0
    mean_episode_length = safe_mean(episode_lengths)

    response_success_rate = (
        successful_response_steps / total_threat_steps
        if total_threat_steps
        else 0.0
    )

    threat_episode_success_rate = (
        successful_threat_episodes / threat_episodes
        if threat_episodes
        else 0.0
    )

    action_distribution = {
        ACTION_NAMES[action_id]: (
            action_counts[action_id] / total_actions
            if total_actions
            else 0.0
        )
        for action_id in ACTION_NAMES
    }

    threat_action_distribution = {
        ACTION_NAMES[action_id]: (
            threat_action_counts[action_id] / total_threat_actions
            if total_threat_actions
            else 0.0
        )
        for action_id in ACTION_NAMES
    }

    execution_time = time.time() - start_time

    # =============================================================================
    # Policy collapse check
    # =============================================================================

    monitor_ratio = action_distribution["MONITOR"]

    if monitor_ratio >= 0.95:
        policy_status = "WARNING - POLICY DOMINATED BY MONITOR"
    elif monitor_ratio >= 0.80:
        policy_status = "CAUTION - HIGH MONITOR USAGE"
    else:
        policy_status = "PASS - DEFENSE ACTIONS ARE DIVERSIFIED"

    # =============================================================================
    # Metrics dictionary
    # =============================================================================

    metrics = {
        "episodes": episodes,
        "mean_reward": mean_reward,
        "reward_std": reward_std,
        "mean_episode_length": mean_episode_length,
        "successful_response_steps": successful_response_steps,
        "total_threat_steps": total_threat_steps,
        "response_success_rate": response_success_rate,
        "threat_episodes": threat_episodes,
        "successful_threat_episodes": successful_threat_episodes,
        "threat_episode_success_rate": threat_episode_success_rate,
        "mean_threat_reduction": safe_mean(threat_reductions),
        "mean_traffic_reduction": safe_mean(traffic_reductions),
        "mean_legitimate_traffic_impact": safe_mean(benign_impacts),
        "mean_resource_cost": safe_mean(resource_costs),
        "action_distribution": action_distribution,
        "threat_action_distribution": threat_action_distribution,
        "attack_stats": attack_stats,
        "severity_stats": severity_stats,
        "policy_status": policy_status,
        "execution_time_seconds": execution_time,
    }

    # =============================================================================
    # Save report
    # =============================================================================

    with open(REPORT_PATH, "w", encoding="utf-8") as file:

        file.write("=" * 90 + "\n")
        file.write("CYBERSHIELD AI - PPO V5 EVALUATION REPORT\n")
        file.write("=" * 90 + "\n\n")

        file.write("OVERALL METRICS\n")
        file.write("-" * 90 + "\n")
        file.write(f"Episodes                    : {episodes}\n")
        file.write(f"Mean Episode Reward         : {mean_reward:.6f}\n")
        file.write(f"Reward Standard Deviation   : {reward_std:.6f}\n")
        file.write(f"Mean Episode Length         : {mean_episode_length:.6f}\n")
        file.write(f"Threat Episodes             : {threat_episodes}\n")
        file.write(f"Successful Threat Episodes  : {successful_threat_episodes}\n")
        file.write(
            f"Threat Episode Success Rate : "
            f"{threat_episode_success_rate:.6f}\n"
        )
        file.write(f"Total Threat Steps          : {total_threat_steps}\n")
        file.write(
            f"Successful Response Steps   : "
            f"{successful_response_steps}\n"
        )
        file.write(
            f"Response Success Rate       : "
            f"{response_success_rate:.6f}\n"
        )
        file.write(
            f"Mean Threat Reduction       : "
            f"{metrics['mean_threat_reduction']:.6f}\n"
        )
        file.write(
            f"Mean Traffic Reduction      : "
            f"{metrics['mean_traffic_reduction']:.6f}\n"
        )
        file.write(
            f"Mean Legitimate Traffic "
            f"Impact                     : "
            f"{metrics['mean_legitimate_traffic_impact']:.6f}\n"
        )
        file.write(
            f"Mean Resource Cost          : "
            f"{metrics['mean_resource_cost']:.6f}\n"
        )
        file.write(
            f"Policy Status               : "
            f"{policy_status}\n"
        )
        file.write(
            f"Execution Time (seconds)    : "
            f"{execution_time:.3f}\n\n"
        )

        file.write("OVERALL ACTION DISTRIBUTION\n")
        file.write("-" * 90 + "\n")
        for line in format_distribution(action_counts, total_actions):
            file.write(line + "\n")

        file.write("\nTHREAT-ONLY ACTION DISTRIBUTION\n")
        file.write("-" * 90 + "\n")
        for line in format_distribution(
            threat_action_counts,
            total_threat_actions,
        ):
            file.write(line + "\n")

        file.write("\nPER-ATTACK PERFORMANCE\n")
        file.write("-" * 90 + "\n")

        if attack_stats:
            for attack_name in sorted(attack_stats):
                stats = attack_stats[attack_name]
                steps = stats["steps"]

                success_rate = (
                    stats["successful_steps"] / steps
                    if steps
                    else 0.0
                )

                file.write(f"\n{attack_name}\n")
                file.write(
                    f"  Threat Steps        : {steps}\n"
                )
                file.write(
                    f"  Response Success    : "
                    f"{success_rate:.4f}\n"
                )
                file.write(
                    f"  Mean Reward         : "
                    f"{safe_mean(stats['reward']):.4f}\n"
                )
                file.write(
                    f"  Threat Reduction    : "
                    f"{safe_mean(stats['threat_reduction']):.4f}\n"
                )
                file.write(
                    f"  Traffic Reduction  : "
                    f"{safe_mean(stats['traffic_reduction']):.4f}\n"
                )
                file.write("  Actions:\n")

                for line in format_distribution(
                    stats["actions"],
                    steps,
                ):
                    file.write("    " + line.strip() + "\n")

        file.write("\nPER-SEVERITY PERFORMANCE\n")
        file.write("-" * 90 + "\n")

        severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        for severity_name in severity_order:
            if severity_name not in severity_stats:
                continue

            stats = severity_stats[severity_name]
            steps = stats["steps"]

            success_rate = (
                stats["successful_steps"] / steps
                if steps
                else 0.0
            )

            file.write(f"\n{severity_name}\n")
            file.write(
                f"  Threat Steps        : {steps}\n"
            )
            file.write(
                f"  Response Success    : "
                f"{success_rate:.4f}\n"
            )
            file.write(
                f"  Mean Reward         : "
                f"{safe_mean(stats['reward']):.4f}\n"
            )
            file.write(
                f"  Threat Reduction    : "
                f"{safe_mean(stats['threat_reduction']):.4f}\n"
            )
            file.write(
                f"  Traffic Reduction  : "
                f"{safe_mean(stats['traffic_reduction']):.4f}\n"
            )
            file.write("  Actions:\n")

            for line in format_distribution(
                stats["actions"],
                steps,
            ):
                file.write("    " + line.strip() + "\n")

        file.write("\n" + "=" * 90 + "\n")

    logging.info("PPO V5 evaluation completed.")
    logging.info("Evaluation report saved to: %s", REPORT_PATH)

    return metrics


# =============================================================================
# Main
# =============================================================================

def main() -> None:

    print("=" * 90)
    print("CYBERSHIELD AI - PPO V5 EVALUATION")
    print("=" * 90)

    try:
        metrics = evaluate(DEFAULT_EPISODES)
    except Exception as exc:
        print()
        print("PPO V5 evaluation failed:")
        print(exc)
        raise

    print()
    print("Evaluation Results")
    print("-" * 90)

    print(f"Mean Reward              : {metrics['mean_reward']:.4f}")
    print(f"Reward Std                : {metrics['reward_std']:.4f}")
    print(
        f"Mean Episode Length       : "
        f"{metrics['mean_episode_length']:.2f}"
    )
    print(
        f"Threat Episodes           : "
        f"{metrics['threat_episodes']}"
    )
    print(
        f"Successful Threat Episodes: "
        f"{metrics['successful_threat_episodes']}"
    )
    print(
        f"Threat Episode Success    : "
        f"{metrics['threat_episode_success_rate']:.4f}"
    )
    print(
        f"Total Threat Steps        : "
        f"{metrics['total_threat_steps']}"
    )
    print(
        f"Successful Response Steps : "
        f"{metrics['successful_response_steps']}"
    )
    print(
        f"Response Success Rate     : "
        f"{metrics['response_success_rate']:.4f}"
    )
    print(
        f"Mean Threat Reduction     : "
        f"{metrics['mean_threat_reduction']:.4f}"
    )
    print(
        f"Mean Traffic Reduction    : "
        f"{metrics['mean_traffic_reduction']:.4f}"
    )
    print(
        f"Mean Benign Traffic Impact: "
        f"{metrics['mean_legitimate_traffic_impact']:.4f}"
    )
    print(
        f"Mean Resource Cost        : "
        f"{metrics['mean_resource_cost']:.4f}"
    )

    print()
    print("Overall Action Distribution")
    for action_name, proportion in metrics["action_distribution"].items():
        print(
            f"  {action_name:12s}: "
            f"{proportion:.4f}"
        )

    print()
    print("Threat-Only Action Distribution")
    for action_name, proportion in metrics[
        "threat_action_distribution"
    ].items():
        print(
            f"  {action_name:12s}: "
            f"{proportion:.4f}"
        )

    print()
    print(
        f"Policy Status: "
        f"{metrics['policy_status']}"
    )

    print()
    print(
        f"Report saved to: "
        f"{REPORT_PATH}"
    )

    print("=" * 90)


if __name__ == "__main__":
    main()
