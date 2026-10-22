
"""Passive live traffic monitoring API."""

from fastapi import APIRouter, HTTPException

from app.services.live_flow_monitor import live_flow_monitor


router = APIRouter(
    prefix="/api/live-monitor",
    tags=["Live Network Monitor"],
)


@router.get("/status")
def get_status():
    return live_flow_monitor.status()


@router.post("/start")
def start_monitor():
    result = live_flow_monitor.start()

    if result["status"] == "started":
        return result

    return result


@router.post("/stop")
def stop_monitor():
    return live_flow_monitor.stop()


@router.get("/flows")
def get_flows():
    status = live_flow_monitor.status()

    if status["last_error"]:
        raise HTTPException(status_code=500, detail=status["last_error"])

    flows = live_flow_monitor.get_flows()
    prediction_count = sum(flow.get("prediction") is not None for flow in flows)
    ready_count = sum(bool(flow.get("feature_extraction_ready")) for flow in flows)
    return {
        "capture_mode": "passive",
        "model_predictions_enabled": True,
        "prediction_pipeline": "xgboost",
        "flows_with_complete_features": ready_count,
        "flows_with_predictions": prediction_count,
        "defense_execution": "disabled",
        "flows": flows,
    }
