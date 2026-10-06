"""
CyberShield AI - XGBoost + PPO + Blockchain Integration

Connects the existing:
    XGBoost inference service
        ->
    V5 state encoder
        ->
    trained PPO V5 model
        ->
    Blockchain security-event ledger

This module does not modify PPO training or the RL environment.
"""

from pathlib import Path
import sys

import numpy as np
from stable_baselines3 import PPO


# =============================================================================
# Project paths
# =============================================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# =============================================================================
# Existing CyberShield components
# =============================================================================

from app.services.xgboost_service import xgboost_service
from ai.rl.agent.state_encoder import CyberDefenseStateEncoder
from blockchain.service import BlockchainService
from blockchain.event import SecurityEvent


# =============================================================================
# PPO configuration
# =============================================================================

PPO_MODEL_PATH = (
    BACKEND_DIR
    / "ai"
    / "models"
    / "saved"
    / "rl"
    / "cybershield_ppo_v5.zip"
)


ACTION_NAMES = {
    0: "MONITOR",
    1: "ALERT",
    2: "RATE_LIMIT",
    3: "BLOCK",
    4: "ISOLATE",
}


# =============================================================================
# Integration class
# =============================================================================

class CyberShieldIntegration:

    def __init__(self):
        print("Loading CyberShield AI integration...")

        # Existing V5 state encoder.
        self.state_encoder = CyberDefenseStateEncoder()

        # Existing trained PPO V5 model.
        if not PPO_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"PPO V5 model not found at: {PPO_MODEL_PATH}"
            )

        self.ppo_model = PPO.load(
            str(PPO_MODEL_PATH)
        )

        # Existing Blockchain service.
        self.blockchain_service = BlockchainService()

        print("CyberShield AI integration loaded successfully.")


    # =========================================================================
    # End-to-end inference
    # =========================================================================

    def predict_and_record(
        self,
        features,
        source_ip,
        threat_severity,
        packet_rate,
        byte_rate,
        active_threats,
        available_resources=1.0,
        previous_action=0,
    ):
        """
        Run:

            XGBoost
                ->
            26-D state encoder
                ->
            PPO V5
                ->
            Blockchain

        Parameters
        ----------
        features : list
            Exactly 40 numerical XGBoost features.

        source_ip : str
            Source IP associated with the network event.

        threat_severity : float
            Normalized severity in [0, 1].

        packet_rate : float
            Normalized packet rate in [0, 1].

        byte_rate : float
            Normalized byte rate in [0, 1].

        active_threats : int
            Number of active threats.

        available_resources : float
            Available defense resources in [0, 1].

        previous_action : int
            Previous PPO action, 0-4.
        """

        # ---------------------------------------------------------------------
        # 1. XGBoost detection
        # ---------------------------------------------------------------------

        xgb_result = xgboost_service.predict(
            features
        )

        attack_type = xgb_result["predicted_class"]
        attack_name = xgb_result["attack_name"]
        confidence = xgb_result["confidence"]


        # ---------------------------------------------------------------------
        # 2. Convert normalized values to safe ranges
        # ---------------------------------------------------------------------

        threat_severity = float(
            np.clip(
                threat_severity,
                0.0,
                1.0,
            )
        )

        packet_rate = float(
            np.clip(
                packet_rate,
                0.0,
                1.0,
            )
        )

        byte_rate = float(
            np.clip(
                byte_rate,
                0.0,
                1.0,
            )
        )

        available_resources = float(
            np.clip(
                available_resources,
                0.0,
                1.0,
            )
        )

        active_threats = int(
            np.clip(
                active_threats,
                0,
                100,
            )
        )


        # ---------------------------------------------------------------------
        # 3. Build the existing V5 26-dimensional state
        # ---------------------------------------------------------------------

        state = self.state_encoder.encode(
            attack_type=attack_type,
            xgboost_confidence=confidence,
            threat_severity=threat_severity,
            packet_rate=packet_rate,
            byte_rate=byte_rate,
            active_threats=active_threats,
            previous_action=previous_action,
            available_resources=available_resources,
        )


        # Safety validation.
        if state.shape != (26,):
            raise ValueError(
                f"Invalid PPO state shape: {state.shape}. "
                "Expected (26,)."
            )


        # ---------------------------------------------------------------------
        # 4. PPO V5 defense decision
        # ---------------------------------------------------------------------

        observation = state.reshape(
            1,
            -1,
        )

        action, _ = self.ppo_model.predict(
            observation,
            deterministic=True,
        )

        action = int(
            np.asarray(action).reshape(-1)[0]
        )

        action_name = ACTION_NAMES.get(
            action,
            f"UNKNOWN_ACTION_{action}",
        )


        # ---------------------------------------------------------------------
        # 5. Blockchain record
        # ---------------------------------------------------------------------

        severity_name = self._severity_name(
            threat_severity
        )

        security_event = SecurityEvent(
            attack_type=attack_name,
            source_ip=source_ip,
            severity=severity_name,
            xgboost_confidence=confidence,
            ppo_action=action_name,
        )

        block = self.blockchain_service.record_event(
            security_event
        )


        # ---------------------------------------------------------------------
        # 6. Return complete result
        # ---------------------------------------------------------------------

        return {
            "xgboost": {
                "predicted_class": attack_type,
                "attack_name": attack_name,
                "confidence": confidence,
            },

            "ppo": {
                "state_shape": list(state.shape),
                "action": action,
                "action_name": action_name,
            },

            "blockchain": {
                "block_index": block["index"],
                "block_hash": block["hash"],
                "previous_hash": block["previous_hash"],
            },
        }


    # =========================================================================
    # Severity mapping
    # =========================================================================

    @staticmethod
    def _severity_name(
        severity: float,
    ) -> str:

        if severity < 0.40:
            return "Low"

        if severity < 0.70:
            return "Medium"

        if severity < 0.90:
            return "High"

        return "Critical"


# =============================================================================
# Shared integration instance
# =============================================================================

cybershield_integration = CyberShieldIntegration()