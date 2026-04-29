import pymysql
import logging
from pathlib import Path
from contextlib import contextmanager
from db.conf.config import get_db_config

logger = logging.getLogger(__name__)

def get_db_connection():
    db_config = get_db_config()
    return pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset=db_config['charset']
    )

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_sql_file_path(filename: str) -> Path:
    return Path(__file__).resolve().parent.parent / 'sql' / filename

def execute_sql_file(conn, filename: str):
    sql_path = get_sql_file_path(filename)
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    cursor = conn.cursor()
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    conn.commit()
    cursor.close()

def init_log_exists(conn) -> bool:
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES LIKE 'init_log'")
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        return False
    finally:
        cursor.close()

def is_file_initialized(conn, filename: str) -> bool:
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM init_log WHERE init_key = %s', (filename,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        return False
    finally:
        cursor.close()

def mark_file_initialized(conn, filename: str):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO init_log (init_key) VALUES (%s)', (filename,))
    conn.commit()
    cursor.close()

async def run_initialization():
    print("[初始化] 开始项目初始化...")

    schema_file = 'schema.sql'
    data_file = 'init_data.sql'

    conn = get_db_connection()
    try:
        if not init_log_exists(conn):
            execute_sql_file(conn, schema_file)
            mark_file_initialized(conn, schema_file)
            print(f"[初始化] {schema_file} 执行完成")
        else:
            if is_file_initialized(conn, schema_file):
                print(f"[初始化] {schema_file} 已执行过，跳过")
            else:
                print(f"[初始化] 执行 {schema_file}...")
                execute_sql_file(conn, schema_file)
                mark_file_initialized(conn, schema_file)
                print(f"[初始化] {schema_file} 执行完成")

        if is_file_initialized(conn, data_file):
            print(f"[初始化] {data_file} 已执行过，跳过")
        else:
            execute_sql_file(conn, data_file)
            mark_file_initialized(conn, data_file)
            print(f"[初始化] {data_file} 执行完成")
    finally:
        conn.close()

    print("[初始化] 项目初始化完成!")