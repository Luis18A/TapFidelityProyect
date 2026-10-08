from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
from typing import Optional
from app.controllers.client_controller import ClientController
from app.controllers.stamp_controller import StampController
from app.controllers.redemption_controller import RedemptionController

router = APIRouter(prefix="/api/client", tags=["Client PWA"])

class RegisterSchema(BaseModel):
    name: str
    whatsapp: str

class RedeemSchema(BaseModel):
    session_token: str
    pin: str

class StampSchema(BaseModel):
    session_token: str

@router.get("/status")
def get_status(authorization: Optional[str] = Header(None)):
    token = None
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
    return ClientController.get_account_status(token)

@router.post("/register")
def register_client(data: RegisterSchema):
    return ClientController.register(data.name, data.whatsapp)

@router.post("/stamp")
def add_stamp(data: StampSchema, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    return StampController.claim_stamp(data.session_token, ip_address=client_ip, device_hash=user_agent)

@router.post("/redeem")
def redeem_reward(data: RedeemSchema):
    return RedemptionController.redeem_reward(data.session_token, data.pin)
