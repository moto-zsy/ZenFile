import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# 👇👇👇 必须加上这一行，否则校验快捷键时会报错 👇👇👇
from pynput.keyboard import HotKey

from src.utils import load_config, save_config
from src.startup import set_autorun, is_autorun_enabled


class SettingsWindow:
    def __init__(self, root, on_save_callback):
        self.root = root
        self.root.title("ZenFile 设置")
        self.root.geometry("500x400")

        # 让窗口居中显示（可选优化）
        self.center_window()

        self.on_save_callback = on_save_callback

        # 强制窗口置顶（防止被其他窗口挡住）
        self.root.attributes('-topmost', True)
        self.root.focus_force()

        # 加载当前配置
        self.config = load_config()

        # === 布局 ===
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab 1: 监控目录
        self.frame_dirs = ttk.Frame(notebook)
        notebook.add(self.frame_dirs, text='监控目录')
        self.setup_dirs_tab()

        # Tab 2: 常规设置 (开机自启 + 快捷键)
        self.frame_general = ttk.Frame(notebook)
        notebook.add(self.frame_general, text='常规设置')
        self.setup_general_tab()

        # 底部按钮
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text="保存并生效", command=self.save_settings).pack(side='right')

    def center_window(self):
        """让弹窗居中显示"""
        self.root.update_idletasks()
        width = 500
        height = 400
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_dirs_tab(self):
        # 列表框
        self.list_box = tk.Listbox(self.frame_dirs, selectmode=tk.SINGLE)
        self.list_box.pack(expand=True, fill='both', padx=5, pady=5)

        # 加载已有目录
        for path in self.config.get("watch_dirs", []):
            self.list_box.insert(tk.END, path)

        # 按钮栏
        btn_bar = ttk.Frame(self.frame_dirs)
        btn_bar.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_bar, text="➕ 添加目录", command=self.add_dir).pack(side='left', padx=2)
        ttk.Button(btn_bar, text="➖ 删除选中", command=self.remove_dir).pack(side='left', padx=2)

    def setup_general_tab(self):
        # 1. 开机自启
        self.var_autorun = tk.BooleanVar(value=is_autorun_enabled())
        chk_autorun = ttk.Checkbutton(self.frame_general, text="开机自动启动 ZenFile", variable=self.var_autorun)
        chk_autorun.pack(anchor='w', padx=20, pady=20)

        # 2. 快捷键设置
        lbl_frame = ttk.LabelFrame(self.frame_general, text="全局快捷键 (暂停/恢复)")
        lbl_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(lbl_frame, text="格式示例: <ctrl>+<alt>+z").pack(anchor='w', padx=10, pady=5)

        self.entry_hotkey = ttk.Entry(lbl_frame)
        self.entry_hotkey.pack(fill='x', padx=10, pady=10)
        # 填入当前快捷键
        current_hotkey = self.config.get("hotkey", "<ctrl>+<alt>+z")
        self.entry_hotkey.insert(0, current_hotkey)

    def add_dir(self):
        path = filedialog.askdirectory()
        if path:
            # 避免重复添加
            current_paths = self.list_box.get(0, tk.END)
            if path not in current_paths:
                self.list_box.insert(tk.END, path)
            # 自动让弹窗重新获得焦点（防止选完目录弹窗跑到后面去）
            self.root.lift()
            self.root.focus_force()

    def remove_dir(self):
        selection = self.list_box.curselection()
        if selection:
            self.list_box.delete(selection[0])

    def save_settings(self):
        # 1. 获取目录列表
        new_dirs = list(self.list_box.get(0, tk.END))
        self.config["watch_dirs"] = new_dirs

        # 2. 获取并校验快捷键
        new_hotkey = self.entry_hotkey.get().strip()
        if not new_hotkey:
            messagebox.showwarning("提示", "快捷键不能为空")
            return

        # === ✅ 校验快捷键格式是否合法 ===
        try:
            HotKey.parse(new_hotkey)
        except Exception:
            messagebox.showerror("格式错误",
                                 "快捷键格式不正确！\n\n"
                                 "正确示例：\n"
                                 "  <ctrl>+<alt>+z\n"
                                 "  <cmd>+<shift>+p\n"
                                 "  <f1>\n\n"
                                 "请务必使用尖括号 <> 包裹功能键，并用 + 连接。")
            return
        # ========================================

        self.config["hotkey"] = new_hotkey

        # 3. 保存文件
        try:
            save_config(self.config)

            # 4. 应用开机自启设置
            set_autorun(self.var_autorun.get())

            # 5. 通知主程序刷新
            if self.on_save_callback:
                self.on_save_callback(self.config)

            messagebox.showinfo("成功", "设置已保存，服务已重启！")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")