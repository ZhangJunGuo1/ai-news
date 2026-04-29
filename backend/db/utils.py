import logging
from db.conf.init import get_db

logger = logging.getLogger(__name__)

def execute_query(query: str, params: tuple = None):
    with get_db() as conn:
        cursor = conn.cursor()
        logger.debug(f"SQL: {query} | Params: {params}")
        cursor.execute(query, params or ())
        return cursor.fetchall()

def execute_query_one(query: str, params: tuple = None):
    with get_db() as conn:
        cursor = conn.cursor()
        logger.debug(f"SQL: {query} | Params: {params}")
        cursor.execute(query, params or ())
        return cursor.fetchone()

def execute_insert(query: str, params: tuple = None):
    with get_db() as conn:
        cursor = conn.cursor()
        logger.debug(f"SQL: {query} | Params: {params}")
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid

def execute_update(query: str, params: tuple = None):
    with get_db() as conn:
        cursor = conn.cursor()
        logger.debug(f"SQL: {query} | Params: {params}")
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount

def execute_delete(query: str, params: tuple = None):
    with get_db() as conn:
        cursor = conn.cursor()
        logger.debug(f"SQL: {query} | Params: {params}")
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount

def execute_query_with_conn(conn, query: str, params: tuple = None):
    cursor = conn.cursor()
    logger.debug(f"SQL: {query} | Params: {params}")
    cursor.execute(query, params or ())
    return cursor.fetchall()

def execute_query_one_with_conn(conn, query: str, params: tuple = None):
    cursor = conn.cursor()
    logger.debug(f"SQL: {query} | Params: {params}")
    cursor.execute(query, params or ())
    return cursor.fetchone()

def execute_insert_with_conn(conn, query: str, params: tuple = None):
    cursor = conn.cursor()
    logger.debug(f"SQL: {query} | Params: {params}")
    cursor.execute(query, params or ())
    return cursor.lastrowid

def execute_update_with_conn(conn, query: str, params: tuple = None):
    cursor = conn.cursor()
    logger.debug(f"SQL: {query} | Params: {params}")
    cursor.execute(query, params or ())
    return cursor.rowcount

def execute_delete_with_conn(conn, query: str, params: tuple = None):
    cursor = conn.cursor()
    logger.debug(f"SQL: {query} | Params: {params}")
    cursor.execute(query, params or ())
    return cursor.rowcount
