# PDF2Image FastAPI 服务

基于 pdf2image 库的 PDF 转图片 FastAPI 接口服务，提供完整的 RESTful API 和 Swagger 文档。

## 功能特性

- 🚀 **高性能**: 基于 FastAPI 异步框架
- 📄 **PDF转图片**: 支持多种输出格式 (PNG, JPEG, TIFF, PPM)
- 🎛️ **参数丰富**: 支持 DPI、页面范围、灰度、透明度等多种配置
- 📊 **PDF信息**: 获取 PDF 文件基本信息
- 🔧 **多线程**: 支持多线程并行转换
- 📖 **完整文档**: 自动生成的 Swagger API 文档
- ⚡ **性能优化**: 支持 pdftocairo 引擎
- 🛡️ **安全验证**: 文件格式和大小限制
- 💾 **灵活存储**: 支持 Base64 编码、文件存储或混合模式
- 🐳 **容器化**: 完整的 Docker 支持
- ⚙️ **环境配置**: 通过环境变量灵活配置
- 🌐 **URL支持**: 支持从URL直接下载并转换PDF文件
- 📁 **返回模式**: 支持Base64编码或文件路径两种返回模式

## 安装要求

### 系统依赖

#### Windows
```bash
# 下载并安装 poppler for Windows
# 推荐使用 @oschwartz10612 版本
# 下载后将 bin 目录添加到系统 PATH
```

#### macOS
```bash
brew install poppler
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# CentOS/RHEL
sudo yum install poppler-utils
```

### Python 依赖
```bash
pip install -r requirements.txt
```

## 快速启动

### 本地运行

#### 方式一：使用 run.py
```bash
python run.py
```

#### 方式二：使用 uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方式三：环境变量配置
```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑配置文件
nano .env

# 启动服务
python run.py
```

### Docker 运行

#### 使用 Docker Compose（推荐）
```bash
# 启动服务
docker-compose up -d

# 启动带 Nginx 代理的服务
docker-compose --profile with-nginx up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 使用 Docker
```bash
# 构建镜像
docker build -t pdf2image-api .

# 运行容器
docker run -d \
  --name pdf2image-api \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  -e OUTPUT_STORAGE_TYPE=both \
  -e OUTPUT_DIR=/app/output \
  pdf2image-api
```

### 访问服务
- API 服务：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc
- 文件访问：http://localhost:8000/files/

## API 接口

### 基础接口

#### GET `/`
服务基本信息

#### GET `/health`
健康检查

### PDF转换接口

#### POST `/convert`
基础PDF转图片接口

**参数：**
- `file`: PDF文件 (form-data)
- `dpi`: 分辨率 (默认: 200)
- `first_page`: 起始页码
- `last_page`: 结束页码  
- `fmt`: 输出格式 (png/jpeg/tiff/ppm)
- `grayscale`: 是否灰度
- `transparent`: 是否透明背景
- `thread_count`: 线程数
- `use_pdftocairo`: 使用 pdftocairo 引擎
- `timeout`: 超时时间（秒）
- `size`: 输出尺寸
- `storage_type`: 存储类型 (base64/file/both)
- `image_mode`: 返回模式 (base64/path)

**响应：**
```json
{
  "success": true,
  "message": "PDF转换成功",
  "pages_count": 3,
  "images": ["base64_image_1", "base64_image_2", "base64_image_3"],
  "file_urls": ["http://localhost:8000/files/page_1.png", "http://localhost:8000/files/page_2.png"],
  "format": "png",
  "storage_type": "both",
  "image_mode": "base64"
}
```

#### POST `/convert-advanced`
高级PDF转图片接口，支持JSON参数配置

**请求体：**
```json
{
  "dpi": 300,
  "first_page": 1,
  "last_page": 5,
  "fmt": "png",
  "grayscale": false,
  "transparent": true,
  "thread_count": 2,
  "use_pdftocairo": false,
  "timeout": 600,
  "size": 800,
  "storage_type": "both",
  "image_mode": "base64",
  "jpegopt": {"quality": 95}
}
```

### PDF信息接口

#### POST `/info`
获取PDF文件信息

**响应：**
```json
{
  "success": true,
  "message": "PDF信息获取成功",
  "pages": 10,
  "title": "示例文档",
  "subject": "技术文档",
  "author": "作者",
  "creator": "创建工具",
  "producer": "生成器",
  "creation_date": "2024-01-01T10:00:00",
  "modification_date": "2024-01-02T15:30:00"
}
```

#### POST `/convert-from-url`
从URL转换PDF文件

**请求体：**
```json
{
  "pdf_url": "https://example.com/document.pdf",
  "dpi": 300,
  "first_page": 1,
  "last_page": 3,
  "fmt": "png",
  "grayscale": false,
  "transparent": true,
  "thread_count": 2,
  "use_pdftocairo": false,
  "timeout": 600,
  "size": 800,
  "storage_type": "file",
  "image_mode": "path"
}
```

**响应：**
```json
{
  "success": true,
  "message": "PDF转换成功",
  "pages_count": 3,
  "images": ["/app/output/document_page_1_20241206_abc123.png"],
  "file_urls": ["http://localhost:8000/files/document_page_1_20241206_abc123.png"],
  "format": "png",
  "storage_type": "file",
  "image_mode": "path"
}
```

## 使用示例

### Python 客户端示例

```python
import requests

# 基础转换
with open('example.pdf', 'rb') as f:
    files = {'file': f}
    params = {'dpi': 300, 'fmt': 'png'}
    response = requests.post('http://localhost:8000/convert', files=files, params=params)
    result = response.json()

# 高级转换
with open('example.pdf', 'rb') as f:
    files = {'file': f}
    json_data = {
        'dpi': 300,
        'fmt': 'jpeg',
        'grayscale': True,
        'first_page': 1,
        'last_page': 3
    }
    response = requests.post('http://localhost:8000/convert-advanced', files=files, json=json_data)
    result = response.json()

# 获取PDF信息
with open('example.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/info', files=files)
    info = response.json()

# 从URL转换PDF
url_data = {
    'pdf_url': 'https://example.com/document.pdf',
    'dpi': 300,
    'fmt': 'jpeg',
    'storage_type': 'file',
    'image_mode': 'path'
}
response = requests.post('http://localhost:8000/convert-from-url', json=url_data)
result = response.json()
```

### cURL 示例

```bash
# 基础转换
curl -X POST "http://localhost:8000/convert" \
  -F "file=@example.pdf" \
  -F "dpi=300" \
  -F "fmt=png"

# 获取PDF信息
curl -X POST "http://localhost:8000/info" \
  -F "file=@example.pdf"

# 从URL转换PDF
curl -X POST "http://localhost:8000/convert-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/document.pdf",
    "dpi": 300,
    "fmt": "png",
    "storage_type": "both",
    "image_mode": "base64"
  }'
```

## 错误处理

所有接口都返回统一的错误格式：

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

**常见错误代码：**
- `INVALID_FILE_FORMAT`: 文件格式不支持
- `FILE_TOO_LARGE`: 文件过大
- `CONVERSION_FAILED`: 转换失败
- `POPPLER_NOT_INSTALLED`: Poppler未安装
- `PDF_CORRUPTED`: PDF文件损坏

## 性能建议

1. **使用输出文件夹**: 对于大文件，建议使用 SSD 存储
2. **线程控制**: 建议线程数不超过 4 个
3. **格式选择**: JPEG 格式转换更快，PNG 压缩较慢
4. **引擎选择**: pdftocairo 引擎性能更好
5. **文件大小**: 建议单个 PDF 文件不超过 50MB

## 项目结构

```
pdf2image/
├── main.py                 # FastAPI 应用主文件
├── models.py              # Pydantic 数据模型
├── services.py            # PDF转换服务类
├── exceptions.py          # 自定义异常类
├── config.py              # 配置管理类
├── run.py                # 服务启动脚本
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker Compose配置
├── nginx.conf            # Nginx代理配置
├── .env.example         # 环境变量示例
├── .dockerignore        # Docker忽略文件
├── __init__.py          # 包初始化
└── README.md            # 项目文档
```

## 环境变量配置

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 8000 | 服务端口 |
| `DEBUG` | false | 调试模式 |
| `OUTPUT_STORAGE_TYPE` | base64 | 存储类型 (base64/file/both) |
| `OUTPUT_DIR` | /tmp/pdf2image_output | 文件输出目录 |
| `OUTPUT_BASE_URL` | http://localhost:8000/files | 文件访问基础URL |
| `MAX_FILE_SIZE` | 52428800 | 最大文件大小 (字节) |
| `DEFAULT_DPI` | 200 | 默认DPI |
| `DEFAULT_FORMAT` | png | 默认输出格式 |
| `MAX_THREAD_COUNT` | 8 | 最大线程数 |
| `DEFAULT_TIMEOUT` | 600 | 默认超时时间 |
| `CORS_ORIGINS` | * | CORS允许的来源 |
| `POPPLER_PATH` | 空 | Poppler工具路径 |
| `ENABLE_CACHE` | false | 启用缓存 |
| `CACHE_TTL` | 3600 | 缓存过期时间

## 许可证

MIT License