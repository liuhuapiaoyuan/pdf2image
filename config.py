import os
from pathlib import Path
from typing import Optional


class Config:
    """应用配置类"""
    
    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 文件存储配置
    OUTPUT_STORAGE_TYPE: str = os.getenv("OUTPUT_STORAGE_TYPE", "file")  # base64, file, both
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/tmp/pdf2image_output")
    OUTPUT_BASE_URL: str = os.getenv("OUTPUT_BASE_URL", "http://localhost:8000/files")
    
    # PDF处理配置
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    DEFAULT_DPI: int = int(os.getenv("DEFAULT_DPI", "200"))
    DEFAULT_FORMAT: str = os.getenv("DEFAULT_FORMAT", "png")
    MAX_THREAD_COUNT: int = int(os.getenv("MAX_THREAD_COUNT", "8"))
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "600"))
    
    # 安全配置
    ALLOWED_EXTENSIONS: list = ["pdf"]
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Poppler配置
    POPPLER_PATH: Optional[str] = os.getenv("POPPLER_PATH")
    
    # 缓存配置
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1小时
    
    @classmethod
    def ensure_output_dir(cls) -> Path:
        """确保输出目录存在"""
        output_path = Path(cls.OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    @classmethod
    def get_file_url(cls, filename: str) -> str:
        """获取文件访问URL"""
        return f"{cls.OUTPUT_BASE_URL.rstrip('/')}/{filename}"


# 全局配置实例
config = Config()