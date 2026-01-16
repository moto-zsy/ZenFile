import json
import os
from pathlib import Path

# 定义全局路径
# 1. 基础配置目录 (AppData/Roaming/ZenFile)
BASE_DIR = Path(os.getenv('APPDATA')) / "ZenFile"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# 2. 关键文件路径
CONFIG_PATH = BASE_DIR / "settings.json"
LOG_DIR = BASE_DIR / "logs"
HISTORY_PATH = BASE_DIR / "history.json"  # 新增：撤销功能

def load_config():
    """读取配置，不存在则返回默认值"""
    if not CONFIG_PATH.exists():
        return {
            "watch_dirs": [],
            "hotkey": "<ctrl>+<alt>+z",
            "rules": {
                "01_图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
                "02_文档": [".pdf", ".docx", ".doc", ".txt", ".md", ".xlsx", ".xls", ".pptx", ".ppt", ".csv"],
                "03_视频": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
                "04_音频": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"],
                "05_压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
                "06_安装包": [".exe", ".msi"],
                "07_代码": [".py", ".java", ".html", ".css", ".js", ".json", ".sql", ".c", ".cpp"]
            },
            # 默认的智能关键词规则 (本次新增)
            "keyword_rules": {
                "合同": "02_文档/合同",
                "发票": "02_文档/财务",
                "报告": "02_文档/报告",
                "设计": "01_图片/设计"
            },
            "ignore_exts": [".tmp", ".crdownload", ".download", ".part", ".opdownload", ".lnk", ".url", ".ini", ".db", ".sys", ".bak", ".log", ".old", ".sav", ".lock"]
        }

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return load_config()

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"保存配置失败: {e}")