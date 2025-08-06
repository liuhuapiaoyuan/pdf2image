#!/usr/bin/env python3
"""
PDF2Image API 服务启动脚本 - 兼容性版本
建议使用 app.py 作为主启动文件
"""
import sys
import os
from pathlib import Path

# 将当前目录添加到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import uvicorn
from main import app
from config import config

if __name__ == "__main__":
    print(f"启动PDF2Image API服务...")
    print(f"服务地址: http://{config.HOST}:{config.PORT}")
    print(f"文档地址: http://{config.HOST}:{config.PORT}/docs")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info" if not config.DEBUG else "debug",
        access_log=True
    )