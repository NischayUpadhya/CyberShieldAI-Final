from pathlib import Path
import numpy as np
from stable_baselines3 import PPO

from environment.cyber_defense_env import CyberDefenseEnv


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "backend" / "ai" / "models" / "saved" / "rl" / "cybershield_ppo_v2"

ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}

EPISODES = 100
SEED = 42

model = PPO.load(str(MODEL_PATH))
env = CyberDefenseEnv()

attack_actions = {name: 0 for name in ACTION_NAMES.values()}
high_severity_actions = {name: 0 for name in ACTION_NAMES.values()}

total_attack_steps = 0
total_high_severity_steps = 0

for episode in range(EPISODES):

    observation, info = env.reset(seed=SEED + episode)

    terminated = False
    truncated = False

    while not (terminated or truncated):

        # Current state BEFORE the action
        threat_present = info.get("threat_present", False)
        severity = info.get("threat_severity", 0.0)

        action, _ = model.predict(
            observation,
            deterministic=True
        )

        action = int(np.asarray(action).item())
        action_name = ACTION_NAMES[action]

        if threat_present:
            total_attack_steps += 1
            attack_actions[action_name] += 1

        if threat_present and severity >= 0.70:
            total_high_severity_steps += 1
            high_severity_actions[action_name] += 1

        observation, reward, terminated, truncated, info = env.step(action)


print("\n" + "=" * 60)
print("PPO V2 ATTACK ACTION DIAGNOSTIC")
print("=" * 60)

print(f"\nTotal attack steps: {total_attack_steps}")

print("\nActions during ATTACK states:")
for action_name, count in attack_actions.items():
    percentage = (
        count / total_attack_steps * 100
        if total_attack_steps > 0
        else 0
    )
    print(f"{action_name:12s}: {count:5d} ({percentage:6.2f}%)")

print(f"\nHigh-severity attack steps (severity >= 0.70): {total_high_severity_steps}")

print("\nActions during HIGH-SEVERITY attacks:")
for action_name, count in high_severity_actions.items():
    percentage = (
        count / total_high_severity_steps * 100
        if total_high_severity_steps > 0
        else 0
    )
    print(f"{action_name:12s}: {count:5d} ({percentage:6.2f}%)")

print("=" * 60)