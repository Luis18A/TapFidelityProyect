from app.models.client_model import ClientModel
from app.models.stamp_model import StampModel
from app.models.redemption_model import RedemptionModel
from app.models.setting_model import SettingModel
from app.services.anti_fraud_service import AntiFraudService

class ClientController:
    @staticmethod
    def get_account_status(session_token: str) -> dict:
        client = ClientModel.get_by_session_token(session_token)
        if not client:
            return {"authenticated": False, "client": None}

        client_id = client["id"]
        total_stamps = StampModel.count_total_stamps(client_id)
        total_redemptions = RedemptionModel.count_redemptions(client_id)
        active_stamps = total_stamps - (total_redemptions * 5)
        if active_stamps < 0:
            active_stamps = 0

        can_redeem = active_stamps >= 5
        reward_name = SettingModel.get_value("current_reward", "Premio Especial")
        
        # Check antifraud status
        is_eligible, cooldown_msg, seconds_remaining = AntiFraudService.check_stamp_eligibility(client_id)

        return {
            "authenticated": True,
            "client": {
                "id": client["id"],
                "name": client["name"],
                "whatsapp": client["whatsapp"],
                "session_token": client["session_token"]
            },
            "card_status": {
                "total_stamps": total_stamps,
                "active_stamps": active_stamps,
                "total_redemptions": total_redemptions,
                "can_redeem": can_redeem,
                "reward_name": reward_name,
                "cooldown": {
                    "is_eligible": is_eligible,
                    "message": cooldown_msg,
                    "seconds_remaining": seconds_remaining
                }
            }
        }

    @staticmethod
    def register(name: str, whatsapp: str) -> dict:
        clean_name = name.strip()
        clean_wa = whatsapp.strip().replace(" ", "").replace("-", "")

        existing = ClientModel.get_by_whatsapp(clean_wa)
        if existing:
            return {
                "success": True,
                "is_new": False,
                "client": existing,
                "message": "Bienvenido de vuelta. Recuperamos tu sesión."
            }

        new_client = ClientModel.create(clean_name, clean_wa)
        return {
            "success": True,
            "is_new": True,
            "client": new_client,
            "message": "¡Registro exitoso! Tu tarjeta digital ha sido activada."
        }
