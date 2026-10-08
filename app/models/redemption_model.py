import uuid
from app.config.database import get_db_connection

class RedemptionModel:
    @staticmethod
    def create_redemption(client_id: str, reward_name: str, stamps_used: int = 5) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        redemption_id = str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO redemptions (id, client_id, stamps_used, reward_name) VALUES (?, ?, ?, ?)",
            (redemption_id, client_id, stamps_used, reward_name)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM redemptions WHERE id = ?", (redemption_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def count_redemptions(client_id: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM redemptions WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()
        return row["count"] if row else 0

    @staticmethod
    def get_all_redemptions():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, c.name as client_name, c.whatsapp as client_whatsapp
            FROM redemptions r
            JOIN clients c ON r.client_id = c.id
            ORDER BY r.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
