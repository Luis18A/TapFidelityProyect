from datetime import datetime, timezone
from app.models.stamp_model import StampModel
from app.models.setting_model import SettingModel

class AntiFraudService:
    @staticmethod
    def check_stamp_eligibility(client_id: str) -> tuple[bool, str, int]:
        """
        Verifica si el cliente puede sumar un sello según la regla antifraude de horas de enfriamiento.
        Retorna: (is_eligible, message, seconds_remaining)
        """
        cooldown_hours_str = SettingModel.get_value("cooldown_hours", "12")
        try:
            cooldown_hours = float(cooldown_hours_str)
        except ValueError:
            cooldown_hours = 12.0

        last_stamp = StampModel.get_last_stamp(client_id)
        if not last_stamp:
            return True, "Primer sello listo para asignar.", 0

        # SQLite timestamps are stored as 'YYYY-MM-DD HH:MM:SS' UTC
        raw_created_at = last_stamp["created_at"]
        try:
            last_stamp_dt = datetime.strptime(raw_created_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            # Fallback if format has T or milliseconds
            last_stamp_dt = datetime.fromisoformat(raw_created_at.replace("Z", "+00:00"))

        now_dt = datetime.now(timezone.utc)
        elapsed_seconds = (now_dt - last_stamp_dt).total_seconds()
        cooldown_seconds = cooldown_hours * 3600

        if elapsed_seconds < cooldown_seconds:
            seconds_remaining = int(cooldown_seconds - elapsed_seconds)
            hours_rem = seconds_remaining // 3600
            mins_rem = (seconds_remaining % 3600) // 60
            
            time_msg = f"{hours_rem}h {mins_rem}m" if hours_rem > 0 else f"{mins_rem} min"
            return False, f"Regla antifraude activa: debes esperar {time_msg} para sumar tu próximo sello.", seconds_remaining

        return True, "Elegible para sumar sello.", 0
