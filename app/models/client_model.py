import uuid
from app.config.database import get_db_connection

class ClientModel:
    @staticmethod
    def create(name: str, whatsapp: str) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        client_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO clients (id, name, whatsapp, session_token) VALUES (?, ?, ?, ?)",
            (client_id, name, whatsapp, session_token)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_session_token(token: str) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE session_token = ?", (token,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_whatsapp(whatsapp: str) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE whatsapp = ?", (whatsapp,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_last_visit(client_id: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE clients SET last_visit_at = CURRENT_TIMESTAMP WHERE id = ?",
            (client_id,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT s.id) as total_stamps,
                   COUNT(DISTINCT r.id) as total_redemptions
            FROM clients c
            LEFT JOIN stamps s ON c.id = s.client_id
            LEFT JOIN redemptions r ON c.id = r.client_id
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
