# ============================================================
# FILE: python/fraud_engine.py
# ============================================================

from db_connect import get_connection, close_connection
from mysql.connector import Error
from datetime import datetime


def get_all_alerts():
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vw_fraud_report")
        return cursor.fetchall()
    except Error as e:
        print(f"[!] Error fetching alerts: {e}")
        return []
    finally:
        close_connection(conn, cursor)


def get_high_risk_alerts(min_score=70):
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM vw_fraud_report WHERE risk_score >= %s", (min_score,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[!] Error fetching high-risk alerts: {e}")
        return []
    finally:
        close_connection(conn, cursor)


def get_rule_summary():
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vw_rule_summary")
        return cursor.fetchall()
    except Error as e:
        print(f"[!] Error fetching rule summary: {e}")
        return []
    finally:
        close_connection(conn, cursor)


def get_user_fraud_summary():
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vw_user_fraud_summary")
        return cursor.fetchall()
    except Error as e:
        print(f"[!] Error fetching user summary: {e}")
        return []
    finally:
        close_connection(conn, cursor)


def python_risk_score(user_id, amount, location, txn_time=None):
    if txn_time is None:
        txn_time = datetime.now()
    score = 0
    rules = []
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT country FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"score": 0, "rules": ["USER_NOT_FOUND"]}

        if amount > 50000:
            score += 40
            rules.append("HIGH_AMOUNT")

        if user["country"].lower() not in location.lower():
            score += 30
            rules.append("LOCATION_MISMATCH")

        if 1 <= txn_time.hour <= 5:
            score += 15
            rules.append("ODD_HOURS")

        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM transactions
            WHERE user_id = %s
              AND txn_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
        """, (user_id,))
        row = cursor.fetchone()
        if row and row["cnt"] >= 3:
            score += 35
            rules.append("VELOCITY")

        return {"score": score, "rules": rules}
    except Error as e:
        print(f"[!] Python scoring error: {e}")
        return {"score": 0, "rules": []}
    finally:
        close_connection(conn, cursor)


def mark_alert_reviewed(alert_id):
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE fraud_alerts SET reviewed = 1 WHERE alert_id = %s", (alert_id,)
        )
        conn.commit()
        print(f"  [OK] Alert {alert_id} marked as reviewed.")
    except Error as e:
        print(f"  [!] Error: {e}")
        if conn:
            conn.rollback()
    finally:
        close_connection(conn, cursor)
