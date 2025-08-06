#!/usr/bin/env python3
"""
PDF2Image API 主启动文件
使用绝对导入避免相对导入错误
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
    print(f"存储模式: {config.OUTPUT_STORAGE_TYPE}")
    print(f"输出目录: {config.OUTPUT_DIR}")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info" if not config.DEBUG else "debug",
        access_log=True
    )