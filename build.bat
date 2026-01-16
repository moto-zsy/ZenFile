@echo off
chcp 65001
echo ========================================================
echo          正在开始打包 ZenFile (v1.1.0)...
echo ========================================================

:: 1. 清理旧的构建文件 (防止缓存导致的问题)
if exist "build" (
    echo [1/3] 正在清理 build 文件夹...
    rmdir /s /q "build"
)
if exist "dist" (
    echo [2/3] 正在清理 dist 文件夹...
    rmdir /s /q "dist"
)
if exist "*.spec" (
    del /f /q "*.spec"
)

:: 2. 执行 PyInstaller 打包命令
echo [3/3] 正在执行 PyInstaller...
echo.

:: 修改说明：
:: 1. 移除了 pynput (新架构暂未启用全局快捷键监听)
:: 2. 增加了 zenfile (核心包), pystray (托盘), PIL (图标处理)
:: 3. 增加了 --clean (清理缓存)

pyinstaller -F -w -n ZenFile ^
    --clean ^
    --icon="assets\icons\logo.ico" ^
    --add-data="assets;assets" ^
    --hidden-import zenfile ^
    --hidden-import pystray ^
    --hidden-import PIL ^
    --hidden-import tkinter ^
main.py

:: 3. 完成提示
if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo             ✅ 打包成功！
    echo      可执行文件位置: dist\ZenFile.exe
    echo ========================================================
    :: 自动打开生成目录
    start explorer dist
) else (
    echo.
    echo ========================================================
    echo             ❌ 打包失败，请检查错误信息。
    echo ========================================================
    pause
)

pause