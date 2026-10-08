from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import dashboard
from app.routes import threats
from app.routes import xgboost
from app.routes import blockchain
from app.routes import defense

app = FastAPI(
    title="CyberShield AI API",
    description="Backend API for the CyberShield AI cybersecurity platform",
    version="1.0.0"
)

# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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
        "status": "online"
    }

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(dashboard.router)
app.include_router(threats.router)
app.include_router(xgboost.router)
app.include_router(blockchain.router)
app.include_router(defense.router)