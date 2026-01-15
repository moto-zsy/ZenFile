import json
import os
import sys
import logging
from pathlib import Path


# 获取运行目录
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


BASE_DIR = get_base_dir()
CONFIG_PATH = BASE_DIR / "config" / "settings.json"


def load_config():
    """读取配置"""
    if not CONFIG_PATH.exists():
        # 默认配置
        return {
            "watch_dirs": [],
            "hotkey": "<ctrl>+<alt>+z",  # 默认快捷键
            "rules": {
                "01_图片": [".jpg", ".png", ".gif"],
                "02_文档": [".pdf", ".docx", ".txt"]
            },
            "ignore_exts": [".tmp", ".crdownload"]
        }

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    """保存配置到文件"""
    # 确保 config 目录存在
    CONFIG_PATH.parent.mkdir(exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def setup_logger():
    # ... (保持原有的日志代码不变) ...
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("ZenFile")
    logger.setLevel(logging.INFO)
    if logger.handlers: return logger
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def get_resource_path(relative_path):
    # PyInstaller 会把资源解压到 sys._MEIPASS 目录下
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)