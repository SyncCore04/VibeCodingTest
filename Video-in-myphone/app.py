import os
import sys
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template, send_file, abort, request, g, jsonify

# ==================== 路径配置 ====================
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    app = Flask(__name__)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 视频根目录：优先读同目录 video_dir.txt，否则默认
DEFAULT_VIDEO_ROOT = r"D:\电视剧"
CONFIG_FILE = os.path.join(BASE_DIR, "video_dir.txt")
if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        VIDEO_ROOT = f.read().strip() or DEFAULT_VIDEO_ROOT
else:
    VIDEO_ROOT = DEFAULT_VIDEO_ROOT

DB_PATH = os.path.join(BASE_DIR, "rewind.db")

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi'}
MIME_TYPES = {
    '.mp4': 'video/mp4',
    '.mkv': 'video/x-matroska',
    '.avi': 'video/x-msvideo',
}

# ==================== 数据库 ====================
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id          TEXT PRIMARY KEY,
            tag         TEXT,
            ip          TEXT,
            user_agent  TEXT,
            first_seen  TEXT,
            last_seen   TEXT
        );
        CREATE TABLE IF NOT EXISTS progress (
            device_id   TEXT,
            video_path  TEXT,
            position    REAL,
            duration    REAL,
            updated_at  TEXT,
            PRIMARY KEY (device_id, video_path)
        );
        CREATE TABLE IF NOT EXISTS watch_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id   TEXT,
            video_path  TEXT,
            started_at  TEXT,
            ended_at    TEXT,
            watched_sec REAL DEFAULT 0,
            completed   INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_device ON watch_sessions(device_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_video  ON watch_sessions(video_path);
    """)
    conn.commit()
    conn.close()

# ==================== 设备识别中间件 ====================
@app.before_request
def identify_device():
    device_id = request.cookies.get('device_id')
    now = datetime.now().isoformat()
    ip = request.remote_addr
    ua = request.user_agent.string

    db = get_db()

    if not device_id:
        # 无 Cookie：先尝试通过 IP + User-Agent 匹配最近的设备
        # 解决首次访问时多个并发请求各自生成新设备的竞态问题
        # 同时兼容不持久化 Cookie 的嵌入式浏览器（如电视盒子）
        existing = db.execute(
            "SELECT id FROM devices WHERE ip = ? AND user_agent = ? ORDER BY last_seen DESC LIMIT 1",
            (ip, ua)
        ).fetchone()
        if existing:
            device_id = existing['id']
            g.new_device = False
        else:
            device_id = str(uuid.uuid4())
            g.new_device = True
    else:
        g.new_device = False

    g.device_id = device_id

    existing = db.execute("SELECT id FROM devices WHERE id = ?", (device_id,)).fetchone()
    if existing:
        db.execute(
            "UPDATE devices SET last_seen=?, ip=?, user_agent=? WHERE id=?",
            (now, ip, ua, device_id)
        )
    else:
        db.execute(
            "INSERT INTO devices (id, tag, ip, user_agent, first_seen, last_seen) VALUES (?,?,?,?,?,?)",
            (device_id, None, ip, ua, now, now)
        )
    db.commit()

@app.after_request
def set_device_cookie(response):
    if getattr(g, 'new_device', False):
        response.set_cookie('device_id', g.device_id, max_age=315360000, samesite='Lax')
    return response

# ==================== 工具函数 ====================
def scan_videos(root_dir):
    videos = []
    if not os.path.isdir(root_dir):
        return videos
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
                videos.append(rel_path)
    videos.sort(key=lambda x: x.lower())
    return videos

def safe_resolve(rel_path):
    if not rel_path:
        return None
    normalized = os.path.normpath(rel_path)
    if normalized.startswith('..') or os.path.isabs(normalized):
        return None
    full_path = os.path.abspath(os.path.join(VIDEO_ROOT, normalized))
    root_abs = os.path.abspath(VIDEO_ROOT)
    if not full_path.startswith(root_abs + os.sep) and full_path != root_abs:
        return None
    return full_path

# ==================== 页面路由 ====================
@app.route('/')
def index():
    videos = scan_videos(VIDEO_ROOT)
    return render_template('index.html', videos=videos)

@app.route('/admin')
def admin():
    return render_template('admin.html')

# ==================== 视频流 ====================
@app.route('/video/<path:filename>')
def video(filename):
    full_path = safe_resolve(filename)
    if full_path is None or not os.path.isfile(full_path):
        abort(404)
    ext = os.path.splitext(full_path)[1].lower()
    mimetype = MIME_TYPES.get(ext, 'application/octet-stream')
    return send_file(full_path, mimetype=mimetype, conditional=True, as_attachment=False)

# ==================== 进度 API ====================
@app.route('/api/progress')
def get_progress():
    video_path = request.args.get('video', '')
    if not video_path:
        return jsonify({'position': 0, 'duration': 0})
    db = get_db()
    row = db.execute(
        "SELECT position, duration FROM progress WHERE device_id=? AND video_path=?",
        (g.device_id, video_path)
    ).fetchone()
    if row:
        return jsonify({'position': row['position'], 'duration': row['duration']})
    return jsonify({'position': 0, 'duration': 0})

@app.route('/api/progress/all')
def get_all_progress():
    db = get_db()
    rows = db.execute(
        "SELECT video_path, position, duration FROM progress WHERE device_id=?",
        (g.device_id,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/play', methods=['POST'])
def play_start():
    data = request.get_json(silent=True) or {}
    video_path = data.get('video', '')
    duration = float(data.get('duration', 0))
    if not video_path:
        return jsonify({'error': 'no video'}), 400

    now = datetime.now().isoformat()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO watch_sessions (device_id, video_path, started_at, ended_at, watched_sec, completed) VALUES (?,?,?,?,0,0)",
        (g.device_id, video_path, now, now)
    )
    session_id = cursor.lastrowid
    db.execute(
        "INSERT OR IGNORE INTO progress (device_id, video_path, position, duration, updated_at) VALUES (?,?,0,?,?)",
        (g.device_id, video_path, duration, now)
    )
    db.commit()
    return jsonify({'session_id': session_id})

@app.route('/api/progress', methods=['POST'])
def save_progress():
    data = request.get_json(silent=True) or {}
    video_path = data.get('video', '')
    position = float(data.get('position', 0))
    duration = float(data.get('duration', 0))
    session_id = data.get('session_id')

    if not video_path:
        return jsonify({'error': 'no video'}), 400

    now = datetime.now().isoformat()
    db = get_db()

    db.execute("""
        INSERT INTO progress (device_id, video_path, position, duration, updated_at)
        VALUES (?,?,?,?,?)
        ON CONFLICT(device_id, video_path) DO UPDATE SET position=?, duration=?, updated_at=?
    """, (g.device_id, video_path, position, duration, now, position, duration, now))

    if session_id:
        completed = 1 if (duration > 0 and position / duration >= 0.9) else 0
        db.execute("""
            UPDATE watch_sessions SET ended_at=?, watched_sec = watched_sec + 5, completed=?
            WHERE id=? AND device_id=?
        """, (now, completed, session_id, g.device_id))

    db.commit()
    return jsonify({'ok': True})

@app.route('/api/end', methods=['POST'])
def play_end():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id') or request.values.get('session_id')
    if session_id:
        now = datetime.now().isoformat()
        db = get_db()
        db.execute(
            "UPDATE watch_sessions SET ended_at=? WHERE id=? AND device_id=?",
            (now, session_id, g.device_id)
        )
        db.commit()
    return jsonify({'ok': True})

# ==================== 仪表盘 API ====================
@app.route('/api/stats')
def get_stats():
    db = get_db()
    total_devices = db.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    total_sessions = db.execute("SELECT COUNT(*) FROM watch_sessions").fetchone()[0]
    total_watch_sec = db.execute("SELECT COALESCE(SUM(watched_sec),0) FROM watch_sessions").fetchone()[0]
    total_completed = db.execute("SELECT COUNT(*) FROM watch_sessions WHERE completed=1").fetchone()[0]
    unique_videos = db.execute("SELECT COUNT(DISTINCT video_path) FROM watch_sessions").fetchone()[0]

    top_videos = db.execute("""
        SELECT video_path, COUNT(*) AS play_count, SUM(watched_sec) AS total_sec
        FROM watch_sessions GROUP BY video_path ORDER BY play_count DESC LIMIT 10
    """).fetchall()

    recent = db.execute("""
        SELECT ws.*, COALESCE(d.tag, '未知设备') AS device_tag
        FROM watch_sessions ws LEFT JOIN devices d ON ws.device_id = d.id
        ORDER BY ws.started_at DESC LIMIT 20
    """).fetchall()

    daily = db.execute("""
        SELECT DATE(started_at) AS day, COUNT(*) AS cnt, SUM(watched_sec) AS sec
        FROM watch_sessions WHERE started_at >= date('now','-14 days')
        GROUP BY day ORDER BY day
    """).fetchall()

    return jsonify({
        'total_devices': total_devices,
        'total_sessions': total_sessions,
        'total_watch_sec': total_watch_sec,
        'total_completed': total_completed,
        'unique_videos': unique_videos,
        'top_videos': [dict(r) for r in top_videos],
        'recent': [dict(r) for r in recent],
        'daily': [dict(r) for r in daily],
    })

@app.route('/api/devices')
def get_devices():
    db = get_db()
    rows = db.execute("""
        SELECT d.*,
            (SELECT COUNT(*) FROM watch_sessions WHERE device_id=d.id) AS play_count,
            (SELECT COALESCE(SUM(watched_sec),0) FROM watch_sessions WHERE device_id=d.id) AS total_sec,
            (SELECT MAX(started_at) FROM watch_sessions WHERE device_id=d.id) AS last_play
        FROM devices d ORDER BY d.last_seen DESC
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/devices/<device_id>/tag', methods=['POST'])
def update_device_tag(device_id):
    data = request.get_json(silent=True) or {}
    tag = (data.get('tag') or '').strip()
    db = get_db()
    db.execute("UPDATE devices SET tag=? WHERE id=?", (tag if tag else None, device_id))
    db.commit()
    return jsonify({'ok': True})

# ==================== 启动 ====================
if __name__ == '__main__':
    init_db()
    print("=" * 55)
    print("  回映 Rewind - 局域网视频流媒体服务器")
    print("=" * 55)
    print(f"  视频目录: {VIDEO_ROOT}")
    print(f"  数据库:   {DB_PATH}")
    print(f"  播放页:   http://localhost:5000")
    print(f"  仪表盘:   http://localhost:5000/admin")
    print(f"  手机访问: http://[电脑局域网IP]:5000")
    print("  按 Ctrl+C 停止服务器")
    print("=" * 55)
    print()
    if not os.path.isdir(VIDEO_ROOT):
        print(f"[警告] 视频目录不存在: {VIDEO_ROOT}")
        print(f"  可在程序同目录创建 video_dir.txt，写入视频文件夹路径。")
        print()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
