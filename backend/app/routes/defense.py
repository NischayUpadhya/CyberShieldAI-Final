
"""
CyberShield AI - Autonomous Defense API

Orchestrates:
    XGBoost -> PPO V5 -> Simulated Defense Execution -> Blockchain
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.xgboost_service import xgboost_service
from ai.rl.simulation.network_simulator import NetworkSimulator
from ai.rl.simulation.defense_executor import DefenseExecutor
from ai.integration.xgboost_ppo_blockchain import cybershield_integration


router = APIRouter(
    prefix="/api/defense",
    tags=["Autonomous Defense"],
)

defense_executor = DefenseExecutor()


class DefenseRequest(BaseModel):
    features: list[float] = Field(
        ...,
        min_length=40,
        max_length=40,
        description="Exactly 40 numerical features required by XGBoost",
    )

    source_ip: str = Field(
        ...,
        description="Source IP associated with the test traffic",
    )


@router.post("/analyze")
def analyze_threat(request: DefenseRequest):
    try:
        # 1. Classify the supplied feature vector.
        xgb_result = xgboost_service.predict(request.features)

        # 2. Generate controlled, simulated network context.
        simulator = NetworkSimulator(seed=42)

        scenario = simulator.generate_scenario(
            attack_type=xgb_result["predicted_class"]
        )

        # 3. Run PPO and record the security event.
        result = cybershield_integration.predict_and_record(
            features=request.features,
            source_ip=request.source_ip,
            threat_severity=scenario.threat_severity,
            packet_rate=scenario.packet_rate,
            byte_rate=scenario.byte_rate,
            active_threats=scenario.active_threats,
            available_resources=1.0,
            previous_action=0,
        )

        # 4. Evaluate the chosen action in the firewall simulator.
        execution = defense_executor.execute(
            action=result["ppo"]["action"],
            threat_severity=scenario.threat_severity,
            packet_rate=scenario.packet_rate,
            byte_rate=scenario.byte_rate,
            is_benign=(xgb_result["predicted_class"] == 0),
        )

        # 5. Return both the decision and simulation result.
        result["defense_execution"] = {
            "mode": "simulation",
            "action": execution.action_name,
            "successful": execution.successful,
            "message": execution.message,
            "threat_reduction": execution.threat_reduction,
            "traffic_reduction": execution.traffic_reduction,
            "legitimate_traffic_impact": (
                execution.legitimate_traffic_impact
            ),
            "resource_cost": execution.resource_cost,
            "response_effectiveness": execution.response_effectiveness,
        }

        result["network_context"] = {
            "packet_rate": scenario.packet_rate,
            "byte_rate": scenario.byte_rate,
            "active_threats": scenario.active_threats,
            "threat_severity": scenario.threat_severity,
        }

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Autonomous defense analysis failed: {str(error)}",
        ) from error
