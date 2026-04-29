import os
import sys

# 添加 libs 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))
sys.path.insert(0, os.path.dirname(__file__))

from api import app
from db.conf.init import run_initialization

if __name__ == '__main__':
    import uvicorn
    import asyncio
    
    # 先执行初始化
    print("执行初始化...")
    asyncio.run(run_initialization())
    
    print("启动服务...")
    uvicorn.run(app, host='0.0.0.0', port=8000)