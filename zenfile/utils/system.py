import sys
import os
import winreg

def get_resource_path(relative_path):
    """获取资源文件的绝对路径 (支持打包后)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_exe_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    return sys.argv[0]

# --- Windows 开机自启逻辑 ---
def set_autorun(enable=True):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    exe_path = get_exe_path()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if enable:
            winreg.SetValueEx(key, "ZenFile", 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, "ZenFile")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"自启设置失败: {e}")
        return False

def is_autorun_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "ZenFile")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False