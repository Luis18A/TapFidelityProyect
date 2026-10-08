from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.controllers.admin_controller import AdminController
from app.controllers.settings_controller import SettingsController
from app.middlewares.auth_middleware import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

class AdminLoginSchema(BaseModel):
    username: str
    password: str

class SettingsUpdateSchema(BaseModel):
    redemption_pin: Optional[str] = None
    current_reward: Optional[str] = None
    cooldown_hours: Optional[str] = None

@router.post("/login")
def login(data: AdminLoginSchema):
    return AdminController.login(data.username, data.password)

@router.get("/dashboard", dependencies=[Depends(get_current_admin)])
def get_dashboard():
    return AdminController.get_dashboard_data()

@router.put("/settings", dependencies=[Depends(get_current_admin)])
def update_settings(data: SettingsUpdateSchema):
    return SettingsController.update_settings(
        redemption_pin=data.redemption_pin,
        current_reward=data.current_reward,
        cooldown_hours=data.cooldown_hours
    )
