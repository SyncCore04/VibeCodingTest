# 回映 Rewind

局域网视频流媒体服务器，在家用手机/平板/电视直接看电脑上的视频，支持断点续播和观看记录。

## 功能特性

- 🎬 **视频播放**：自动扫描指定文件夹及子目录下的 mp4 / mkv / avi，点击即播
- ⏩ **拖动进度条**：正确处理 HTTP Range 请求，手机端可快进快退
- 📱 **响应式设计**：自适应手机屏幕，播放控件大按钮适合触控
- 🔖 **断点续播**：自动记录播放位置，下次打开从上次位置继续
- 📊 **观看记录**：记录每次播放的时长、是否看完，视频列表显示续播/已看完徽章
- 📈 **后台仪表盘**：观看趋势图、最多观看排行、设备管理与标签
- 🔒 **路径安全**：防止目录遍历攻击（`../`）
- 📦 **单文件打包**：PyInstaller 打包成单个 exe，免装 Python

## 快速开始

### 方式一：源码运行

```bash
# 1. 安装依赖
pip install flask

# 2. 启动
python app.py
```

### 方式二：打包成 exe（免装 Python）

```bash
# 双击 打包.bat，或手动执行：
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --name "VideoStreamServer" app.py
# 产物在 dist\VideoStreamServer.exe
```

### 访问

- 播放页：`http://localhost:5000`
- 仪表盘：`http://localhost:5000/admin`
- 手机访问：`http://[电脑局域网IP]:5000`（电脑和手机需在同一 WiFi）

## 配置

### 视频目录

默认扫描 `D:\电视剧`。如需修改，在程序同目录创建 `video_dir.txt`，写入视频文件夹路径：

```
D:\电视剧
```

### 数据库

SQLite 数据库 `rewind.db` 自动创建在程序同目录，无需配置。删除后重启会重建空库。

## 仪表盘说明

访问 `/admin` 查看：

| 模块 | 内容 |
|------|------|
| 统计卡片 | 设备数、播放次数、总观看时长、看完数、看过的视频数 |
| 观看趋势 | 近 14 天每日观看时长柱状图 |
| 视频排行 | 播放次数最多的 Top 10 视频 |
| 设备管理 | 所有访问设备，可打标签（如"客厅电视""我的手机"） |
| 最近观看 | 最近 20 条播放记录 |

## 项目结构

```
Video-in-myphone/
├── app.py                  # 主程序（Flask 服务 + SQLite + API）
├── 启动服务器.bat           # 源码模式一键启动
├── 打包.bat                # PyInstaller 一键打包
├── video_dir.txt           # （可选）自定义视频目录
├── rewind.db               # （运行时生成）SQLite 数据库
├── templates/
│   ├── index.html          # 播放页
│   └── admin.html          # 仪表盘页
└── dist/
    └── VideoStreamServer.exe  # （打包后生成）单文件可执行程序
```

## 技术栈

- **后端**：Python + Flask
- **数据库**：SQLite（Python 内置，零依赖）
- **前端**：原生 HTML5 + CSS + JavaScript
- **图表**：Chart.js（CDN）
- **打包**：PyInstaller

## 注意事项

- MKV 格式部分手机浏览器（如 iOS Safari）原生不支持解码，可能只有声音无画面，MP4 兼容性最好
- 服务器监听 `0.0.0.0:5000`，确保防火墙允许 5000 端口入站
- 仪表盘无密码保护，仅限局域网内使用
- 观看时长为近似统计（每 5 秒上报一次），家用场景足够准确

## License

MIT
