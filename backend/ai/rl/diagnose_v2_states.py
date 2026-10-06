from pathlib import Path
import numpy as np
import torch
from stable_baselines3 import PPO


BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BASE_DIR
    / "backend"
    / "ai"
    / "models"
    / "saved"
    / "rl"
    / "cybershield_ppo_v2"
)

ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}

model = PPO.load(str(MODEL_PATH))


test_states = {
    "Benign": np.array(
        [0.0, 0.95, 0.0, 0.20, 0.20, 0.0, 0.0, 1.0],
        dtype=np.float32
    ),

    "Low severity attack": np.array(
        [2/14, 0.90, 0.20, 0.50, 0.50, 0.10, 0.0, 1.0],
        dtype=np.float32
    ),

    "Medium severity attack": np.array(
        [2/14, 0.90, 0.50, 0.70, 0.70, 0.20, 0.0, 1.0],
        dtype=np.float32
    ),

    "High severity attack": np.array(
        [2/14, 0.95, 0.90, 0.90, 0.90, 0.30, 0.0, 1.0],
        dtype=np.float32
    ),

    "Critical severity attack": np.array(
        [2/14, 0.99, 1.00, 1.00, 1.00, 0.50, 0.0, 1.0],
        dtype=np.float32
    ),
}


print("\n" + "=" * 60)
print("PPO V2 DIRECT STATE DIAGNOSTIC")
print("=" * 60)
for state_name, state in test_states.items():

    obs = torch.tensor(state.reshape(1, -1), dtype=torch.float32)

    distribution = model.policy.get_distribution(obs)
    probabilities = (
        distribution.distribution.probs
        .detach()
        .cpu()
        .numpy()[0]
    )

    action = int(np.argmax(probabilities))

    print(f"\n{state_name}")
    print(f"Selected action: {ACTION_NAMES[action]} ({action})")

    for action_id, probability in enumerate(probabilities):
        print(
            f"  {ACTION_NAMES[action_id]:12s}: "
            f"{probability * 100:6.2f}%"
        )

print("\n" + "=" * 60)  
print("\n" + "=" * 60)