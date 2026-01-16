import logging
from .config import LOG_DIR  # 引用同级模块的变量


def setup_logger():
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("ZenFile")
    logger.setLevel(logging.INFO)
    if logger.handlers: return logger

    formatter = logging.Formatter('%(asctime)s - %(message)s')

    # 文件日志
    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger