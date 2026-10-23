import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import live_monitor
from app.routes import dashboard
from app.routes import threats
from app.routes import xgboost
from app.routes import blockchain
from app.routes import defense

# Import the monitor instance
from app.services.live_flow_monitor import live_flow_monitor

logger = logging.getLogger("uvicorn.error")


def _is_capture_healthy() -> bool:
    """Verify if the live flow monitor capture is actively running and healthy."""
    if not hasattr(live_flow_monitor, "_sniffer_active"):
        return False
    if not live_flow_monitor._sniffer_active():
        return False
    st = live_flow_monitor.status()
    if not st.get("running"):
        return False
    if st.get("last_error"):
        return False
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager.

    Starts passive live flow monitoring when the backend starts and cleanly stops
    capture when the application shuts down.

    Startup Failure Policy:
    If live flow capture fails to start (e.g. missing Npcap, permission denial, or no
    active network interface), the error is logged and recorded in the monitor status.
    The FastAPI application remains available to serve other endpoints (dashboard, threats,
    XGBoost predictions, blockchain, defense status), but live network monitoring is
    truthfully reported as inactive (running=False).
    """
    try:
        try:
            start_result = live_flow_monitor.start()
            status_code = start_result.get("status")
            if status_code == "started":
                if _is_capture_healthy():
                    logger.info(
                        "[live_monitor] Passive network monitoring started successfully on "
                        "interface '%s' (device: %s).",
                        start_result.get("interface"),
                        start_result.get("device"),
                    )
                else:
                    err_msg = (
                        f"Startup returned 'started', but capture sniffer is inactive or has errors: {start_result}"
                    )
                    logger.error("[live_monitor] %s Requesting safe cleanup.", err_msg)
                    with live_flow_monitor._lock:
                        live_flow_monitor._running = False
                        if not live_flow_monitor._last_error:
                            live_flow_monitor._last_error = f"StartupHealthCheckFailed: {err_msg}"
                    try:
                        live_flow_monitor.stop()
                    except Exception as stop_err:
                        logger.error("[live_monitor] Error cleaning up unhealthy capture: %s", stop_err)
            elif status_code == "already_running":
                if _is_capture_healthy():
                    logger.info(
                        "[live_monitor] Monitoring is already running and verified healthy on interface '%s'.",
                        start_result.get("interface"),
                    )
                else:
                    err_msg = (
                        f"Monitoring reported 'already_running', but capture is inactive or unhealthy: {start_result}"
                    )
                    logger.error("[live_monitor] %s Refusing to spawn duplicate capture.", err_msg)
                    with live_flow_monitor._lock:
                        live_flow_monitor._running = False
                        if not live_flow_monitor._last_error:
                            live_flow_monitor._last_error = f"UnhealthyCaptureState: {err_msg}"
            else:
                logger.error(
                    "[live_monitor] Failed to start passive network monitoring: %s. "
                    "Server will remain online with live monitoring inactive.",
                    start_result.get("error", start_result),
                )
        except Exception as startup_err:
            with live_flow_monitor._lock:
                live_flow_monitor._running = False
                live_flow_monitor._last_error = f"LifespanStartupError: {type(startup_err).__name__}: {startup_err}"
            logger.error(
                "[live_monitor] Exception while starting live flow monitor: %s. "
                "Server will remain online with live monitoring inactive.",
                startup_err,
                exc_info=True,
            )
            try:
                live_flow_monitor.stop()
            except Exception as cleanup_err:
                logger.error("[live_monitor] Error cleaning up after startup exception: %s", cleanup_err)

        yield

    finally:
        logger.info("[live_monitor] Shutting down live flow monitor...")
        try:
            stop_response = live_flow_monitor.stop()
            sniffer_still_active = (
                hasattr(live_flow_monitor, "_sniffer_active")
                and live_flow_monitor._sniffer_active()
            )
            legacy_still_active = bool(
                live_flow_monitor._thread
                and getattr(live_flow_monitor._thread, "is_alive", lambda: False)()
            )
            if sniffer_still_active or legacy_still_active:
                logger.warning(
                    "[live_monitor] Incomplete shutdown: capture stop requested (result=%s), "
                    "but capture thread did not terminate within timeout. "
                    "Capture reference retained to avoid duplicate sessions.",
                    stop_response,
                )
            else:
                logger.info(
                    "[live_monitor] Live flow monitor stop requested and capture thread verified terminated cleanly."
                )
        except Exception as shutdown_err:
            logger.error(
                "[live_monitor] Exception during live flow monitor shutdown: %s",
                shutdown_err,
                exc_info=True,
            )


app = FastAPI(
    title="CyberShield AI API",
    description="Backend API for the CyberShield AI cybersecurity platform",
    version="1.0.0",
    lifespan=lifespan,
)

# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "CyberShield AI Backend is running",
        "status": "online",
    }

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(dashboard.router)
app.include_router(threats.router)
app.include_router(xgboost.router)
app.include_router(blockchain.router)
app.include_router(defense.router)
app.include_router(live_monitor.router)
