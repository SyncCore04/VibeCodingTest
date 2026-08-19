# 回映 Rewind 技术文档（学习版）

> 本文档面向有一点编程基础的初学者，逐模块讲解这个局域网视频流媒体服务器是怎么实现的。读完你会理解 Flask 后端、HTTP 视频流、SQLite 数据库、断点续播等核心概念。

---

## 一、项目整体架构

```
┌─────────────────────────────────────────────────┐
│                   浏览器（手机/电脑）               │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 播放页 /  │  │ 仪表盘 /  │  │  HTML5 <video>│  │
│  │   /      │  │  /admin  │  │   播放器       │  │
│  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       │              │                │          │
│       └──────────────┼────────────────┘          │
│                      │ HTTP 请求                  │
└──────────────────────┼───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│                  Flask 后端 (app.py)              │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ 页面路由   │ │ 视频流   │ │  API 接口        │  │
│  │ /  /admin │ │ /video/  │ │ /api/progress 等│  │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │             │                │            │
│       └─────────────┼────────────────┘            │
│                     │                             │
│              ┌──────▼──────┐                      │
│              │  SQLite 数据库 │                     │
│              │  rewind.db   │                     │
│              └─────────────┘                     │
└──────────────────────────────────────────────────┘
```

**核心思路**：浏览器发请求 → Flask 处理 → 读数据库或读视频文件 → 返回响应。就这么简单。

---

## 二、Flask 基础（3 分钟看懂）

Flask 是一个轻量级 Python Web 框架。核心概念只有两个：

### 2.1 路由（Route）

用 `@app.route('/路径')` 装饰器，把一个 URL 绑定到一个 Python 函数：

```python
@app.route('/')
def index():
    return render_template('index.html', videos=videos)
```

用户访问 `http://localhost:5000/` 时，Flask 就会调用 `index()` 函数，把 `index.html` 渲染后返回给浏览器。

### 2.2 模板（Template）

`render_template('index.html', videos=videos)` 会读取 `templates/index.html`，把 `videos` 变量传进去。模板里用 `{{ videos|tojson }}` 把 Python 列表转成 JSON，前端 JS 就能直接用：

```html
<script>
    const videos = {{ videos|tojson }};  // Python 列表 → JS 数组
</script>
```

### 2.3 请求和响应

```python
from flask import request, jsonify

@app.route('/api/progress')
def get_progress():
    video = request.args.get('video')   # 取 URL 参数 ?video=xxx
    return jsonify({'position': 120.5})  # 返回 JSON
```

- `request.args`：GET 请求的 URL 参数
- `request.get_json()`：POST 请求的 JSON body
- `jsonify()`：把字典转成 JSON 响应

---

## 三、视频文件扫描与安全

### 3.1 递归扫描视频

```python
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi'}

def scan_videos(root_dir):
    videos = []
    for dirpath, _, filenames in os.walk(root_dir):  # 递归遍历所有子目录
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)  # 转成相对路径
                videos.append(rel_path.replace('\\', '/'))       # Windows 反斜杠转正斜杠
    return sorted(videos)
```

**为什么用相对路径？** 前端只需要知道相对路径，URL 里用 `/video/相对路径` 就能播放。绝对路径包含 `D:\` 这种信息，不应该暴露给前端。

### 3.2 防止目录遍历攻击

如果用户请求 `/video/../../Windows/system32/config/sam`，不做校验就会读到视频文件夹之外的文件！

```python
def safe_resolve(rel_path):
    normalized = os.path.normpath(rel_path)  # 规范化，把 ../ 解析掉
    if normalized.startswith('..') or os.path.isabs(normalized):
        return None  # 拒绝
    full_path = os.path.abspath(os.path.join(VIDEO_ROOT, normalized))
    root_abs = os.path.abspath(VIDEO_ROOT)
    if not full_path.startswith(root_abs + os.sep):
        return None  # 解析后不在根目录内，拒绝
    return full_path
```

**关键步骤**：
1. `os.path.normpath()` 把 `a/../b` 变成 `b`，把隐藏的 `..` 暴露出来
2. 检查是否以 `..` 开头或是否是绝对路径
3. 拼接后再 `os.path.abspath()` 取绝对路径，确认在根目录内

---

## 四、视频流式播放与 HTTP Range

### 4.1 为什么需要 Range？

普通的文件下载是一次性把整个文件发出去。但视频播放需要：
- 拖动进度条跳到第 30 分钟
- 不需要先下载整个文件才能播放

HTTP 协议用 `Range` 请求头解决这个问题：

```
请求头：
Range: bytes=1048576-2097151    ← 我要第 1MB 到第 2MB 的数据

响应头：
HTTP/1.1 206 Partial Content    ← 206 表示"部分内容"
Content-Range: bytes 1048576-2097151/52428800
Content-Length: 1048576
```

浏览器拖动进度条时，会自动发 Range 请求，服务器返回对应片段（状态码 206）。

### 4.2 Flask 的实现

```python
@app.route('/video/<path:filename>')
def video(filename):
    full_path = safe_resolve(filename)
    return send_file(full_path, mimetype='video/mp4', conditional=True)
```

**`conditional=True` 是关键**：它告诉 Flask 检查请求中的 `Range`、`If-Modified-Since` 等条件头，自动返回 206 部分内容。没有这个参数，Flask 会返回完整文件（200），手机就无法拖动进度条。

`<path:filename>` 中的 `path` 转换器允许文件名包含斜杠（子目录路径）。

---

## 五、SQLite 数据库设计

### 5.1 为什么选 SQLite？

- Python 内置 `sqlite3` 模块，**零安装零配置**
- 整个数据库就是一个文件 `rewind.db`，备份复制都方便
- 家用场景并发量极低，SQLite 完全够用

### 5.2 三张表的设计

```sql
-- 设备表：记录每个访问过的设备
CREATE TABLE devices (
    id          TEXT PRIMARY KEY,   -- UUID，存在浏览器 Cookie 里
    tag         TEXT,               -- 用户给设备起的名字（如"客厅电视"）
    ip          TEXT,               -- 局域网 IP
    user_agent  TEXT,               -- 浏览器标识
    first_seen  TEXT,               -- 首次访问时间
    last_seen   TEXT                -- 最近访问时间
);

-- 进度表：每个设备+每个视频只有一条最新记录
CREATE TABLE progress (
    device_id   TEXT,
    video_path  TEXT,
    position    REAL,               -- 当前播放位置（秒）
    duration    REAL,               -- 视频总时长（秒）
    updated_at  TEXT,
    PRIMARY KEY (device_id, video_path)  -- 联合主键
);

-- 观看会话表：每次播放算一条历史记录
CREATE TABLE watch_sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id   TEXT,
    video_path  TEXT,
    started_at  TEXT,               -- 开始时间
    ended_at    TEXT,               -- 结束时间
    watched_sec REAL DEFAULT 0,     -- 本次观看时长（秒）
    completed   INTEGER DEFAULT 0   -- 是否看完（0=否，1=是）
);
```

**为什么进度和会话分两张表？**
- `progress` 只关心"最新位置"，频繁更新（每 5 秒一次），用于断点续播
- `watch_sessions` 是追加写入（每次播放新增一条），用于统计和历史记录
- 混在一起会导致历史记录被覆盖

### 5.3 Flask 中使用 SQLite

```python
import sqlite3
from flask import g

def get_db():
    if 'db' not in g:                    # g 是 Flask 的请求级全局变量
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row   # 让查询结果可以用列名访问
        g.db.execute("PRAGMA journal_mode=WAL")  # WAL 模式，读写不互锁
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db: db.close()
```

**要点**：
- `g` 是 Flask 提供的请求上下文变量，同一个请求内共享，请求结束自动销毁
- `teardown_appcontext` 装饰器在请求结束时自动关闭数据库连接
- WAL 模式（Write-Ahead Logging）让读和写可以同时进行，不会互相阻塞

### 5.4 UPSERT（存在则更新，不存在则插入）

保存进度时，如果这个设备+视频已有记录就更新，没有就插入：

```python
db.execute("""
    INSERT INTO progress (device_id, video_path, position, duration, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(device_id, video_path) DO UPDATE SET position=?, duration=?, updated_at=?
""", (device_id, video, position, duration, now, position, duration, now))
```

`?` 是参数化查询，**千万不要用字符串拼接 SQL**，否则会有 SQL 注入风险。

---

## 六、设备识别（无登录系统）

### 6.1 问题

没有用户注册登录，怎么知道"谁在看"？

- 用 IP？家用路由器 DHCP 会变 IP
- 用 User-Agent？同一个浏览器的 UA 都一样，区分不了两个人

### 6.2 方案：Cookie + UUID

```python
import uuid
from flask import request, make_response

@app.before_request          # 每个请求之前都执行
def identify_device():
    device_id = request.cookies.get('device_id')
    if not device_id:
        device_id = str(uuid.uuid4())  # 生成随机唯一ID
        g.new_device = True
    g.device_id = device_id
    # ... 存入或更新数据库 ...

@app.after_request           # 每个响应返回前执行
def set_device_cookie(response):
    if getattr(g, 'new_device', False):
        response.set_cookie('device_id', g.device_id, max_age=315360000)  # 10年
    return response
```

**流程**：
1. 浏览器第一次访问，没有 `device_id` Cookie
2. 后端生成 UUID，通过 `Set-Cookie` 响应头写回浏览器
3. 之后每次请求浏览器自动带上这个 Cookie
4. 后端根据 Cookie 识别设备

`@before_request` 和 `@after_request` 是 Flask 的钩子函数，分别在请求处理前和响应返回前自动执行。

---

## 七、断点续播的实现

### 7.1 整体流程

```
用户点击视频
    │
    ▼
前端 POST /api/play {video, duration}  →  后端创建 watch_session，返回 session_id
    │
    ▼
视频加载元数据后，GET /api/progress?video=xxx  →  拿到上次播放位置
    │
    ▼
video.currentTime = savedPosition  →  自动跳到上次位置
    │
    ▼
播放中，每 5 秒 POST /api/progress {video, position, duration, session_id}
    │  → 后端更新 progress 表 + 给 watch_session 的 watched_sec 加 5
    ▼
视频结束 / 页面关闭  →  POST /api/end {session_id}  →  标记会话结束
```

### 7.2 前端进度上报

```javascript
let lastProgressSend = 0;

player.addEventListener('timeupdate', () => {
    const now = Date.now();
    // 每 5 秒上报一次，且只在播放中（非暂停）时上报
    if (!player.paused && !player.ended && now - lastProgressSend >= 5000) {
        lastProgressSend = now;
        fetch('/api/progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video: currentVideo,
                position: player.currentTime,
                duration: player.duration,
                session_id: currentSession
            })
        });
    }
});
```

`timeupdate` 事件在视频播放时高频触发（约每秒 4 次），我们用时间戳节流到每 5 秒一次，避免频繁写数据库。

### 7.3 页面关闭时保存

`beforeunload` 事件中用 `fetch` 不可靠（页面可能在请求完成前就关了），要用 `navigator.sendBeacon()`：

```javascript
window.addEventListener('beforeunload', () => {
    const data = new Blob(
        [JSON.stringify({ session_id: currentSession, position: player.currentTime })],
        { type: 'application/json' }
    );
    navigator.sendBeacon('/api/end', data);  // 浏览器保证发送完成
});
```

`sendBeacon` 是浏览器专门为"页面关闭前发数据"设计的 API，它会异步发送且保证不阻塞页面关闭。

### 7.4 自动续播

```javascript
player.addEventListener('loadedmetadata', async () => {
    const res = await fetch(`/api/progress?video=${encodeURIComponent(videoPath)}`);
    const data = await res.json();
    if (data.position > 5) {  // 超过 5 秒才续播，避免从 0 开始也弹提示
        player.currentTime = data.position;
        showToast(`已从 ${fmtTime(data.position)} 续播`);
    }
});
```

`loadedmetadata` 事件在视频元数据（时长、尺寸等）加载完成后触发，此时才能设置 `currentTime`。

---

## 八、仪表盘数据聚合

仪表盘的数据都是 SQL 聚合查询，举几个例子：

### 8.1 最多观看的视频

```sql
SELECT video_path, COUNT(*) AS play_count, SUM(watched_sec) AS total_sec
FROM watch_sessions
GROUP BY video_path
ORDER BY play_count DESC
LIMIT 10
```

`GROUP BY` 按视频分组，`COUNT(*)` 算播放次数，`SUM(watched_sec)` 算总观看时长。

### 8.2 近 14 天观看趋势

```sql
SELECT DATE(started_at) AS day, COUNT(*) AS cnt, SUM(watched_sec) AS sec
FROM watch_sessions
WHERE started_at >= date('now', '-14 days')
GROUP BY day
ORDER BY day
```

`DATE()` 把时间戳截成日期，`date('now', '-14 days')` 是 SQLite 内置的日期计算函数。

### 8.3 设备统计（关联子查询）

```sql
SELECT d.*,
    (SELECT COUNT(*) FROM watch_sessions WHERE device_id = d.id) AS play_count,
    (SELECT SUM(watched_sec) FROM watch_sessions WHERE device_id = d.id) AS total_sec
FROM devices d
ORDER BY d.last_seen DESC
```

用子查询给每个设备算出播放次数和总时长。也可以用 `JOIN + GROUP BY`，但子查询写法更直观。

---

## 九、响应式前端设计

### 9.1 移动端适配三要素

```html
<!-- 1. viewport：告诉浏览器按设备宽度渲染，不要缩放 -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

```css
/* 2. 流式布局：用 max-width + margin: 0 auto，小屏自动填满 */
.container { max-width: 900px; margin: 0 auto; padding: 16px; }

/* 3. 媒体查询：小屏幕调整字号和间距 */
@media (max-width: 480px) {
    .container { padding: 12px; }
    header h1 { font-size: 1.2rem; }
}
```

### 9.2 大触控按钮

```css
.video-list a {
    min-height: 52px;   /* 至少 52px 高，苹果推荐触控区域不小于 44px */
    padding: 14px 16px;
}
```

### 9.3 视频列表徽章

每个视频项根据进度显示不同徽章：
- 进度 > 0 且 < 90%：显示"续播 23:15"（橙色）
- 进度 >= 90%：显示"✓ 已看完"（绿色）
- 无进度：不显示徽章

数据来自页面加载时的 `GET /api/progress/all`，一次性拿到本设备所有视频的进度。

---

## 十、PyInstaller 打包

### 10.1 打包命令

```bash
pyinstaller --onefile --add-data "templates;templates" --name "VideoStreamServer" app.py
```

| 参数 | 作用 |
|------|------|
| `--onefile` | 打包成单个 exe 文件 |
| `--add-data "templates;templates"` | 把 templates 文件夹打包进去（Windows 用分号分隔源和目标） |
| `--name` | 输出文件名 |

### 10.2 打包后的路径问题

打包后运行时，PyInstaller 会把文件解压到一个临时目录 `_MEIPASS`，模板文件在那里。代码需要判断：

```python
import sys, os

if getattr(sys, 'frozen', False):  # 打包后运行
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
    BASE_DIR = os.path.dirname(sys.executable)  # exe 所在目录（数据库放这里）
else:  # 源码运行
    app = Flask(__name__)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

**关键区分**：
- `sys._MEIPASS`：临时解压目录，模板等只读资源放这里
- `sys.executable`：exe 本身的路径，其目录用于存放数据库、配置文件等**需要写入**的文件

数据库绝对不能放 `_MEIPASS`，因为程序关闭后临时目录会被清理，数据就丢了。

---

## 十一、安全清单

| 风险 | 防护措施 |
|------|---------|
| 目录遍历（`../`） | `safe_resolve()` 规范化路径 + 根目录校验 |
| SQL 注入 | 全部使用参数化查询 `?`，不拼接 SQL |
| 未授权访问仪表盘 | 家用局域网内使用，如需公网暴露应加密码 |
| 敏感信息泄露 | 前端只传相对路径，不传绝对路径 |
| 端口暴露 | 仅监听 0.0.0.0:5000，需防火墙配合限制入站 |

---

## 十二、可以继续学习的方向

1. **给仪表盘加密码**：Flask 的 `session` + 简单登录表单
2. **支持更多格式**：用 `ffmpeg` 实时转码（需要 `ffmpeg-python`）
3. **视频缩略图**：用 `ffmpeg` 截取首帧作为列表封面
4. **搜索优化**：当前是前端过滤，视频多了可以做后端全文搜索
5. **用户系统**：多用户账号，每个用户有独立的观看记录
6. **WebSocket 实时通知**：有人开始播放时仪表盘实时刷新

---

> 读懂这份文档后，你已经掌握了 Flask Web 开发、HTTP 流媒体、SQLite 数据库、前端交互、软件打包的完整链路。这是一个很好的全栈入门项目。
