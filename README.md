# 🍃 ZenFile (v1.0.0)

**让您的桌面重归宁静。**

ZenFile 是一款轻量级的 Windows 桌面文件自动整理工具。它在后台静默运行，根据预设规则将杂乱的文件自动归类到相应的文件夹中，助您保持工作环境的高效与整洁。

---

## ✨ 核心功能

* **🕵️‍♂️ 多目录实时监控**：同时监控“桌面”、“下载”等多个文件夹，毫秒级响应文件的创建与移动。
* **📂 智能自动归类**：自动在监控目录下创建分类文件夹（如 `01_图片`, `02_文档`），并将文件移动进去。
* **🧩 智能防冲突**：移动时如果遇到同名文件，自动重命名（例如 `file_1.txt`），绝不覆盖原有数据。
* **🔇 静默运行**：启动后最小化至系统托盘，不占用任务栏。
    * 🔵 **蓝色图标**：运行中。
    * ⚪ **灰色图标**：已暂停。
* **⚡ 全局快捷键**：默认使用 `<ctrl>+<alt>+z` 一键暂停/恢复整理，方便临时操作文件。
* **⌨️ 智能录制**：设置界面支持键盘按键录制，轻松自定义您喜欢的快捷键。
* **🚀 开机自启**：支持跟随 Windows 系统启动，无需手动打开。
* **🛡️ 单例保护**：防止程序重复开启，确保资源占用最小化。

---

## 🛠️ 安装与运行

### 方式一：直接运行 (推荐普通用户)
下载打包好的 `ZenFile.exe`，双击即可运行。
* 程序启动后会自动隐藏到右下角系统托盘。
* 首次运行默认监控路径为空，请在设置中添加。

### 方式二：源码运行 (开发人员)

1.  **克隆项目**
    ```bash
    git clone https://github.com/moto-zsy/ZenFile
    cd ZenFile
    ```

2.  **安装依赖**
    ```bash
    pip install watchdog pystray pynput Pillow pywin32
    ```

3.  **运行**
    ```bash
    python main.py
    ```

---

## 📖 使用指南

### 1. 添加监控目录
1.  在任务栏右下角找到 ZenFile 图标（可能在折叠菜单 `^` 里）。
2.  **右键图标** -> 选择 **“设置”**。
3.  在 **“监控目录”** 标签页，点击 **“➕ 添加目录”**。
4.  选择您需要整理的文件夹（例如 Desktop 或 Downloads）。
5.  点击 **“保存并生效”**。

### 2. 暂停/恢复整理
当您正在下载文件或需要临时在桌面上处理文件时，可以暂停自动整理：
* **快捷键**：按下 `ctrl+alt+z`（默认）。
* **托盘菜单**：左键点击托盘图标，或右键选择状态切换。
* **状态指示**：
    * **运行中**：文件会被立即移走。
    * **已暂停**：文件保留在原地。

### 3. 修改设置
在设置面板的 **“常规设置”** 中，您可以：
* 开启/关闭 **开机自动启动**。
* 自定义 **全局快捷键**（点击输入框并按下键盘组合键即可自动录制）。

---

## ⚙️ 默认整理规则

目前 v1.0.0 版本内置了以下文件分类规则（可在 `utils.py` 中修改）：

| 📂 目标文件夹 | 📝 包含的文件类型 (后缀) |
| :--- | :--- |
| **🖼️ 01_图片** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg` |
| **📄 02_文档** | `.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.xlsx`, `.xls`, `.pptx`, `.ppt` |
| **🎥 03_视频** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv` |
| **🎵 04_音频** | `.mp3`, `.wav`, `.flac`, `.m4a`, `.aac` |
| **📦 05_压缩包** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| **💿 06_安装包** | `.exe`, `.msi`, `.iso` |
| **💻 07_代码** | `.py`, `.java`, `.html`, `.css`, `.js`, `.json`, `.sql` |
| **🏷️ 99_其他** | 不符合上述规则的其他所有文件 |

*注：临时文件（如 `.tmp`, `.crdownload`）及隐藏文件（`.` 开头）会被自动忽略。*

---

## 🏗️ 项目结构

```text
ZenFile/
│
├── zenfile/                 # 📦 将 src 改名为项目名，作为核心包
│   ├── __init__.py          # 暴露关键接口
│   │
│   ├── core/                # 🧠 核心业务层 (Business Logic)
│   │   ├── __init__.py
│   │   ├── organizer.py     # 原 core.py 的核心：负责文件移动、重命名
│   │   ├── monitor.py       # 专门负责 Watchdog 监控逻辑
│   │   ├── rules.py         # 专门负责“关键词匹配”、“后缀判断” (RuleManager)
│   │   └── history.py       # 专门负责“撤销”、“记录” (HistoryManager)
│   │
│   ├── ui/                  # 🎨 界面层 (Presentation)
│   │   ├── __init__.py
│   │   ├── main_window.py   # 主窗口 UI 代码
│   │   ├── tray.py          # 系统托盘相关代码 (Pystray)
│   │   └── components.py    # 通用组件 (如按钮、弹窗)
│   │
│   └── utils/               # 🔧 基础设施层 (Infrastructure)
│       ├── __init__.py
│       ├── config.py        # 配置加载与保存
│       ├── logger.py        # 日志系统
│       └── system.py        # 开机自启、路径获取、权限检查
│
├── tests/                   # 🧪 测试目录 (专业项目标配)
│   ├── test_rules.py        # 测试规则匹配是否准确
│   └── test_organizer.py    # 测试文件移动是否正常
│
├── config/                  # 外部资源
├── logs/
├── main.py                  # 🚀 启动入口 (保持极简)
├── requirements.txt
└── README.md
```

## 📦 打包命令 (PyInstaller)

如果您修改了代码并希望重新打包成 EXE，请使用以下命令：

```bash
pyinstaller -F -w -n ZenFile ^
    --icon="assets\icons\logo.ico" ^
    --add-data="assets;assets" ^
    --hidden-import pynput.keyboard._win32 ^
    --hidden-import pynput.mouse._win32 ^
    --hidden-import tkinter ^
main.py
```

参数说明：

* -F: 打包成单个 EXE 文件。

* -w: 无控制台模式（不显示黑框）。

* --add-data: 将 assets 文件夹打包进 EXE 内部。

* --hidden-import: 强制引入隐式调用的库，防止运行报错。


## 📝 版本历史

* v1.0.0 (2026-01-15)

    * 🎉 初始版本发布。

    * 实现核心监控、自动分类功能。

    * 实现系统托盘交互与全局快捷键控制。

    * 支持开机自启与配置持久化。
    
## 📄 License

This project is licensed under the [MIT License](LICENSE).
