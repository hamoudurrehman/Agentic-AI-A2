"""Authentication and Onboarding Router."""
from fastapi import APIRouter, HTTPException
from ..schemas.api_models import UserLoginRequest, UserProfileResponse
from ..auth.token_store import token_store_instance
from gigbid.mcp_servers.marketplace.server import get_adapter

router = APIRouter(prefix="/auth", tags=["auth"])

CURRENT_SESSION = {
    "user_id": "usr_reviewer_01",
    "username": "Reviewer",
    "persona_id": "persona_aiml",
    "active_profile": "open",
    "hourly_rate": 95.0,
    "weekly_connects_budget": 120
}

@router.post("/login", response_model=UserProfileResponse)
def login(req: UserLoginRequest):
    CURRENT_SESSION["username"] = req.username
    if req.persona_id:
        CURRENT_SESSION["persona_id"] = req.persona_id
    token_store_instance.store_token(CURRENT_SESSION["user_id"], "simulated_oauth_access_token")
    
    bal = get_adapter().get_connects_balance(CURRENT_SESSION["user_id"])
    return UserProfileResponse(
        user_id=CURRENT_SESSION["user_id"],
        username=CURRENT_SESSION["username"],
        persona_id=CURRENT_SESSION["persona_id"],
        active_profile=CURRENT_SESSION["active_profile"],
        connects_balance=bal,
        hourly_rate=CURRENT_SESSION["hourly_rate"],
        weekly_connects_budget=CURRENT_SESSION["weekly_connects_budget"]
    )

@router.get("/me", response_model=UserProfileResponse)
def get_current_user():
    bal = get_adapter().get_connects_balance(CURRENT_SESSION["user_id"])
    return UserProfileResponse(
        user_id=CURRENT_SESSION["user_id"],
        username=CURRENT_SESSION["username"],
        persona_id=CURRENT_SESSION["persona_id"],
        active_profile=CURRENT_SESSION["active_profile"],
        connects_balance=bal,
        hourly_rate=CURRENT_SESSION["hourly_rate"],
        weekly_connects_budget=CURRENT_SESSION["weekly_connects_budget"]
    )

@router.post("/switch-persona")
def switch_persona(persona_id: str):
    CURRENT_SESSION["persona_id"] = persona_id
    return {"status": "success", "active_persona": persona_id}
