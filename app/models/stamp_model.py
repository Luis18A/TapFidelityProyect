import uuid
from app.config.database import get_db_connection

class StampModel:
    @staticmethod
    def add_stamp(client_id: str, ip_address: str = None, device_hash: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        stamp_id = str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO stamps (id, client_id, ip_address, device_hash) VALUES (?, ?, ?, ?)",
            (stamp_id, client_id, ip_address, device_hash)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM stamps WHERE id = ?", (stamp_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_last_stamp(client_id: str) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM stamps WHERE client_id = ? ORDER BY created_at DESC LIMIT 1",
            (client_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def count_total_stamps(client_id: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM stamps WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()
        return row["count"] if row else 0

    @staticmethod
    def get_all_stamps():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stamps ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
