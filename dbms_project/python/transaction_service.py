# ============================================================
# FILE: python/transaction_service.py
# Fraud scoring done in Python after insert (no trigger needed)
# ============================================================

from db_connect import get_connection, close_connection
from mysql.connector import Error
from datetime import datetime

def insert_transaction(user_id, amount, merchant, location, ip_address=None):
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO transactions (user_id, amount, merchant, location, ip_address)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, amount, merchant, location, ip_address))
        conn.commit()
        txn_id = cursor.lastrowid
        print(f"  [+] Inserted txn_id={txn_id}  Rs.{amount}  user={user_id}")

        # Score fraud in Python right after insert
        _score_and_update(txn_id, user_id, amount, location, ip_address)
        return txn_id
    except Error as e:
        print(f"  [!] Insert failed: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        close_connection(conn, cursor)


def _score_and_update(txn_id, user_id, amount, location, ip_address):
    """Score the transaction and update status + alerts."""
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user country
        cursor.execute("SELECT country FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return

        user_country = user["country"]
        risk_score   = 0
        rules_fired  = []
        now          = datetime.now()

        # Get thresholds from fraud_rules table
        cursor.execute("SELECT threshold FROM fraud_rules WHERE rule_name='HIGH_AMOUNT' AND is_active=1")
        row = cursor.fetchone()
        high_threshold = float(row["threshold"]) if row else 50000

        cursor.execute("SELECT threshold FROM fraud_rules WHERE rule_name='VELOCITY' AND is_active=1")
        row = cursor.fetchone()
        velocity_limit = int(row["threshold"]) if row else 3

        # RULE 1: HIGH AMOUNT
        if amount > high_threshold:
            risk_score += 40
            rules_fired.append("HIGH_AMOUNT")

        # RULE 2: VELOCITY - more than N txns in 10 mins
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM transactions
            WHERE user_id = %s
              AND txn_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
              AND txn_id != %s
        """, (user_id, txn_id))
        cnt = cursor.fetchone()["cnt"]
        if cnt >= velocity_limit:
            risk_score += 35
            rules_fired.append("VELOCITY")

        # RULE 3: LOCATION MISMATCH
        if user_country.lower() not in location.lower():
            risk_score += 30
            rules_fired.append("LOCATION_MISMATCH")

        # RULE 4: ODD HOURS (1 AM - 5 AM)
        if 1 <= now.hour <= 5:
            risk_score += 15
            rules_fired.append("ODD_HOURS")

        # RULE 5: RAPID REPEAT - same amount in last 60 seconds
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM transactions
            WHERE user_id = %s
              AND amount   = %s
              AND txn_time >= DATE_SUB(NOW(), INTERVAL 60 SECOND)
              AND txn_id  != %s
        """, (user_id, amount, txn_id))
        repeat = cursor.fetchone()["cnt"]
        if repeat >= 1:
            risk_score += 25
            rules_fired.append("RAPID_REPEAT")

        # Update status
        if risk_score > 0:
            rules_str = " ".join(rules_fired)
            cursor.execute(
                "UPDATE transactions SET status='blocked' WHERE txn_id=%s", (txn_id,))
            cursor.execute(
                "INSERT INTO fraud_alerts (txn_id, rule_triggered, risk_score) VALUES (%s,%s,%s)",
                (txn_id, rules_str, risk_score))
            cursor.execute(
                "INSERT INTO audit_log (action, table_affected, record_id, details) VALUES (%s,%s,%s,%s)",
                ("FRAUD_FLAGGED", "transactions", txn_id,
                 f"Risk score: {risk_score} | Rules: {rules_str}"))
            print(f"  [BLOCKED] Rules: {rules_str}  Score: {risk_score}")
        else:
            cursor.execute(
                "UPDATE transactions SET status='approved' WHERE txn_id=%s", (txn_id,))
            cursor.execute(
                "INSERT INTO audit_log (action, table_affected, record_id, details) VALUES (%s,%s,%s,%s)",
                ("TXN_APPROVED", "transactions", txn_id, "No fraud rules triggered"))
            print(f"  [APPROVED]")

        conn.commit()
    except Error as e:
        print(f"  [!] Scoring error: {e}")
        if conn:
            conn.rollback()
    finally:
        close_connection(conn, cursor)


def get_transaction_status(txn_id):
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT txn_id, amount, status, merchant, location FROM transactions WHERE txn_id=%s",
            (txn_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"  [!] Status fetch failed: {e}")
        return None
    finally:
        close_connection(conn, cursor)


def update_transaction_status(txn_id, new_status):
    conn = cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET status=%s WHERE txn_id=%s", (new_status, txn_id))
        conn.commit()
        print(f"  [OK] Transaction {txn_id} updated to '{new_status}'")
    except Error as e:
        print(f"  [!] Update failed: {e}")
        if conn:
            conn.rollback()
    finally:
        close_connection(conn, cursor)
