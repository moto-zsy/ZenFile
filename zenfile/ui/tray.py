import pystray
from PIL import Image
import tkinter as tk
from pystray import MenuItem as item
import threading
from zenfile.utils.system import get_resource_path
from .main_window import SettingsWindow


class SystemTray:
    def __init__(self, organizer):
        self.organizer = organizer
        self.icon = None
        self.paused = False

        # 加载图标
        self.icon_image = Image.open(get_resource_path("assets/icons/logo.png"))
        self.pause_image = Image.open(get_resource_path("assets/icons/pause.png"))

    def create_menu(self):
        return pystray.Menu(
            item('设置', self.open_settings),
            item('暂停/恢复', self.toggle_pause, checked=lambda item: self.paused),
            item('退出', self.quit_app)
        )

    def run(self):
        self.icon = pystray.Icon("ZenFile", self.icon_image, "ZenFile (运行中)", self.create_menu())
        self.icon.run()

    def toggle_pause(self, icon, item):
        self.paused = not self.paused
        if self.paused:
            self.icon.icon = self.pause_image
            self.icon.title = "ZenFile (已暂停)"
            # 这里可以通知 organizer 暂停监控 (v1.1暂未实现底层暂停，仅改图标示意)
            # 实际上 Watchdog 是持续运行的，如果要真暂停，可以在 Organizer 里加个标志位
        else:
            self.icon.icon = self.icon_image
            self.icon.title = "ZenFile (运行中)"

    def open_settings(self, icon, item):
        # 启动 Tkinter 窗口
        # 注意：Pystray 运行在独立线程，Tkinter 需要在主线程或独立线程中小心处理
        # 这里我们简单地起一个新线程来跑 Tkinter loop
        t = threading.Thread(target=self._show_settings_window)
        t.start()

    def _show_settings_window(self):
        root = tk.Tk()
        # 传入 organizer 和当前配置
        app = SettingsWindow(root, self.organizer, self.organizer.config)
        root.mainloop()

    def quit_app(self, icon, item):
        self.icon.stop()