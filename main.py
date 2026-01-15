import threading
import os
import tkinter as tk
from PIL import Image, ImageDraw

# GUI 与 交互
import pystray
from pystray import MenuItem as Item
from pynput import keyboard

# 内部模块
from src.utils import load_config, setup_logger,get_resource_path
from src.core import FileOrganizer
from src.ui import SettingsWindow
from watchdog.observers import Observer

# 防止双开锁
import win32event, win32api, winerror


class ZenFileApp:
    def __init__(self, root):
        self.root = root
        self.logger = setup_logger()
        self.observer = None
        self.is_running = False
        self.icon = None
        self.hotkey_listener = None

        # 加载配置
        self.config = load_config()
        self.watch_dirs = self.config.get("watch_dirs", [])
        self.hotkey_str = self.config.get("hotkey", "<ctrl>+<alt>+z")

        # 初始化后台逻辑
        self.start_watching()
        self.start_hotkey()

    # --- 1. 托盘图标 ---
    def create_icon_image(self, color):
        """加载自定义 PNG 图标，失败则画圆点"""
        if color == "#0078D7":
            rel_path = "assets/icons/logo.png"
        else:
            rel_path = "assets/icons/pause.png"

        try:
            icon_path = get_resource_path(rel_path)
            if icon_path.exists():
                return Image.open(icon_path).convert("RGBA")
        except Exception as e:
            print(f"[Error] 图标加载失败: {e}")

        # 兜底绘制
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((8, 8, 56, 56), fill=color)
        dc.ellipse((24, 24, 40, 40), fill='white')
        return image

    def build_menu(self):
        """
        ✅ 核心修复：
        每次调用都根据当前状态生成全新的菜单对象。
        不再依赖 pystray 的动态文本回调，确保 100% 刷新。
        """
        # 直接根据状态生成固定的字符串
        state_text = "状态: 运行中 🟢" if self.is_running else "状态: 已暂停 🔴"

        return pystray.Menu(
            Item(state_text, self.toggle_watching),  # 第一行直接显示当前状态
            pystray.Menu.SEPARATOR,
            Item('⚙️ 设置', self.open_settings_ui),
            Item('退出', self.quit_app)
        )

    def update_tray_icon(self):
        if not self.icon: return

        # 重新生成图标对象，确保 UI 线程检测到变化
        if self.is_running:
            self.icon.icon = self.create_icon_image("#0078D7")  # 蓝
            self.icon.title = f"ZenFile: 运行中\n快捷键: {self.hotkey_str}"
        else:
            self.icon.icon = self.create_icon_image("#808080")  # 灰
            self.icon.title = "ZenFile: 已暂停"

        # 2. ✅ 核心修复：强制替换整个菜单对象
        # 这样无论有没有缓存，下次点开必定是新的文字
        self.icon.menu = self.build_menu()

    def run_tray(self):
        # 初始启动时创建图标和菜单
        self.icon = pystray.Icon(
            "ZenFile",
            self.create_icon_image("#0078D7"),
            "ZenFile",
            self.build_menu()  # 使用 build_menu 初始化
        )
        self.update_tray_icon()  # 确保状态同步
        self.icon.run()

    # --- 2. 界面与交互 ---
    def open_settings_ui(self, icon=None, item=None):
        self.root.after(0, self._show_settings_window)

    def _show_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        SettingsWindow(settings_win, on_save_callback=self.reload_config)

    def reload_config(self, new_config):
        self.logger.info("配置已更新...")

        was_running = self.is_running

        self.config = new_config
        self.watch_dirs = new_config.get("watch_dirs", [])
        new_hotkey = new_config.get("hotkey", "<ctrl>+<alt>+z")

        self.stop_watching()

        if was_running:
            self.start_watching()
        else:
            self.logger.info("保持暂停状态")

        if new_hotkey != self.hotkey_str:
            self.hotkey_str = new_hotkey
            self.stop_hotkey()
            self.start_hotkey()

        self.update_tray_icon()

    # --- 3. 监控逻辑 ---
    def start_watching(self):
        if self.is_running: return
        if not self.watch_dirs: return

        self.observer = Observer()
        count = 0
        for path_str in self.watch_dirs:
            if path_str.startswith("~"): path_str = os.path.expanduser(path_str)
            if os.path.exists(path_str):
                handler = FileOrganizer(path_str, self.config, self.logger)
                self.observer.schedule(handler, path_str, recursive=False)
                count += 1

        if count > 0:
            self.observer.start()
            self.is_running = True
            self.logger.info(f"✅ 服务已启动，监控 {count} 个目录")
        else:
            self.logger.error("❌ 启动失败：所有路径均无效")

    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.is_running = False

    def toggle_watching(self, icon=None, item=None):
        self.logger.info("正在切换状态...")

        # 切换逻辑
        if self.is_running:
            self.stop_watching()
            msg = "自动整理已暂停"
        else:
            self.start_watching()
            msg = "自动整理已恢复"

        if self.icon:
            self.icon.notify(msg)

        # 强制刷新 (这里会调用 build_menu 重建菜单)
        self.update_tray_icon()
        self.logger.info(f"状态切换完成: {msg}")

    # --- 4. 快捷键逻辑 ---
    def start_hotkey(self):
        def listen():
            try:
                with keyboard.GlobalHotKeys({self.hotkey_str: self.toggle_watching}) as h:
                    self.hotkey_listener = h
                    h.join()
            except Exception as e:
                self.logger.error(f"快捷键注册失败: {e}")

        threading.Thread(target=listen, daemon=True).start()

    def stop_hotkey(self):
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
            self.hotkey_listener = None

    def quit_app(self, icon, item):
        if self.icon:
            self.icon.visible = False
            self.icon.stop()
        os._exit(0)


if __name__ == "__main__":
    mutex = win32event.CreateMutex(None, False, "Global\\ZenFile_GUI_Lock")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, "ZenFile 已经在运行中！", "提示", 0x40)
        os._exit(0)

    root = tk.Tk()
    root.withdraw()

    app = ZenFileApp(root)
    threading.Thread(target=app.run_tray, daemon=True).start()
    root.mainloop()