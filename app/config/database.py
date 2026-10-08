import sqlite3
import psycopg2
import psycopg2.extras
import bcrypt
from app.config.settings import settings

def is_postgres() -> bool:
    return bool(settings.DATABASE_URL and settings.DATABASE_URL.strip())

class PostgresCursorWrapper:
    """Wrapper for psycopg2 cursor to translate '?' parameter placeholders to '%s'."""
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query: str, vars=None):
        if "?" in query:
            query = query.replace("?", "%s")
        if vars is not None:
            return self.cursor.execute(query, vars)
        return self.cursor.execute(query)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __getattr__(self, name):
        return getattr(self.cursor, name)

class PostgresConnectionWrapper:
    """Wrapper for psycopg2 connection."""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return PostgresCursorWrapper(cursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()
        self._conn.close()

def get_db_connection():
    if is_postgres():
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        raw_conn = psycopg2.connect(db_url)
        return PostgresConnectionWrapper(raw_conn)
    else:
        conn = sqlite3.connect(settings.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla de Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        whatsapp TEXT UNIQUE NOT NULL,
        session_token TEXT UNIQUE NOT NULL,
        last_visit_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de Sellos / Visitas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stamps (
        id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL REFERENCES clients (id),
        ip_address TEXT,
        device_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de Canjes / Premios Reclamados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS redemptions (
        id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL REFERENCES clients (id),
        stamps_used INTEGER DEFAULT 5,
        reward_name TEXT NOT NULL,
        pin_verified INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de Usuarios Administradores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de Configuración (Key-Value)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insertar valores por defecto si no existen
    cursor.execute("INSERT INTO system_settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO NOTHING", ("redemption_pin", settings.DEFAULT_REDEMPTION_PIN))
    cursor.execute("INSERT INTO system_settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO NOTHING", ("current_reward", settings.DEFAULT_REWARD_NAME))
    cursor.execute("INSERT INTO system_settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO NOTHING", ("cooldown_hours", str(settings.DEFAULT_COOLDOWN_HOURS)))

    # Insertar administrador por defecto (admin / admin123)
    cursor.execute("SELECT id FROM admin_users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        hashed_pw = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("INSERT INTO admin_users (id, username, password_hash) VALUES (?, ?, ?)", ("admin-001", "admin", hashed_pw))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
