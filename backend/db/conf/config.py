import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

DB_TYPE = os.getenv('DB_TYPE', 'mysql')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'news_db')
DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')

def get_db_config():
    if DB_TYPE == 'mysql':
        return {
            'type': 'mysql',
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': DB_NAME,
            'charset': DB_CHARSET
        }
    else:
        raise ValueError(f"不支持的数据库类型: {DB_TYPE}")