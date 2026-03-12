from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import uuid

from models import UserRegister, UserLogin, TokenResponse, UserResponse
from auth_utils import hash_password, verify_password, create_access_token, get_current_user
from database import get_db

import json
import os

router = APIRouter()

# Simple file-based user store for demo mode
DEMO_USERS_FILE = "demo_users.json"

def _load_demo_users():
    if os.path.exists(DEMO_USERS_FILE):
        try:
            with open(DEMO_USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_demo_users(users):
    try:
        with open(DEMO_USERS_FILE, "w") as f:
            json.dump(users, f)
    except Exception:
        pass

_demo_users = _load_demo_users()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    global _demo_users
    _demo_users = _load_demo_users()

    email_lower = payload.email.lower().strip()

    # Check duplicate in demo store
    for u in _demo_users.values():
        if u.get("email", "").lower().strip() == email_lower:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    uid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    user_data = {
        "uid":          uid,
        "email":        email_lower, # Save in lowercase for consistency
        "display_name": payload.display_name or "Anonymous",
        "password":     hash_password(payload.password),
        "created_at":   now,
    }

    # Save to demo store
    _demo_users[uid] = user_data
    _save_demo_users(_demo_users)

    # Also try saving to Firebase (if connected)
    try:
        db = get_db()
        db.collection("users").document(uid).set(user_data)
    except Exception:
        pass

    token = create_access_token({"sub": uid, "email": email_lower})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            uid=uid,
            email=email_lower,
            display_name=user_data["display_name"],
            created_at=now,
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    global _demo_users
    _demo_users = _load_demo_users()

    email_lower = payload.email.lower().strip()
    found_user = None
    
    # Search in demo store
    for u in _demo_users.values():
        if u.get("email", "").lower().strip() == email_lower:
            found_user = u
            break

    # Search in Firebase if not found
    if not found_user:
        try:
            db = get_db()
            for doc in db.collection("users").stream():
                u = doc.to_dict()
                if u.get("email", "").lower().strip() == email_lower:
                    found_user = u
                    break
        except Exception:
            pass

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found. Please sign up first."
        )

    # Verify password
    if not verify_password(payload.password, found_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again."
        )

    token = create_access_token({"sub": found_user["uid"], "email": found_user["email"]})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            uid=found_user["uid"],
            email=found_user["email"],
            display_name=found_user.get("display_name", "Anonymous"),
            created_at=found_user.get("created_at"),
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    global _demo_users
    _demo_users = _load_demo_users()
    uid = current_user["sub"]

    user = _demo_users.get(uid)

    if not user:
        try:
            db = get_db()
            doc = db.collection("users").document(uid).get()
            if doc.exists:
                user = doc.to_dict()
        except Exception:
            pass

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        uid=user["uid"],
        email=user["email"],
        display_name=user.get("display_name", "Anonymous"),
        created_at=user.get("created_at"),
    )
