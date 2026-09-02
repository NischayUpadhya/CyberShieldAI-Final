from fastapi import APIRouter, HTTPException
from app.models.threat import Threat

router = APIRouter(
    prefix="/api/threats",
    tags=["Threats"]
)


# Temporary in-memory threat data
threats = [
    Threat(
        id=1,
        type="Brute Force",
        source_ip="192.168.1.10",
        severity="High",
        status="Blocked"
    ),
    Threat(
        id=2,
        type="SQL Injection",
        source_ip="10.0.0.25",
        severity="Critical",
        status="Blocked"
    ),
    Threat(
        id=3,
        type="Port Scanning",
        source_ip="172.16.0.15",
        severity="Medium",
        status="Monitoring"
    )
]


# GET all threats
@router.get("/", response_model=list[Threat])
def get_threats():
    return threats


# GET one threat
@router.get("/{threat_id}", response_model=Threat)
def get_threat(threat_id: int):

    for threat in threats:
        if threat.id == threat_id:
            return threat

    raise HTTPException(
        status_code=404,
        detail="Threat not found"
    )


# CREATE threat
@router.post("/", response_model=Threat, status_code=201)
def create_threat(threat: Threat):

    # Check if ID already exists
    for existing_threat in threats:
        if existing_threat.id == threat.id:
            raise HTTPException(
                status_code=400,
                detail="Threat ID already exists"
            )

    threats.append(threat)

    return threat


# UPDATE threat
@router.put("/{threat_id}", response_model=Threat)
def update_threat(threat_id: int, updated_threat: Threat):

    for index, threat in enumerate(threats):

        if threat.id == threat_id:

            updated_threat.id = threat_id
            threats[index] = updated_threat

            return updated_threat

    raise HTTPException(
        status_code=404,
        detail="Threat not found"
    )


# DELETE threat
@router.delete("/{threat_id}")
def delete_threat(threat_id: int):

    for index, threat in enumerate(threats):

        if threat.id == threat_id:

            deleted_threat = threats.pop(index)

            return {
                "message": "Threat deleted successfully",
                "threat": deleted_threat
            }

    raise HTTPException(
        status_code=404,
        detail="Threat not found"
    )
@router.post("/from-ai", response_model=Threat, status_code=201)
def create_ai_threat(threat: Threat):

    # Generate a new ID
    if threats:
        new_id = max(t.id for t in threats) + 1
    else:
        new_id = 1

    ai_threat = Threat(
        id=new_id,
        type=threat.type,
        source_ip=threat.source_ip,
        severity=threat.severity,
        status=threat.status
    )

    threats.append(ai_threat)

    return ai_threat