import json
import uuid
from datetime import datetime
from zenfile.utils.config import HISTORY_PATH


class HistoryManager:
    """管理文件移动历史，撤销功能"""

    @staticmethod
    def load_history():
        if not HISTORY_PATH.exists():
            return []
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def save_history(history):
        # 只保留最近 500 条记录
        if len(history) > 500:
            history = history[-500:]
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")

    @staticmethod
    def add_record(source, target):
        """记录一次移动操作"""
        record = {
            "id": str(uuid.uuid4()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": str(source),
            "target": str(target)
        }
        history = HistoryManager.load_history()
        history.append(record)
        HistoryManager.save_history(history)

    @staticmethod
    def pop_last_record():
        """取出最后一条记录用于撤销"""
        history = HistoryManager.load_history()
        if not history:
            return None
        last_record = history.pop()
        HistoryManager.save_history(history)
        return last_record