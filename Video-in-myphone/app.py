import os
from flask import Flask, render_template, send_file, abort, request
from urllib.parse import quote

app = Flask(__name__)

# 视频根目录
VIDEO_ROOT = r"D:\电视剧"

# 支持的视频格式
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi'}

# MIME 类型映射
MIME_TYPES = {
    '.mp4': 'video/mp4',
    '.mkv': 'video/x-matroska',
    '.avi': 'video/x-msvideo',
}


def scan_videos(root_dir):
    """递归扫描根目录下所有视频文件，返回相对路径列表"""
    videos = []
    if not os.path.isdir(root_dir):
        return videos
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)
                # 统一使用正斜杠，便于 URL 处理
                rel_path = rel_path.replace('\\', '/')
                videos.append(rel_path)
    videos.sort(key=lambda x: x.lower())
    return videos


def safe_resolve(rel_path):
    """
    将相对路径安全解析为绝对路径，防止目录遍历攻击。
    解析后的路径必须位于 VIDEO_ROOT 之内，否则返回 None。
    """
    if not rel_path:
        return None
    # 规范化路径，消除 .. 等
    normalized = os.path.normpath(rel_path)
    # 拒绝以分隔符开头或包含盘符的路径
    if normalized.startswith('..') or os.path.isabs(normalized):
        return None
    full_path = os.path.join(VIDEO_ROOT, normalized)
    full_path = os.path.abspath(full_path)
    # 确保解析后仍在根目录内
    root_abs = os.path.abspath(VIDEO_ROOT)
    if not full_path.startswith(root_abs + os.sep) and full_path != root_abs:
        return None
    return full_path


@app.route('/')
def index():
    videos = scan_videos(VIDEO_ROOT)
    return render_template('index.html', videos=videos)


@app.route('/video/<path:filename>')
def video(filename):
    full_path = safe_resolve(filename)
    if full_path is None or not os.path.isfile(full_path):
        abort(404)

    ext = os.path.splitext(full_path)[1].lower()
    mimetype = MIME_TYPES.get(ext, 'application/octet-stream')

    # conditional=True 启用 HTTP Range 请求支持，实现拖动进度条/快进
    return send_file(
        full_path,
        mimetype=mimetype,
        conditional=True,
        as_attachment=False
    )


if __name__ == '__main__':
    if not os.path.isdir(VIDEO_ROOT):
        print(f"[警告] 视频目录不存在: {VIDEO_ROOT}")
        print("请修改 app.py 中的 VIDEO_ROOT 为实际视频文件夹路径。")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
