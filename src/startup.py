import sys
import winreg
from pathlib import Path

APP_NAME = "ZenFile"


def get_exe_path():
    """获取当前运行的可执行文件路径"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return sys.argv[0]


def set_autorun(enable=True):
    """
    设置或取消开机自启
    原理：修改注册表 HKCU\Software\Microsoft\Windows\CurrentVersion\Run
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    exe_path = get_exe_path()

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            print(f"✅ 已开启开机自启: {exe_path}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                print("✅ 已关闭开机自启")
            except FileNotFoundError:
                pass  # 本来就没开，忽略
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"❌ 设置开机自启失败: {e}")
        return False


def is_autorun_enabled():
    """检查当前是否已开启自启"""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False