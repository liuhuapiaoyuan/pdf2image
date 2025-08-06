class PDF2ImageException(Exception):
    """PDF2Image基础异常类"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class InvalidFileFormatException(PDF2ImageException):
    """无效文件格式异常"""
    def __init__(self, message: str = "文件格式不支持"):
        super().__init__(message, "INVALID_FILE_FORMAT")


class FileTooLargeException(PDF2ImageException):
    """文件过大异常"""
    def __init__(self, message: str = "文件大小超过限制"):
        super().__init__(message, "FILE_TOO_LARGE")


class ConversionFailedException(PDF2ImageException):
    """转换失败异常"""
    def __init__(self, message: str = "PDF转换失败"):
        super().__init__(message, "CONVERSION_FAILED")


class PopplerNotInstalledException(PDF2ImageException):
    """Poppler未安装异常"""
    def __init__(self, message: str = "Poppler工具未正确安装或配置"):
        super().__init__(message, "POPPLER_NOT_INSTALLED")


class PDFCorruptedException(PDF2ImageException):
    """PDF文件损坏异常"""
    def __init__(self, message: str = "PDF文件已损坏或无法读取"):
        super().__init__(message, "PDF_CORRUPTED")