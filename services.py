import base64
import io
import os
import uuid
import httpx
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image

from pdf2image import convert_from_bytes, pdfinfo_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError,
    PDFPopplerTimeoutError
)

from config import config
from exceptions import (
    PDF2ImageException,
    ConversionFailedException,
    PopplerNotInstalledException,
    PDFCorruptedException
)
from models import ConversionRequest


class PDFConverterService:
    """PDF转换服务类"""
    
    @staticmethod
    def validate_pdf_file(pdf_data: bytes) -> None:
        """验证PDF文件"""
        if len(pdf_data) == 0:
            raise PDF2ImageException("文件为空", "EMPTY_FILE")
        
        if len(pdf_data) > config.MAX_FILE_SIZE:
            raise PDF2ImageException(f"文件大小超过限制 ({config.MAX_FILE_SIZE // (1024*1024)}MB)", "FILE_TOO_LARGE")
        
        # 检查PDF文件头
        if not pdf_data.startswith(b'%PDF-'):
            raise PDF2ImageException("不是有效的PDF文件", "INVALID_PDF_FORMAT")
    
    @staticmethod
    def generate_filename(page_index: int, fmt: str, prefix: str = None) -> str:
        """生成文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        if prefix:
            return f"{prefix}_page_{page_index + 1}_{timestamp}_{unique_id}.{fmt}"
        return f"page_{page_index + 1}_{timestamp}_{unique_id}.{fmt}"
    
    @staticmethod
    def save_image_to_file(image: Image.Image, filepath: Path, fmt: str, jpegopt: Optional[dict] = None) -> str:
        """保存图片到文件"""
        try:
            # 确保目录存在
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # 根据格式保存图片
            save_format = fmt.upper()
            if save_format == 'PPM':
                save_format = 'PNG'  # PPM格式转换为PNG
                filepath = filepath.with_suffix('.png')
            
            # 设置保存参数
            save_kwargs = {'format': save_format}
            if fmt == 'jpeg' and jpegopt:
                save_kwargs.update(jpegopt)
            
            image.save(filepath, **save_kwargs)
            return str(filepath)
            
        except Exception as e:
            raise ConversionFailedException(f"保存图片文件失败: {str(e)}")
    
    @staticmethod
    async def download_pdf_from_url(url: str, timeout: int = 30) -> bytes:
        """从URL下载PDF文件"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # 检查Content-Type是否为PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
                    # 再检查文件内容是否以PDF头开始
                    content = response.content
                    if not content.startswith(b'%PDF-'):
                        raise ConversionFailedException("URL返回的不是有效的PDF文件")
                
                return response.content
                
        except httpx.TimeoutException:
            raise ConversionFailedException("下载PDF文件超时")
        except httpx.HTTPStatusError as e:
            raise ConversionFailedException(f"下载PDF文件失败: HTTP {e.response.status_code}")
        except Exception as e:
            raise ConversionFailedException(f"下载PDF文件失败: {str(e)}")
    
    @staticmethod
    def convert_pdf_to_images(pdf_data: bytes, request: ConversionRequest, filename_prefix: str = None) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """
        将PDF转换为图片
        
        Args:
            pdf_data: PDF文件字节数据
            request: 转换请求参数
            filename_prefix: 文件名前缀
            
        Returns:
            Tuple[Optional[List[str]], Optional[List[str]]]: (Base64列表, 文件URL列表)
        """
        try:
            PDFConverterService.validate_pdf_file(pdf_data)
            
            # 构建转换参数
            convert_params = {
                'pdf_file': pdf_data,
                'dpi': request.dpi,
                'fmt': request.fmt,
                'grayscale': request.grayscale,
                'transparent': request.transparent,
                'thread_count': request.thread_count,
                'use_pdftocairo': request.use_pdftocairo,
                'timeout': request.timeout,
                'strict': True
            }
            
            # 添加Poppler路径
            if config.POPPLER_PATH:
                convert_params['poppler_path'] = config.POPPLER_PATH
            
            # 添加可选参数
            if request.first_page is not None:
                convert_params['first_page'] = request.first_page
            if request.last_page is not None:
                convert_params['last_page'] = request.last_page
            if request.size is not None:
                convert_params['size'] = request.size
            if request.jpegopt is not None:
                convert_params['jpegopt'] = request.jpegopt
            
            # 执行转换
            images = convert_from_bytes(**convert_params)
            
            base64_images = None
            file_urls = None
            
            # 根据存储类型处理结果
            storage_type = getattr(request, 'storage_type', config.OUTPUT_STORAGE_TYPE)
            image_mode = getattr(request, 'image_mode', 'base64')
            
            if storage_type in ['base64', 'both']:
                base64_images = []
                for img in images:
                    if image_mode == 'base64':
                        # 返回base64编码
                        buffer = io.BytesIO()
                        
                        # 根据格式保存图片
                        save_format = request.fmt.upper()
                        if save_format == 'PPM':
                            save_format = 'PNG'  # PPM格式转换为PNG
                        
                        # 设置保存参数
                        save_kwargs = {'format': save_format}
                        if request.fmt == 'jpeg' and request.jpegopt:
                            save_kwargs.update(request.jpegopt)
                        
                        img.save(buffer, **save_kwargs)
                        img_data = buffer.getvalue()
                        base64_img = base64.b64encode(img_data).decode('utf-8')
                        base64_images.append(base64_img)
                    else:
                        # image_mode == 'path', 暂时先保存到临时文件并返回路径
                        # 这种情况下建议使用 storage_type='file' 
                        base64_images = None
                        break
            
            if storage_type in ['file', 'both']:
                file_urls = []
                output_dir = config.ensure_output_dir()
                
                # 如果 image_mode 是 'path' 且 base64_images 为空，则填充文件路径到 base64_images
                if image_mode == 'path' and not base64_images:
                    base64_images = []
                
                for i, img in enumerate(images):
                    filename = PDFConverterService.generate_filename(i, request.fmt, filename_prefix)
                    filepath = output_dir / filename
                    
                    # 保存文件
                    PDFConverterService.save_image_to_file(img, filepath, request.fmt, request.jpegopt)
                    
                    # 生成访问URL
                    file_url = config.get_file_url(filename)
                    file_urls.append(file_url)
                    
                    # 如果 image_mode 是 'path'，添加文件路径到 base64_images
                    if image_mode == 'path':
                        base64_images.append(str(filepath))
            
            return base64_images, file_urls
            
        except PDFInfoNotInstalledError:
            raise PopplerNotInstalledException("Poppler工具未正确安装，请安装poppler-utils")
        except PDFPageCountError as e:
            raise PDFCorruptedException(f"PDF页面计数错误: {str(e)}")
        except PDFSyntaxError as e:
            raise PDFCorruptedException(f"PDF语法错误: {str(e)}")
        except PDFPopplerTimeoutError:
            raise ConversionFailedException("PDF转换超时，请尝试减少页面数量或增加超时时间")
        except Exception as e:
            raise ConversionFailedException(f"PDF转换失败: {str(e)}")
    
    @staticmethod
    def get_pdf_info(pdf_data: bytes) -> Dict[str, Any]:
        """
        获取PDF文件信息
        
        Args:
            pdf_data: PDF文件字节数据
            
        Returns:
            Dict[str, Any]: PDF信息字典
        """
        try:
            PDFConverterService.validate_pdf_file(pdf_data)
            
            # 获取PDF信息
            info = pdfinfo_from_bytes(pdf_data, strict=True)
            
            # 处理返回数据
            result = {
                'pages': info.get('Pages'),
                'title': info.get('Title'),
                'subject': info.get('Subject'),
                'author': info.get('Author'),
                'creator': info.get('Creator'),
                'producer': info.get('Producer'),
                'creation_date': info.get('CreationDate'),
                'modification_date': info.get('ModDate')
            }
            
            return result
            
        except PDFInfoNotInstalledError:
            raise PopplerNotInstalledException("Poppler工具未正确安装，请安装poppler-utils")
        except PDFSyntaxError as e:
            raise PDFCorruptedException(f"PDF语法错误: {str(e)}")
        except Exception as e:
            raise ConversionFailedException(f"获取PDF信息失败: {str(e)}")