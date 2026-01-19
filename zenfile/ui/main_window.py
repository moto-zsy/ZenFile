import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from zenfile.utils.config import save_config
from zenfile.utils.system import set_autorun, is_autorun_enabled
from zenfile.core.history import HistoryManager
from .components import center_window, HotkeyRecorder


class SettingsWindow:
    def __init__(self, window, organizer, monitor_mgr, hotkey_mgr):
        # 1. 基础窗口设置
        self.window = window
        self.organizer = organizer
        self.monitor_mgr = monitor_mgr
        self.hotkey_mgr = hotkey_mgr
        self.config = organizer.config

        self.window.title("ZenFile 控制台")
        center_window(self.window, 700, 500)  # 稍微调大一点，适合现代布局
        self.window.resizable(True, True)  # 允许调整大小

        # 如果传入的是普通 tk 窗口，尝试应用 ttkbootstrap 样式
        # 注意：通常需要在 main.py 引入 style，这里做局部美化
        self.style = ttk.Style("cosmo")  # 可选主题: cosmo, flatly, journal, superhero(黑), darkly(黑)

        # 2. 布局容器
        # 主容器：左右分栏
        self.main_container = ttk.Frame(self.window, padding=0)
        self.main_container.pack(fill=BOTH, expand=YES)

        # 左侧：侧边导航栏
        self.sidebar = ttk.Frame(self.main_container, width=180, bootstyle="light")
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)  # 固定宽度

        # 右侧：内容显示区
        self.content_area = ttk.Frame(self.main_container, padding=20)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=YES)

        # 3. 初始化导航和页面
        self.pages = {}  # 存储所有页面实例
        self.current_page = None

        self.setup_sidebar()
        self.setup_pages()

        # 默认显示第一页
        self.switch_to("dashboard")

    def setup_sidebar(self):
        """构建侧边栏菜单"""
        # APP 标题/Logo区
        title_lbl = ttk.Label(
            self.sidebar,
            text="ZenFile",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        title_lbl.pack(pady=20, padx=10)

        # 导航按钮 (使用函数封装，方便扩展)
        self.create_nav_btn("🏠 仪表盘", "dashboard")
        self.create_nav_btn("📂 目录监控", "dirs")
        self.create_nav_btn("📝 操作日志", "logs")
        self.create_nav_btn("⚙️ 系统设置", "settings")

        # 底部保存按钮
        ttk.Separator(self.sidebar).pack(side=BOTTOM, fill=X, pady=10)
        save_btn = ttk.Button(
            self.sidebar,
            text="保存并生效",
            command=self.save,
            bootstyle="success"
        )
        save_btn.pack(side=BOTTOM, fill=X, padx=10, pady=10)

    def create_nav_btn(self, text, page_key):
        """创建统一风格的导航按钮"""
        btn = ttk.Button(
            self.sidebar,
            text=text,
            bootstyle="link",
            command=lambda: self.switch_to(page_key)
        )
        btn.pack(fill=X, pady=2, padx=5)

    def setup_pages(self):
        """初始化所有功能页面"""
        # 页面 1: 仪表盘 (Dashboard)
        f_dash = ttk.Frame(self.content_area)
        self.build_dashboard_page(f_dash)
        self.pages["dashboard"] = f_dash

        # 页面 2: 目录管理 (Dirs)
        f_dirs = ttk.Frame(self.content_area)
        self.build_dirs_page(f_dirs)
        self.pages["dirs"] = f_dirs

        # 页面 3: 日志 (Dirs)
        f_logs = ttk.Frame(self.content_area)
        self.build_logs_page(f_logs)
        self.pages["logs"] = f_logs

        # 页面 4: 设置 (Settings)
        f_set = ttk.Frame(self.content_area)
        self.build_settings_page(f_set)
        self.pages["settings"] = f_set

    def switch_to(self, page_key):
        """切换页面逻辑"""
        # 隐藏当前页面
        if self.current_page:
            self.current_page.pack_forget()



        # 显示新页面
        frame = self.pages.get(page_key)
        if frame:
            frame.pack(fill=BOTH, expand=YES)
            self.current_page = frame
            if page_key == "logs":
                self.refresh_logs()

    # --- 页面构建具体逻辑 ---
    def build_logs_page(self, parent):
            """构建日志表格页面"""
            # 顶部工具栏
            header_frame = ttk.Frame(parent)
            header_frame.pack(fill=X, pady=(0, 10))
            ttk.Label(header_frame, text="历史记录 (最近100条)", font=("Helvetica", 16, "bold")).pack(side=LEFT)
            ttk.Button(header_frame, text="刷新", bootstyle="info-outline", command=self.refresh_logs).pack(side=RIGHT)

            # 表格区域
            table_frame = ttk.Frame(parent)
            table_frame.pack(fill=BOTH, expand=YES)

            columns = ("time", "action", "source", "target")
            self.log_tree = ttk.Treeview(table_frame, columns=columns, show="headings", bootstyle="primary")

            self.log_tree.heading("time", text="时间")
            self.log_tree.heading("action", text="类型")
            self.log_tree.heading("source", text="源文件")
            self.log_tree.heading("target", text="目标位置")

            self.log_tree.column("time", width=140, anchor="w")
            self.log_tree.column("action", width=80, anchor="center")
            self.log_tree.column("source", width=200, anchor="w")
            self.log_tree.column("target", width=200, anchor="w")

            # 滚动条
            ysb = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.log_tree.yview)
            xsb = ttk.Scrollbar(table_frame, orient=HORIZONTAL, command=self.log_tree.xview)
            self.log_tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

            ysb.pack(side=RIGHT, fill=Y)
            xsb.pack(side=BOTTOM, fill=X)
            self.log_tree.pack(fill=BOTH, expand=YES)

    def refresh_logs(self):
            """刷新日志数据"""
            # 1. 清空表格
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)

            try:
                # 2. 读取并倒序
                history = HistoryManager.load_history()  # 这里调用了我们在 HistoryManager 加的别名
                if not history: return

                # 3. 填充数据 (最新的在最上面)
                for rec in reversed(history):
                    self.log_tree.insert("", "end", values=(
                        rec.get("time", ""),
                        "整理",  # 暂时统一显示整理
                        rec.get("source", ""),
                        rec.get("target", "")
                    ))
            except Exception as e:
                print(f"日志加载错误: {e}")

    def build_dashboard_page(self, parent):
        ttk.Label(parent, text="操作中心", font=("Helvetica", 14, "bold")).pack(anchor=W, pady=(0, 20))

        # 卡片式布局：状态卡片
        status_frame = ttk.Labelframe(parent, text="当前状态", padding=15)
        status_frame.pack(fill=X, pady=10)

        state_text = "⏸ 已暂停" if self.organizer.paused else "▶ 正在运行"
        state_color = "danger" if self.organizer.paused else "success"
        ttk.Label(status_frame, text=state_text, font=("Helvetica", 12), bootstyle=state_color).pack(anchor=W)

        # 卡片式布局：快捷操作
        action_frame = ttk.Labelframe(parent, text="快捷操作", padding=15)
        action_frame.pack(fill=X, pady=10)

        col = ttk.Frame(action_frame)
        col.pack(fill=X)

        b1 = ttk.Button(col, text="立即整理所有文件", bootstyle="primary-outline", command=self.run_now)
        b1.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        b2 = ttk.Button(col, text="撤销上一次操作", bootstyle="warning-outline", command=self.undo)
        b2.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

    def build_dirs_page(self, parent):
        ttk.Label(parent, text="监控目录管理", font=("Helvetica", 14, "bold")).pack(anchor=W, pady=(0, 10))

        # 列表与滚动条
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=BOTH, expand=YES)

        self.lb = tk.Listbox(list_frame, height=10, borderwidth=0, highlightthickness=0, bg="#f8f9fa",
                             font=("Consolas", 10))
        self.lb.pack(side=LEFT, fill=BOTH, expand=YES)

        scroll = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.lb.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.lb.config(yscrollcommand=scroll.set)

        # 加载数据
        for p in self.config.get("watch_dirs", []):
            self.lb.insert(tk.END, p)

        # 按钮栏
        btn_bar = ttk.Frame(parent, padding=(0, 10))
        btn_bar.pack(fill=X)
        ttk.Button(btn_bar, text="+ 添加目录", bootstyle="success-link", command=self.add).pack(side=LEFT)
        ttk.Button(btn_bar, text="- 删除选中", bootstyle="danger-link", command=self.rem).pack(side=RIGHT)

    def build_settings_page(self, parent):
        ttk.Label(parent, text="常规设置", font=("Helvetica", 14, "bold")).pack(anchor=W, pady=(0, 20))

        # 开机自启
        self.v_run = tk.BooleanVar(value=is_autorun_enabled())
        chk = ttk.Checkbutton(
            parent,
            text=" 开机自动启动 ZenFile",
            variable=self.v_run,
            command=self.tog_run,
            bootstyle="round-toggle"  # 变成开关样式
        )
        chk.pack(anchor=W, pady=10)

        ttk.Separator(parent).pack(fill=X, pady=15)

        # 快捷键设置
        ttk.Label(parent, text="全局快捷键 (暂停/恢复)", bootstyle="secondary").pack(anchor=W)
        self.hk = HotkeyRecorder(parent, default_value=self.config.get("hotkey", "<ctrl>+<alt>+z"))
        self.hk.pack(fill=X, pady=5)
        ttk.Label(parent, text="* 点击输入框后直接按下组合键即可录制", font=("Arial", 8), bootstyle="secondary").pack(anchor=W)

    # --- 原有业务逻辑保持不变 ---

    def run_now(self):
        c = self.organizer.run_now()
        messagebox.showinfo("完成", f"已立即处理 {c} 个文件")
        self.refresh_logs()

    def undo(self):
        s, m = self.organizer.undo_last_action()
        messagebox.showinfo("操作结果", m)
        self.refresh_logs()

    def tog_run(self):
        if not set_autorun(self.v_run.get()):
            self.v_run.set(not self.v_run.get())
            messagebox.showerror("错误", "权限不足，请以管理员身份运行")

    def add(self):
        p = filedialog.askdirectory()
        if p and p not in self.lb.get(0, tk.END): self.lb.insert(tk.END, p)

    def rem(self):
        s = self.lb.curselection()
        if s: self.lb.delete(s)

    def save(self):
        dirs = list(self.lb.get(0, tk.END))
        hk = self.hk.get_hotkey()

        # 更新配置
        self.config.update({"watch_dirs": dirs, "hotkey": hk})
        save_config(self.config)

        # 触发各模块重载
        self.organizer.reload_config(self.config)
        self.monitor_mgr.update_watches(dirs)
        self.hotkey_mgr.restart(hk)

        messagebox.showinfo("保存成功", "配置已更新并立即生效")
        self.window.destroy()