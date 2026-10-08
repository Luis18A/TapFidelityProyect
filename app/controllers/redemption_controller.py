from app.models.client_model import ClientModel
from app.models.stamp_model import StampModel
from app.models.redemption_model import RedemptionModel
from app.models.setting_model import SettingModel

class RedemptionController:
    @staticmethod
    def redeem_reward(session_token: str, pin: str) -> dict:
        client = ClientModel.get_by_session_token(session_token)
        if not client:
            return {"success": False, "error": "CLIENT_NOT_FOUND", "message": "Sesión no válida."}

        client_id = client["id"]

        # Check active stamps balance
        total_stamps = StampModel.count_total_stamps(client_id)
        total_redemptions = RedemptionModel.count_redemptions(client_id)
        active_stamps = max(0, total_stamps - (total_redemptions * 5))

        if active_stamps < 5:
            return {
                "success": False,
                "error": "INSUFFICIENT_STAMPS",
                "message": f"Necesitas 5 sellos para canjear tu premio. Tienes {active_stamps} sellos."
            }

        # Verify 4-digit PIN
        valid_pin = SettingModel.get_value("redemption_pin", "1234")
        if str(pin).strip() != str(valid_pin).strip():
            return {
                "success": False,
                "error": "INVALID_PIN",
                "message": "El PIN de validación es incorrecto. Pídele al encargado que lo ingrese."
            }

        reward_name = SettingModel.get_value("current_reward", "Premio Especial")

        # Process redemption
        redemption = RedemptionModel.create_redemption(client_id, reward_name, stamps_used=5)

        new_active_stamps = active_stamps - 5

        return {
            "success": True,
            "message": "¡Premio canjeado con éxito! Muestra esta pantalla al encargado.",
            "reward_name": reward_name,
            "redemption": redemption,
            "active_stamps": new_active_stamps
        }
