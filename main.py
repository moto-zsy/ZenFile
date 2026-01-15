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
        """
                尝试加载自定义 PNG 图标。
                如果加载失败，自动降级为绘制圆点图标作为兜底。
                """
        # 根据颜色判断状态，决定加载哪张图片
        if color == "#0078D7":
            # 运行状态 (蓝色) -> 加载 run.png
            rel_path = "assets/icons/logo.png"
        else:
            # 暂停状态 (灰色) -> 加载 pause.png
            rel_path = "assets/icons/pause.png"

        try:
            # 使用 get_resource_path 获取真实路径 (兼容 EXE 内部路径)
            # 注意：一定要确保 main.py 顶部导入了 get_resource_path
            icon_path = get_resource_path(rel_path)

            if icon_path.exists():
                # ✅ 关键：加载图片并转换为 RGBA 模式 (支持透明)
                return Image.open(icon_path).convert("RGBA")
            else:
                # 如果找不到文件，打印个提示 (在黑框模式下能看到)
                print(f"[Warning] 找不到图标文件: {icon_path}，将使用默认绘图。")

        except Exception as e:
            print(f"[Error] 图标加载失败: {e}，将使用默认绘图。")

        # === 🛡️ 兜底方案 (如果上面加载失败了，就用原来画圆点的代码) ===
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # 透明背景
        dc = ImageDraw.Draw(image)
        dc.ellipse((8, 8, 56, 56), fill=color)
        dc.ellipse((24, 24, 40, 40), fill='white')
        return image

    def update_tray_icon(self):
        if not self.icon: return

        # 重新生成图标对象，确保 UI 线程检测到变化
        if self.is_running:
            self.icon.icon = self.create_icon_image("#0078D7")  # 蓝
            self.icon.title = f"ZenFile: 运行中\n快捷键: {self.hotkey_str}"
        else:
            self.icon.icon = self.create_icon_image("#808080")  # 灰
            self.icon.title = "ZenFile: 已暂停"

    # === 修复点 1：去掉了多余的 def run_tray(self) 嵌套 ===
    def run_tray(self):
        def get_state_text(item):
            return "状态: 运行中 🟢" if self.is_running else "状态: 已暂停 🔴"

        menu = pystray.Menu(
            Item(get_state_text, self.toggle_watching),
            pystray.Menu.SEPARATOR,
            Item('⚙️ 设置', self.open_settings_ui),
            Item('退出', self.quit_app)
        )

        self.icon = pystray.Icon("ZenFile", self.create_icon_image("#0078D7"), "ZenFile", menu)
        self.update_tray_icon()
        self.icon.run()

    # --- 2. 设置界面调用 ---
    def open_settings_ui(self, icon=None, item=None):
        # 托盘是在子线程运行的，必须通知主线程(Tkinter)去显示窗口
        self.root.after(0, self._show_settings_window)

    def _show_settings_window(self):
        # 创建一个顶级窗口 (Toplevel)
        settings_win = tk.Toplevel(self.root)
        # 把保存回调传进去
        SettingsWindow(settings_win, on_save_callback=self.reload_config)

    def reload_config(self, new_config):
        """当设置界面保存后，刷新所有服务"""
        self.logger.info("配置已更新，正在重载服务...")
        self.config = new_config
        self.watch_dirs = new_config.get("watch_dirs", [])
        new_hotkey = new_config.get("hotkey", "<ctrl>+<alt>+z")

        # 重启监控
        self.stop_watching()
        self.start_watching()

        # 重启快捷键 (如果变了)
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
            self.logger.error("❌ 启动失败：所有监控路径均无效")

    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.is_running = False

    # === 修复点 2：去掉了多余的 def toggle_watching(...) 嵌套 ===
    def toggle_watching(self, icon=None, item=None):
        self.logger.info("正在切换状态...")

        if self.is_running:
            self.stop_watching()
            msg = "自动整理已暂停"
        else:
            self.start_watching()
            msg = "自动整理已恢复"

        # 发送通知
        if self.icon:
            self.icon.notify(msg)

        # 强制刷新图标和提示词
        self.update_tray_icon()

        self.logger.info(f"状态切换完成: {msg}")

    # --- 4. 快捷键逻辑 ---
    def start_hotkey(self):
        def listen():
            try:
                with keyboard.GlobalHotKeys({self.hotkey_str: self.toggle_watching}) as h:
                    self.hotkey_listener = h
                    h.join()
            except ValueError as e:
                err_msg = f"快捷键 '{self.hotkey_str}' 格式错误，注册失败！\n请去设置里重新配置。"
                self.logger.error(err_msg)
                if self.icon: self.icon.notify(err_msg, "错误")
            except Exception as e:
                self.logger.error(f"快捷键监听异常: {e}")

        threading.Thread(target=listen, daemon=True).start()

    def stop_hotkey(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None

    def quit_app(self, icon, item):
        if self.icon:
            self.icon.visible = False
            self.icon.stop()
        self.logger.info("用户请求强制退出")
        os._exit(0)


# === 程序入口 ===
if __name__ == "__main__":
    mutex = win32event.CreateMutex(None, False, "Global\\ZenFile_GUI_Lock")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "ZenFile 已经在运行中！\n请检查系统托盘。", "提示", 0x40)
        os._exit(0)

    # 2. 初始化 Tkinter 主窗口 (作为幕后主线程)
    root = tk.Tk()
    root.withdraw()  # 关键：隐藏主窗口

    app = ZenFileApp(root)

    # 3. 在子线程启动托盘
    threading.Thread(target=app.run_tray, daemon=True).start()

    # 4. 进入 Tkinter 主循环
    root.mainloop()