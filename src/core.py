import shutil
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler


class FileOrganizer(FileSystemEventHandler):
    # 变更：__init__ 增加 specific_watch_path 参数
    def __init__(self, specific_watch_path, config, logger):
        self.watch_dir = Path(specific_watch_path)  # 当前实例只管这一个目录
        self.rules = config["rules"]
        self.ignore_exts = config["ignore_exts"]
        self.logger = logger

    def on_modified(self, event):
        if not event.is_directory: self.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory: self.process_file(event.dest_path)

    def on_created(self, event):
        if not event.is_directory: self.process_file(event.src_path)

    def process_file(self, file_path_str):
        file_path = Path(file_path_str)

        if not file_path.exists() or file_path.name.startswith("."):
            return
        if file_path.suffix.lower() in self.ignore_exts:
            return

        # 匹配规则
        target_folder_name = "99_其他"
        ext = file_path.suffix.lower()
        for folder, ext_list in self.rules.items():
            if ext in ext_list:
                target_folder_name = folder
                break

        # 如果不需要处理"其他"，取消注释
        # if target_folder_name == "99_其他": return

        self.move_file(file_path, target_folder_name)

    def move_file(self, file_path, folder_name):
        # 关键：在当前监控的根目录下创建分类文件夹
        target_dir = self.watch_dir / folder_name

        try:
            target_dir.mkdir(exist_ok=True)
            target_path = target_dir / file_path.name

            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1

            time.sleep(0.5)
            shutil.move(str(file_path), str(target_path))
            self.logger.info(f"[{self.watch_dir.name}] 整理: {file_path.name} -> {folder_name}")

        except Exception as e:
            self.logger.error(f"移动失败: {e}")