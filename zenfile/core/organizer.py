import shutil
import time
import sys
from pathlib import Path
from .history import HistoryManager
from .rules import RuleMatcher


class Organizer:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.matcher = RuleMatcher(config)

        # 处理监控路径 (兼容字符串或列表)
        raw_dirs = config.get("watch_dirs", [])
        if isinstance(raw_dirs, str):
            self.watch_dirs = [Path(raw_dirs)]
        else:
            self.watch_dirs = [Path(p) for p in raw_dirs]

    def process_file(self, file_path_str):
        """处理单个文件 (核心逻辑)"""
        file_path = Path(file_path_str)

        # 1. 基础检查
        if not file_path.exists(): return

        # 防止处理程序自己
        if getattr(sys, 'frozen', False) and file_path.resolve() == Path(sys.executable).resolve():
            return

        # 忽略隐藏文件、临时锁文件
        if file_path.name.startswith(".") or file_path.name.startswith("~$"):
            return

        # 2. 规则匹配
        should_ignore, target_folder_name = self.matcher.match(file_path)
        if should_ignore:
            return

        # 3. 执行移动
        self._move_file(file_path, target_folder_name)

    def _move_file(self, source_path, folder_name):
        """内部方法：执行物理移动并记录历史"""
        # 确定目标父目录 (通常是当前文件所在目录)
        parent_dir = source_path.parent
        target_dir = parent_dir / folder_name

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / source_path.name

            # 防重名处理
            counter = 1
            stem = source_path.stem
            suffix = source_path.suffix
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            # 稍微等待文件释放
            time.sleep(0.1)

            shutil.move(str(source_path), str(target_path))

            # 记录历史
            HistoryManager.add_record(source_path, target_path)

            self.logger.info(f"整理成功: {source_path.name} -> {folder_name}")
            return True
        except Exception as e:
            self.logger.error(f"移动失败 {source_path.name}: {e}")
            return False

    def run_now(self):
        """一键整理所有目录"""
        count = 0
        self.logger.info(">>> 开始一键整理...")
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists(): continue
            for item in watch_dir.iterdir():
                if item.is_file():
                    self.process_file(item)
                    count += 1
        self.logger.info(f"<<< 一键整理完成，扫描了 {count} 个文件")
        return count

    def undo_last_action(self):
        """撤销上一步"""
        record = HistoryManager.pop_last_record()
        if not record:
            return False, "没有可撤销的操作"

        try:
            current_path = Path(record['target'])
            original_path = Path(record['source'])

            if not current_path.exists():
                return False, f"文件已不存在: {current_path.name}"

            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), str(original_path))

            self.logger.info(f"撤销成功: {current_path.name} -> 返回原位")
            return True, f"已撤销: {original_path.name}"
        except Exception as e:
            self.logger.error(f"撤销失败: {e}")
            return False, f"撤销出错: {e}"