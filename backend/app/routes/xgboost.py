from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.xgboost_service import xgboost_service

router = APIRouter(
    prefix="/api/xgboost",
    tags=["XGBoost"]
)


class XGBoostPredictionRequest(BaseModel):
    features: list[float] = Field(
        ...,
        min_length=40,
        max_length=40,
        description="Exactly 40 numerical features required by the XGBoost model"
    )

    source_ip: str = Field(
        ...,
        description="Source IP address of the detected traffic"
    )


class XGBoostPredictionResponse(BaseModel):
    predicted_class: int
    attack_name: str
    confidence: float
    severity: str
    status: str
    source_ip: str


def determine_severity(attack_name: str, confidence: float) -> str:
    """
    Determine threat severity from attack type and model confidence.
    """

    if attack_name == "Benign":
        return "Low"

    critical_attacks = {
        "DDoS",
        "Infiltration",
        "Heartbleed",
        "SQL Injection"
    }

    high_attacks = {
        "DoS",
        "Bot Attack",
        "Brute Force"
    }

    if attack_name in critical_attacks:
        return "Critical"

    if attack_name in high_attacks:
        return "High"

    if confidence >= 0.90:
        return "High"

    if confidence >= 0.70:
        return "Medium"

    return "Low"


@router.post(
    "/predict",
    response_model=XGBoostPredictionResponse
)
def predict_attack(request: XGBoostPredictionRequest):

    try:

        result = xgboost_service.predict(
            request.features
        )

        severity = determine_severity(
            result["attack_name"],
            result["confidence"]
        )

        status = (
            "Detected"
            if result["attack_name"] != "Benign"
            else "Monitoring"
        )

        return {
            "predicted_class": result["predicted_class"],
            "attack_name": result["attack_name"],
            "confidence": result["confidence"],
            "severity": severity,
            "status": status,
            "source_ip": request.source_ip
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )