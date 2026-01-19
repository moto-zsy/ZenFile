import json
import uuid
import threading
from datetime import datetime
from zenfile.utils.config import HISTORY_PATH


class HistoryManager:
    _lock = threading.Lock()

    @staticmethod
    def load_history():
        if not HISTORY_PATH.exists():
            return []
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    load = load_history

    @staticmethod
    def save_history(history):
        if len(history) > 1000:
            history = history[-1000:]
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")

    @staticmethod
    def add_record(source, target, batch_id=None):
        with HistoryManager._lock:
            record = {
                "id": str(uuid.uuid4()),
                "batch_id": batch_id,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": str(source),
                "target": str(target)
            }
            history = HistoryManager.load_history()
            history.append(record)
            HistoryManager.save_history(history)

    @staticmethod
    def pop_last_batch():
        with HistoryManager._lock:
            history = HistoryManager.load_history()
            if not history:
                return []

            last_record = history[-1]
            last_batch_id = last_record.get("batch_id")

            if not last_batch_id:
                history.pop()
                HistoryManager.save_history(history)
                return [last_record]

            batch_records = []
            while history:
                if history[-1].get("batch_id") == last_batch_id:
                    batch_records.append(history.pop())
                else:
                    break

            HistoryManager.save_history(history)
            return batch_records