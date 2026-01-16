import sys
import platform
from pathlib import Path
from watchdog.observers import Observer

from zenfile.utils.config import load_config
from zenfile.utils.logger import setup_logger
from zenfile.core.organizer import Organizer
from zenfile.core.monitor import FileMonitor
from zenfile.ui.tray import SystemTray

# Windows 单例锁依赖
if platform.system() == "Windows":
    import win32event, win32api, winerror


def check_single_instance():
    """防止软件重复运行"""
    if platform.system() == "Windows":
        mutex = win32event.CreateMutex(None, False, "Global\\ZenFile_v1_Lock")
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            return False, mutex
        return True, mutex
    return True, None


def main():
    # 1. 单例检查
    is_unique, mutex = check_single_instance()
    if not is_unique:
        print("ZenFile 已经在运行中...")
        # 这里虽然没有弹窗提示，但会直接静默退出，防止后台堆积
        sys.exit(0)

    # 2. 初始化基础设施
    logger = setup_logger()
    config = load_config()
    logger.info(">>> ZenFile 启动中...")

    # 3. 初始化核心业务
    organizer = Organizer(config, logger)
    event_handler = FileMonitor(organizer)

    # 4. 启动文件监控 (Watchdog)
    observer = Observer()
    watch_dirs = config.get("watch_dirs", [])

    monitor_started = False
    for path_str in watch_dirs:
        path = Path(path_str)
        if path.exists():
            observer.schedule(event_handler, str(path), recursive=False)
            logger.info(f"正在监控: {path}")
            monitor_started = True

    if monitor_started:
        observer.start()
    else:
        logger.warning("没有配置有效的监控目录，仅启动托盘菜单。")

    # 5. 启动系统托盘 (阻塞主线程)
    try:
        tray = SystemTray(organizer)
        tray.run()
    except KeyboardInterrupt:
        pass
    finally:
        if monitor_started:
            observer.stop()
            observer.join()
        logger.info("<<< ZenFile 已退出")


if __name__ == "__main__":
    main()