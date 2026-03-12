from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid

from models import ChatMessage, BotReply, ChatMessageResponse
from auth_utils import get_current_user
from database import get_db
from sentiment import analyse_sentiment, get_bot_reply, is_crisis, get_helplines
from routers.crisis import log_crisis_internal

import json
import os

router = APIRouter()

# Simple file-based chat store for demo mode
DEMO_CHATS_FILE = "demo_chats.json"

def _load_demo_chats():
    if os.path.exists(DEMO_CHATS_FILE):
        try:
            with open(DEMO_CHATS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_demo_chats(chats):
    try:
        with open(DEMO_CHATS_FILE, "w") as f:
            json.dump(chats, f)
    except Exception:
        pass

_demo_chats = _load_demo_chats()


@router.post("/send", response_model=BotReply)
async def send_message(
    payload: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    global _demo_chats
    _demo_chats = _load_demo_chats()
    db  = get_db()
    uid = current_user["sub"]
    now = datetime.utcnow().isoformat()

    # Get recent history for context
    history = []
    
    # Try demo store first
    user_chats = _demo_chats.get(uid, [])
    if user_chats:
        history = user_chats[-5:]
    else:
        # Fallback to Firebase
        try:
            history_docs = list(
                db.collection("chats").document(uid)
                  .collection("messages")
                  .order_by("timestamp", direction="DESCENDING")
                  .limit(5)
                  .stream()
            )
            history = [d.to_dict() for d in reversed(history_docs)]
        except Exception:
            pass

    score, level = analyse_sentiment(payload.content)
    crisis       = is_crisis(level)
    bot_text     = get_bot_reply(score, level, history)
    msg_id       = str(uuid.uuid4())
    bot_id       = str(uuid.uuid4())

    user_msg = {
        "id":              msg_id,
        "user_id":         uid,
        "content":         payload.content,
        "role":            "user",
        "sentiment_score": score,
        "sentiment_level": level,
        "timestamp":       now,
    }
    
    bot_msg = {
        "id":        bot_id,
        "user_id":   uid,
        "content":   bot_text,
        "role":      "bot",
        "timestamp": now,
    }

    # Save to demo store
    if uid not in _demo_chats:
        _demo_chats[uid] = []
    _demo_chats[uid].append(user_msg)
    _demo_chats[uid].append(bot_msg)
    _save_demo_chats(_demo_chats)

    # Also try saving to Firebase (if connected)
    try:
        db.collection("chats").document(uid).collection("messages").document(msg_id).set(user_msg)
        db.collection("chats").document(uid).collection("messages").document(bot_id).set(bot_msg)
    except Exception:
        pass

    # Auto-log crisis
    if crisis:
        try:
            await log_crisis_internal(db, uid, payload.content, score, level, now)
        except Exception:
            pass

    return BotReply(
        message=bot_text,
        sentiment_score=score,
        sentiment_level=level,
        crisis_detected=crisis,
        helplines=get_helplines() if crisis else None,
    )


@router.get("/history", response_model=list[ChatMessageResponse])
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    global _demo_chats
    _demo_chats = _load_demo_chats()
    db  = get_db()
    uid = current_user["sub"]

    # Try demo store first
    messages = _demo_chats.get(uid, [])
    
    if not messages:
        # Fallback to Firebase
        try:
            docs = list(
                db.collection("chats").document(uid)
                  .collection("messages")
                  .order_by("timestamp")
                  .limit(limit)
                  .stream()
            )

            for doc in docs:
                d = doc.to_dict()
                messages.append(ChatMessageResponse(
                    id=d.get("id"),
                    user_id=d.get("user_id", uid),
                    content=d.get("content", ""),
                    role=d.get("role", "user"),
                    sentiment_score=d.get("sentiment_score"),
                    sentiment_level=d.get("sentiment_level"),
                    timestamp=d.get("timestamp"),
                ))
        except Exception:
            pass
            
    return messages[:limit]


@router.delete("/history")
async def clear_history(current_user: dict = Depends(get_current_user)):
    global _demo_chats
    _demo_chats = _load_demo_chats()
    db  = get_db()
    uid = current_user["sub"]

    deleted_count = 0
    
    # Clear demo store
    if uid in _demo_chats:
        deleted_count = len(_demo_chats[uid])
        _demo_chats[uid] = []
        _save_demo_chats(_demo_chats)

    # Also try Firebase
    try:
        docs = list(
            db.collection("chats").document(uid)
              .collection("messages").stream()
        )
        for doc in docs:
            doc_ref = db.collection("chats").document(uid).collection("messages").document(doc.id)
            doc_ref.delete()
        deleted_count = max(deleted_count, len(docs))
    except Exception:
        pass

    return {"deleted": deleted_count, "message": "Chat history cleared"}
