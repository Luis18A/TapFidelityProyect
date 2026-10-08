from app.models.client_model import ClientModel
from app.models.stamp_model import StampModel
from app.models.redemption_model import RedemptionModel
from app.services.anti_fraud_service import AntiFraudService

class StampController:
    @staticmethod
    def claim_stamp(session_token: str, ip_address: str = None, device_hash: str = None) -> dict:
        client = ClientModel.get_by_session_token(session_token)
        if not client:
            return {"success": False, "error": "CLIENT_NOT_FOUND", "message": "Sesión no válida o cliente no registrado."}

        client_id = client["id"]

        # Antifraud check: 12h cooldown
        is_eligible, message, seconds_remaining = AntiFraudService.check_stamp_eligibility(client_id)
        if not is_eligible:
            return {
                "success": False,
                "error": "COOLDOWN_ACTIVE",
                "message": message,
                "seconds_remaining": seconds_remaining
            }

        # Add stamp
        stamp = StampModel.add_stamp(client_id, ip_address, device_hash)
        ClientModel.update_last_visit(client_id)

        # Recalculate balances
        total_stamps = StampModel.count_total_stamps(client_id)
        total_redemptions = RedemptionModel.count_redemptions(client_id)
        active_stamps = max(0, total_stamps - (total_redemptions * 5))

        return {
            "success": True,
            "message": "¡Sello agregado con éxito! Gracias por tu visita.",
            "stamp": stamp,
            "active_stamps": active_stamps,
            "can_redeem": active_stamps >= 5
        }
