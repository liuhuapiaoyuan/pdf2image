from typing import Optional, List, Literal, Union
from pydantic import BaseModel, Field, HttpUrl


class ConversionRequest(BaseModel):
    """PDF转换请求参数"""
    dpi: int = Field(default=200, ge=50, le=600, description="输出图片DPI，范围50-600")
    first_page: Optional[int] = Field(default=None, ge=1, description="起始页码（从1开始）")
    last_page: Optional[int] = Field(default=None, ge=1, description="结束页码")
    fmt: Literal["jpeg", "png", "ppm", "tiff"] = Field(default="png", description="输出图片格式")
    grayscale: bool = Field(default=False, description="是否转换为灰度图")
    transparent: bool = Field(default=False, description="是否保持透明背景（仅PNG支持）")
    thread_count: int = Field(default=1, ge=1, le=8, description="线程数，范围1-8")
    use_pdftocairo: bool = Field(default=False, description="是否使用pdftocairo引擎")
    timeout: int = Field(default=600, ge=30, le=1800, description="超时时间（秒），范围30-1800")
    size: Optional[int] = Field(default=None, ge=100, le=4000, description="输出图片大小（保持宽高比）")
    jpegopt: Optional[dict] = Field(default=None, description="JPEG压缩选项")
    storage_type: Literal["base64", "file", "both"] = Field(default="base64", description="存储类型：base64编码、文件存储或两者都有")
    image_mode: Literal["base64", "path"] = Field(default="base64", description="返回图片模式：base64编码或文件路径")
    
    class Config:
        schema_extra = {
            "example": {
                "dpi": 200,
                "first_page": 1,
                "last_page": 5,
                "fmt": "png",
                "grayscale": False,
                "transparent": True,
                "thread_count": 2,
                "use_pdftocairo": False,
                "timeout": 600,
                "size": 800,
                "storage_type": "base64",
                "image_mode": "base64"
            }
        }


class URLConversionRequest(BaseModel):
    """URL PDF转换请求参数"""
    pdf_url: HttpUrl = Field(description="PDF文件的URL地址")
    dpi: int = Field(default=200, ge=50, le=600, description="输出图片DPI，范围50-600")
    first_page: Optional[int] = Field(default=None, ge=1, description="起始页码（从1开始）")
    last_page: Optional[int] = Field(default=None, ge=1, description="结束页码")
    fmt: Literal["jpeg", "png", "ppm", "tiff"] = Field(default="png", description="输出图片格式")
    grayscale: bool = Field(default=False, description="是否转换为灰度图")
    transparent: bool = Field(default=False, description="是否保持透明背景（仅PNG支持）")
    thread_count: int = Field(default=1, ge=1, le=8, description="线程数，范围1-8")
    use_pdftocairo: bool = Field(default=False, description="是否使用pdftocairo引擎")
    timeout: int = Field(default=600, ge=30, le=1800, description="超时时间（秒），范围30-1800")
    size: Optional[int] = Field(default=None, ge=100, le=4000, description="输出图片大小（保持宽高比）")
    jpegopt: Optional[dict] = Field(default=None, description="JPEG压缩选项")
    storage_type: Literal["base64", "file", "both"] = Field(default="base64", description="存储类型：base64编码、文件存储或两者都有")
    image_mode: Literal["base64", "path"] = Field(default="base64", description="返回图片模式：base64编码或文件路径")
    
    class Config:
        schema_extra = {
            "example": {
                "pdf_url": "https://example.com/document.pdf",
                "dpi": 200,
                "first_page": 1,
                "last_page": 3,
                "fmt": "png",
                "grayscale": False,
                "transparent": True,
                "thread_count": 2,
                "use_pdftocairo": False,
                "timeout": 600,
                "size": 800,
                "storage_type": "file",
                "image_mode": "path"
            }
        }


class ConversionResponse(BaseModel):
    """转换结果响应"""
    success: bool = Field(description="转换是否成功")
    message: str = Field(description="响应消息")
    pages_count: int = Field(description="转换的页面数量")
    images: Optional[List[str]] = Field(default=None, description="Base64编码的图片列表或文件路径列表")
    file_urls: Optional[List[str]] = Field(default=None, description="图片文件访问URL列表")
    format: str = Field(description="图片格式")
    storage_type: str = Field(description="存储类型")
    image_mode: str = Field(description="图片返回模式")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "PDF转换成功",
                "pages_count": 3,
                "images": ["base64_image_data_1", "base64_image_data_2", "base64_image_data_3"],
                "file_urls": ["http://localhost:8000/files/page_1.png", "http://localhost:8000/files/page_2.png"],
                "format": "png",
                "storage_type": "both",
                "image_mode": "base64"
            }
        }


class PDFInfoResponse(BaseModel):
    """PDF信息响应"""
    success: bool = Field(description="获取信息是否成功")
    message: str = Field(description="响应消息")
    pages: Optional[int] = Field(description="总页数")
    title: Optional[str] = Field(description="PDF标题")
    subject: Optional[str] = Field(description="PDF主题")
    author: Optional[str] = Field(description="PDF作者")
    creator: Optional[str] = Field(description="PDF创建者")
    producer: Optional[str] = Field(description="PDF生成器")
    creation_date: Optional[str] = Field(description="创建日期")
    modification_date: Optional[str] = Field(description="修改日期")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "PDF信息获取成功",
                "pages": 10,
                "title": "示例文档",
                "subject": "技术文档",
                "author": "张三",
                "creator": "Microsoft Word",
                "producer": "Adobe PDF Library",
                "creation_date": "2024-01-01T10:00:00",
                "modification_date": "2024-01-02T15:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(default=False, description="操作是否成功")
    message: str = Field(description="错误消息")
    error_code: str = Field(description="错误代码")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "文件格式不支持",
                "error_code": "INVALID_FILE_FORMAT"
            }
        }