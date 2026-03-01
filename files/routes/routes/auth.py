"""
Auth routes
POST /api/auth/login        → user login (only registered accounts)
POST /api/auth/signup       → new user signup
POST /api/auth/admin-login  → admin login with access code
POST /api/auth/social       → social provider login (Google only)
GET  /api/auth/me           → get current user profile
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from utils import create_token, get_current_user, ADMIN_CODE

router = APIRouter()

# ─── IN-MEMORY USER STORE ─────────────────────────────────────────────────────
# { email: { name, email, password, role, isAdmin } }
_users: dict = {}

# ─── MODELS ───────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "creator"

class AdminLoginRequest(BaseModel):
    email: str
    password: str
    accessCode: str

class SocialLoginRequest(BaseModel):
    provider: str  # "Google"

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@router.post("/login")
def login(body: LoginRequest):
    """User login — only registered accounts can login."""
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    email = body.email.strip().lower()

    if email not in _users:
        raise HTTPException(status_code=401, detail="No account found with this email. Please sign up first.")

    stored = _users[email]
    if stored["password"] != body.password:
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")

    user = {"name": stored["name"], "email": stored["email"], "role": stored["role"], "isAdmin": stored["isAdmin"]}
    token = create_token(user)
    return {"token": token, "user": user}


@router.post("/signup")
def signup(body: SignupRequest):
    """New user registration — creates a real account."""
    if not body.name.strip() or not body.email.strip() or not body.password:
        raise HTTPException(status_code=400, detail="Name, email and password are all required.")

    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    email = body.email.strip().lower()

    if email in _users:
        raise HTTPException(status_code=409, detail="An account with this email already exists. Please login instead.")

    _users[email] = {
        "name":     body.name.strip(),
        "email":    email,
        "password": body.password,
        "role":     body.role or "creator",
        "isAdmin":  False,
    }

    user = {"name": _users[email]["name"], "email": email, "role": _users[email]["role"], "isAdmin": False}
    token = create_token(user)
    return {"token": token, "user": user}


@router.post("/admin-login")
def admin_login(body: AdminLoginRequest):
    """Admin login — requires special access code."""
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="Credentials required.")
    if body.accessCode != ADMIN_CODE:
        raise HTTPException(status_code=403, detail=f"Invalid access code. Use {ADMIN_CODE} for demo.")

    user = {"name": "Admin User", "email": body.email, "role": "admin", "isAdmin": True}
    token = create_token(user)
    return {"token": token, "user": user}


@router.post("/social")
def social_login(body: SocialLoginRequest):
    """Google social login simulation."""
    import time
    fake_email = f"{body.provider.lower()}user_{int(time.time())}@{body.provider.lower()}.com"
    user = {"name": f"{body.provider} User", "email": fake_email, "role": "creator", "isAdmin": False}
    token = create_token(user)
    return {"token": token, "user": user}


@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return user
