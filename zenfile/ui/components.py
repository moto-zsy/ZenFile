import tkinter as tk


class ToolTip:
    """
    通用组件：为按钮或控件添加鼠标悬停提示
    使用方法: ToolTip(widget, "这是一个提示")
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # 去掉窗口边框
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)  # 保证在最顶层

        label = tk.Label(self.tooltip_window, text=self.text,
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("Microsoft YaHei", "9", "normal"))
        label.pack(ipadx=5, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def center_window(root, width=500, height=550):
    """
    通用组件：让窗口在屏幕居中
    """
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f'{width}x{height}+{x}+{y}')