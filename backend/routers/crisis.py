from fastapi import APIRouter, Depends
from datetime import datetime
import uuid

from models import CrisisLogResponse
from auth_utils import get_current_user
from database import get_db

router = APIRouter()


async def log_crisis_internal(db, uid: str, message: str, score: float, level: str, timestamp: str):
    """Called internally by chat router when crisis is detected."""
    crisis_id = str(uuid.uuid4())
    db.collection("crisis_logs").document(crisis_id).set({
        "id":              crisis_id,
        "user_id":         uid,
        "message":         message,
        "sentiment_score": score,
        "crisis_level":    level,
        "timestamp":       timestamp,
        "resolved":        False,
    })
    return crisis_id


@router.get("/logs", response_model=list[CrisisLogResponse])
async def get_crisis_logs(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get all crisis logs for current user."""
    db  = get_db()
    uid = current_user["sub"]

    docs = list(
        db.collection("crisis_logs")
          .where("user_id", "==", uid)
          .order_by("timestamp")
          .limit(limit)
          .stream()
    )

    logs = []
    for doc in docs:
        d = doc.to_dict()
        logs.append(CrisisLogResponse(
            id=d.get("id", doc.id),
            user_id=d.get("user_id", uid),
            message=d.get("message", ""),
            sentiment_score=d.get("sentiment_score", 0),
            crisis_level=d.get("crisis_level", "high"),
            timestamp=d.get("timestamp", ""),
            resolved=d.get("resolved", False),
        ))
    return logs


@router.patch("/logs/{crisis_id}/resolve")
async def resolve_crisis(
    crisis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a crisis log as resolved."""
    db = get_db()
    db.collection("crisis_logs").document(crisis_id).update({"resolved": True})
    return {"message": "Crisis log marked as resolved", "id": crisis_id}


@router.get("/helplines")
async def get_helplines_list():
    """Public endpoint — returns Indian mental health helplines."""
    return [
        {"name": "iCall",                "number": "9152987821",    "hours": "Mon–Sat 8AM–10PM", "type": "counselling"},
        {"name": "Vandrevala Foundation", "number": "1860-2662-345", "hours": "24/7",             "type": "crisis"},
        {"name": "NIMHANS",              "number": "080-46110007",  "hours": "24/7",             "type": "psychiatric"},
        {"name": "Snehi",                "number": "044-24640050",  "hours": "8AM–10PM",         "type": "emotional support"},
    ]
