from app.config.database import get_db_connection, is_postgres

class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics() -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total Clientes
        cursor.execute("SELECT COUNT(*) as count FROM clients")
        total_clients = cursor.fetchone()["count"]

        # Visitas Hoy (Sellos emitidos en la fecha actual UTC)
        if is_postgres():
            cursor.execute("SELECT COUNT(*) as count FROM stamps WHERE DATE(created_at) = CURRENT_DATE")
        else:
            cursor.execute("SELECT COUNT(*) as count FROM stamps WHERE DATE(created_at) = DATE('now')")
        visits_today = cursor.fetchone()["count"]

        # Visitas Esta Semana
        if is_postgres():
            cursor.execute("SELECT COUNT(*) as count FROM stamps WHERE created_at >= (CURRENT_DATE - INTERVAL '7 days')")
        else:
            cursor.execute("SELECT COUNT(*) as count FROM stamps WHERE created_at >= DATE('now', '-7 days')")
        visits_this_week = cursor.fetchone()["count"]

        # Total Sellos Emitidos
        cursor.execute("SELECT COUNT(*) as count FROM stamps")
        total_stamps = cursor.fetchone()["count"]

        # Total Canjes Realizados
        cursor.execute("SELECT COUNT(*) as count FROM redemptions")
        total_redemptions = cursor.fetchone()["count"]

        # Clientes Recurrentes (Clientes con al menos 2 visitas)
        cursor.execute("""
            SELECT COUNT(*) as count FROM (
                SELECT client_id FROM stamps GROUP BY client_id HAVING COUNT(id) >= 2
            ) AS subquery
        """)
        recurrent_clients = cursor.fetchone()["count"]

        # Tasa de Retención (%)
        retention_rate = round((recurrent_clients / total_clients * 100), 1) if total_clients > 0 else 0.0

        # Tasa de Canje (%)
        potential_redemptions = total_stamps // 5
        redemption_rate = round((total_redemptions / potential_redemptions * 100), 1) if potential_redemptions > 0 else 0.0

        conn.close()

        return {
            "total_clients": total_clients,
            "visits_today": visits_today,
            "visits_this_week": visits_this_week,
            "total_stamps": total_stamps,
            "total_redemptions": total_redemptions,
            "recurrent_clients": recurrent_clients,
            "retention_rate": retention_rate,
            "redemption_rate": redemption_rate
        }
