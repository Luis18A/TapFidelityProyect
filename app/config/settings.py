import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tengile_malamala_super_secret_jwt_key_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_PATH: str = os.getenv("DB_PATH", "fidelizacion.db")
    DEFAULT_REDEMPTION_PIN: str = "1234"
    DEFAULT_COOLDOWN_HOURS: int = 12
    DEFAULT_REWARD_NAME: str = "Café de Especialidad + 20% en tu próxima compra"

settings = Settings()

