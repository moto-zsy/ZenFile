import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from zenfile.utils.config import save_config
from zenfile.utils.system import set_autorun, is_autorun_enabled
from .components import center_window

class SettingsWindow:
    def __init__(self, root, organizer, current_config):
        self.root = root
        self.organizer = organizer
        self.config = current_config

        self.root.title("ZenFile 设置")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        # 居中显示
        center_window(root)

        # 布局容器
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # 初始化页面
        self.frame_general = ttk.Frame(self.notebook)
        self.frame_watch = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_general, text='常规设置')
        self.notebook.add(self.frame_watch, text='监控目录')

        self.setup_general_tab()
        self.setup_watch_tab()

        # 底部保存按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=20, pady=10)
        ttk.Button(btn_frame, text="保存并应用", command=self.save_settings).pack(side='right')



    def setup_general_tab(self):
        # 1. 开机自启
        self.var_autorun = tk.BooleanVar(value=is_autorun_enabled())
        chk_autorun = ttk.Checkbutton(self.frame_general, text="开机自动启动", variable=self.var_autorun,
                                      command=self.toggle_autorun)
        chk_autorun.pack(anchor='w', padx=20, pady=20)

        # 2. 快捷键设置
        frame_hotkey = ttk.LabelFrame(self.frame_general, text="快捷键 (暂停/恢复)")
        frame_hotkey.pack(fill='x', padx=20, pady=10)

        self.entry_hotkey = ttk.Entry(frame_hotkey)
        self.entry_hotkey.insert(0, self.config.get("hotkey", "<ctrl>+<alt>+z"))
        self.entry_hotkey.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_hotkey, text="* 修改后需重启软件生效", foreground="gray").pack(anchor='w', padx=10, pady=0)

        # --- 新增功能区 ---
        ttk.Separator(self.frame_general, orient='horizontal').pack(fill='x', padx=20, pady=10)

        action_frame = ttk.LabelFrame(self.frame_general, text="手动操作")
        action_frame.pack(fill='x', padx=20, pady=5)

        # 立即整理按钮
        self.btn_run_now = ttk.Button(action_frame, text="🧹 立即整理所有目录", command=self.do_run_now)
        self.btn_run_now.pack(side='left', padx=10, pady=10, expand=True, fill='x')

        # 撤销按钮
        self.btn_undo = ttk.Button(action_frame, text="↩️ 撤销上一步", command=self.do_undo)
        self.btn_undo.pack(side='left', padx=10, pady=10, expand=True, fill='x')

    def setup_watch_tab(self):
        # 目录列表
        self.listbox = tk.Listbox(self.frame_watch, height=15)
        self.listbox.pack(fill='both', expand=True, padx=10, pady=10)

        # 加载已有目录
        for path in self.config.get("watch_dirs", []):
            self.listbox.insert(tk.END, path)

        # 按钮区
        btn_frame = ttk.Frame(self.frame_watch)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="➕ 添加目录", command=self.add_dir).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="➖ 删除选中", command=self.remove_dir).pack(side='left', padx=5)

    # --- 逻辑处理 ---
    def do_run_now(self):
        ans = messagebox.askyesno("确认", "确定要立即整理所有监控目录下的文件吗？")
        if ans:
            count = self.organizer.run_now()
            messagebox.showinfo("完成", f"整理完成！\n共扫描处理了 {count} 个文件。")

    def do_undo(self):
        success, msg = self.organizer.undo_last_action()
        if success:
            messagebox.showinfo("撤销成功", msg)
        else:
            messagebox.showwarning("撤销失败", msg)

    def toggle_autorun(self):
        success = set_autorun(self.var_autorun.get())
        if not success:
            # 如果失败，回滚状态
            self.var_autorun.set(not self.var_autorun.get())
            messagebox.showerror("错误", "无法修改注册表，请尝试以管理员身份运行。")

    def add_dir(self):
        path = filedialog.askdirectory()
        if path:
            # 简单的查重
            current_paths = self.listbox.get(0, tk.END)
            if path not in current_paths:
                self.listbox.insert(tk.END, path)

    def remove_dir(self):
        selection = self.listbox.curselection()
        if selection:
            self.listbox.delete(selection)

    def save_settings(self):
        # 收集数据
        new_watch_dirs = list(self.listbox.get(0, tk.END))
        new_hotkey = self.entry_hotkey.get().strip()

        # 更新配置对象
        self.config["watch_dirs"] = new_watch_dirs
        self.config["hotkey"] = new_hotkey

        # 保存到文件
        save_config(self.config)

        messagebox.showinfo("保存成功", "配置已保存！\n部分设置（如快捷键、新目录监控）可能需要重启软件生效。")
        self.root.destroy()