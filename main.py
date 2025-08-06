from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
import time
from pathlib import Path

from config import config
from models import ConversionRequest, URLConversionRequest, ConversionResponse, PDFInfoResponse, ErrorResponse
from services import PDFConverterService
from exceptions import PDF2ImageException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/pdf2image.log') if os.path.exists('/app') else logging.FileHandler('pdf2image.log')
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="PDF2Image API",
    description="基于pdf2image库的PDF转图片接口服务",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务
if config.OUTPUT_STORAGE_TYPE in ["file", "both"]:
    output_dir = config.ensure_output_dir()
    app.mount("/files", StaticFiles(directory=str(output_dir)), name="files")


def validate_file(file: UploadFile = File(...)) -> UploadFile:
    """验证上传的文件"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件格式")
    return file


@app.get("/", tags=["基础信息"])
async def root():
    """API根路径，返回服务信息"""
    return {
        "service": "PDF2Image API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["基础信息"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "pdf2image-api"}


@app.post(
    "/convert",
    response_model=ConversionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    },
    tags=["PDF转换"],
    summary="PDF转图片",
    description="将上传的PDF文件转换为图片，支持多种格式和参数配置"
)
async def convert_pdf_to_images(
    file: UploadFile = Depends(validate_file),
    dpi: int = 200,
    first_page: int = None,
    last_page: int = None,
    fmt: str = "png",
    grayscale: bool = False,
    transparent: bool = False,
    thread_count: int = 1,
    use_pdftocairo: bool = False,
    timeout: int = 600,
    size: int = None,
    storage_type: str = "file",
    image_mode: str = "path"
):
    """
    转换PDF文件为图片格式
    
    - **file**: 要转换的PDF文件
    - **dpi**: 输出分辨率 (50-600)
    - **first_page**: 起始页码（从1开始）
    - **last_page**: 结束页码
    - **fmt**: 输出格式 (jpeg/png/ppm/tiff)
    - **grayscale**: 是否转为灰度图
    - **transparent**: 是否保持透明背景
    - **thread_count**: 线程数 (1-8)
    - **use_pdftocairo**: 是否使用pdftocairo引擎
    - **timeout**: 超时时间（秒）
    - **size**: 输出图片大小（保持宽高比）
    - **storage_type**: 存储类型 (base64/file/both)
    - **image_mode**: 图片返回模式 (base64/path)
    """
    start_time = time.time()
    logger.info(f"开始处理PDF转换请求 - 文件名: {file.filename}, DPI: {dpi}, 格式: {fmt}, 存储类型: {storage_type}, 返回模式: {image_mode}")
    
    try:
        # 读取文件内容
        logger.info(f"开始读取PDF文件: {file.filename}")
        pdf_data = await file.read()
        logger.info(f"PDF文件读取完成，大小: {len(pdf_data)} bytes")
        
        # 构建转换请求
        request = ConversionRequest(
            dpi=dpi,
            first_page=first_page,
            last_page=last_page,
            fmt=fmt,
            grayscale=grayscale,
            transparent=transparent,
            thread_count=thread_count,
            use_pdftocairo=use_pdftocairo,
            timeout=timeout,
            size=size,
            storage_type=storage_type,
            image_mode=image_mode
        )
        
        # 执行转换
        filename_prefix = os.path.splitext(file.filename)[0] if file.filename else "pdf"
        logger.info(f"开始转换PDF，参数: dpi={request.dpi}, 格式={request.fmt}, 页面范围={request.first_page}-{request.last_page}")
        base64_images, file_urls = PDFConverterService.convert_pdf_to_images(pdf_data, request, filename_prefix)
        logger.info(f"PDF转换完成")
        
        # 计算页面数
        pages_count = len(base64_images) if base64_images else len(file_urls) if file_urls else 0
        
        elapsed_time = time.time() - start_time
        logger.info(f"PDF转换成功完成，耗时: {elapsed_time:.2f}秒，页面数: {pages_count}")
        
        return ConversionResponse(
            success=True,
            message="PDF转换成功",
            pages_count=pages_count,
            images=base64_images,
            file_urls=file_urls,
            format=fmt,
            storage_type=storage_type,
            image_mode=image_mode
        )
        
    except PDF2ImageException as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                message=e.message,
                error_code=e.error_code
            ).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=f"服务器内部错误: {str(e)}",
                error_code="INTERNAL_ERROR"
            ).dict()
        )


@app.post(
    "/convert-advanced",
    response_model=ConversionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    },
    tags=["PDF转换"],
    summary="PDF转图片（高级版）",
    description="使用JSON参数配置的PDF转图片接口，支持所有转换参数"
)
async def convert_pdf_to_images_advanced(
    request: ConversionRequest,
    file: UploadFile = Depends(validate_file)
):
    """
    高级PDF转图片接口，支持完整的参数配置
    """
    try:
        # 读取文件内容
        pdf_data = await file.read()
        
        # 执行转换
        filename_prefix = os.path.splitext(file.filename)[0] if file.filename else "pdf"
        base64_images, file_urls = PDFConverterService.convert_pdf_to_images(pdf_data, request, filename_prefix)
        
        # 计算页面数
        pages_count = len(base64_images) if base64_images else len(file_urls) if file_urls else 0
        
        return ConversionResponse(
            success=True,
            message="PDF转换成功",
            pages_count=pages_count,
            images=base64_images,
            file_urls=file_urls,
            format=request.fmt,
            storage_type=request.storage_type,
            image_mode=request.image_mode
        )
        
    except PDF2ImageException as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                message=e.message,
                error_code=e.error_code
            ).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=f"服务器内部错误: {str(e)}",
                error_code="INTERNAL_ERROR"
            ).dict()
        )


@app.post(
    "/convert-from-url",
    response_model=ConversionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    },
    tags=["PDF转换"],
    summary="从URL转换PDF",
    description="从提供的URL下载PDF文件并转换为图片"
)
async def convert_pdf_from_url(request: URLConversionRequest):
    """
    从URL下载PDF并转换为图片
    
    - **pdf_url**: PDF文件的URL地址
    - 其他参数与文件上传转换接口相同
    """
    try:
        # 从URL下载PDF文件
        pdf_data = await PDFConverterService.download_pdf_from_url(str(request.pdf_url), request.timeout)
        
        # 执行转换
        from urllib.parse import urlparse
        parsed_url = urlparse(str(request.pdf_url))
        filename_prefix = Path(parsed_url.path).stem or "url_pdf"
        
        base64_images, file_urls = PDFConverterService.convert_pdf_to_images(pdf_data, request, filename_prefix)
        
        # 计算页面数
        pages_count = len(base64_images) if base64_images else len(file_urls) if file_urls else 0
        
        return ConversionResponse(
            success=True,
            message="PDF转换成功",
            pages_count=pages_count,
            images=base64_images,
            file_urls=file_urls,
            format=request.fmt,
            storage_type=request.storage_type,
            image_mode=request.image_mode
        )
        
    except PDF2ImageException as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                message=e.message,
                error_code=e.error_code
            ).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=f"服务器内部错误: {str(e)}",
                error_code="INTERNAL_ERROR"
            ).dict()
        )


@app.post(
    "/info",
    response_model=PDFInfoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    },
    tags=["PDF信息"],
    summary="获取PDF信息",
    description="获取PDF文件的基本信息，如页数、作者、创建日期等"
)
async def get_pdf_info(file: UploadFile = Depends(validate_file)):
    """
    获取PDF文件的基本信息
    
    - **file**: 要查询信息的PDF文件
    """
    try:
        # 读取文件内容
        pdf_data = await file.read()
        
        # 获取PDF信息
        info = PDFConverterService.get_pdf_info(pdf_data)
        
        return PDFInfoResponse(
            success=True,
            message="PDF信息获取成功",
            **info
        )
        
    except PDF2ImageException as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                message=e.message,
                error_code=e.error_code
            ).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=f"服务器内部错误: {str(e)}",
                error_code="INTERNAL_ERROR"
            ).dict()
        )


# 异常处理器
@app.exception_handler(PDF2ImageException)
async def pdf2image_exception_handler(request, exc: PDF2ImageException):
    """PDF2Image异常处理器"""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            success=False,
            message=exc.message,
            error_code=exc.error_code
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code="HTTP_ERROR"
        ).dict()
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"]
    )