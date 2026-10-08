from datetime import datetime, timezone, timedelta
import jwt
from app.models.admin_model import AdminModel
from app.models.client_model import ClientModel
from app.models.redemption_model import RedemptionModel
from app.models.setting_model import SettingModel
from app.services.analytics_service import AnalyticsService
from app.config.settings import settings

class AdminController:
    @staticmethod
    def login(username: str, password: str) -> dict:
        admin = AdminModel.get_by_username(username.strip())
        if not admin or not AdminModel.verify_password(password.strip(), admin["password_hash"]):
            return {"success": False, "message": "Usuario o contraseña incorrectos"}

        payload = {
            "sub": admin["username"],
            "admin_id": admin["id"],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return {
            "success": True,
            "token": token,
            "username": admin["username"],
            "message": "Autenticación exitosa"
        }

    @staticmethod
    def get_dashboard_data() -> dict:
        metrics = AnalyticsService.get_dashboard_metrics()
        clients = ClientModel.get_all()
        redemptions = RedemptionModel.get_all_redemptions()
        all_settings = SettingModel.get_all()

        return {
            "success": True,
            "metrics": metrics,
            "clients": clients,
            "recent_redemptions": redemptions[:10],
            "settings": all_settings
        }
