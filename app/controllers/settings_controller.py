from app.models.setting_model import SettingModel

class SettingsController:
    @staticmethod
    def update_settings(redemption_pin: str = None, current_reward: str = None, cooldown_hours: str = None) -> dict:
        updated = {}
        if redemption_pin is not None:
            clean_pin = str(redemption_pin).strip()
            if len(clean_pin) == 4 and clean_pin.isdigit():
                SettingModel.set_value("redemption_pin", clean_pin)
                updated["redemption_pin"] = clean_pin
            else:
                return {"success": False, "message": "El PIN debe contener exactamente 4 dígitos numéricos."}

        if current_reward is not None:
            clean_reward = str(current_reward).strip()
            if len(clean_reward) > 0:
                SettingModel.set_value("current_reward", clean_reward)
                updated["current_reward"] = clean_reward

        if cooldown_hours is not None:
            try:
                hours = float(cooldown_hours)
                if hours > 0:
                    SettingModel.set_value("cooldown_hours", str(hours))
                    updated["cooldown_hours"] = str(hours)
            except ValueError:
                pass

        return {
            "success": True,
            "message": "Configuración actualizada con éxito.",
            "updated": updated,
            "all_settings": SettingModel.get_all()
        }
