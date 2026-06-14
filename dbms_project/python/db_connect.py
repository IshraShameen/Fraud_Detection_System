# ============================================================
# FILE: python/db_connect.py
# ============================================================

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "Ishra9390",       # your MySQL password
    "database": "dbms_project"     # database name
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"[DB ERROR] Could not connect: {e}")
        raise

def close_connection(conn, cursor=None):
    if cursor:
        cursor.close()
    if conn and conn.is_connected():
        conn.close()
