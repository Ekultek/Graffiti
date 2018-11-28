import os
import sqlite3


import lib.settings


def initialize(memory=False):
    """
    initialize the database either in memory or by the db file
    """
    if memory:
        print("initializing database in memory")
        conn = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
        return conn.cursor()
    else:
        if not os.path.exists(lib.settings.DATABASE_PATH):
            cursor = sqlite3.connect(lib.settings.DATABASE_PATH)
            cursor.execute(
                'CREATE TABLE "cached_payloads" ('
                '`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                '`payload` TEXT NOT NULL,'
                '`payload_type` TEXT NOT NULL,'
                '`exec_type` TEXT NOT NULL'
                ')'
            )
        conn = sqlite3.connect(lib.settings.DATABASE_PATH, isolation_level=None, check_same_thread=False)
        return conn.cursor()


def fetch_cached_payloads(cursor):
    """
    fetch cached payloads from the database
    """
    try:
        payloads = cursor.execute("SELECT * FROM cached_payloads")
        return payloads.fetchall()
    except Exception:
        return []


def insert_payload(payload, script_type, exec_type, cursor):
    """
    insert a payload into the database
    """
    try:
        cached = False
        current_cache = fetch_cached_payloads(cursor)
        id_number = len(current_cache) + 1
        for item in current_cache:
            _, cached_payload, _, _ = item
            if payload == cached_payload:
                cached = True
        if not cached:
            cursor.execute(
                "INSERT INTO cached_payloads (id,payload,payload_type,exec_type) VALUES (?,?,?,?)", (
                    id_number, payload, script_type, exec_type
                )
            )
    except Exception:
        return False
    return True
