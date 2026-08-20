"""
一次性清理脚本：合并重复设备（同 IP + 同 User-Agent）
保留最近活跃的设备，将进度和观看记录迁移过去，删除重复项。
使用方法：python cleanup_duplicates.py
"""
import sqlite3
import os
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rewind.db")

if not os.path.isfile(DB_PATH):
    print("数据库不存在，无需清理。")
    exit(0)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. 按 (ip, user_agent) 分组，找出所有重复设备
groups = defaultdict(list)
for row in cur.execute("SELECT id, ip, user_agent, last_seen, tag FROM devices"):
    key = (row['ip'], row['user_agent'])
    groups[key].append(dict(row))

duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}

if not duplicate_groups:
    print("没有发现重复设备，无需清理。")
    conn.close()
    exit(0)

print(f"发现 {len(duplicate_groups)} 组重复设备：")
total_dup = 0
for (ip, ua), devs in duplicate_groups.items():
    print(f"  IP={ip}, 设备数={len(devs)}")
    total_dup += len(devs) - 1

print(f"\n将删除 {total_dup} 个重复设备，保留每组中最近活跃的一个。")

# 2. 对每组，保留 last_seen 最新的设备
merge_map = {}  # old_id -> keep_id
for (ip, ua), devs in duplicate_groups.items():
    # 按 last_seen 降序，第一个保留
    devs.sort(key=lambda x: x['last_seen'], reverse=True)
    keep_id = devs[0]['id']
    for dev in devs[1:]:
        merge_map[dev['id']] = keep_id

print(f"\n合并映射：{len(merge_map)} 个设备将被合并")

# 3. 迁移进度数据（Python 层面合并，避免 SQLite 不支持 UPDATE 表别名的问题）
for old_id, keep_id in merge_map.items():
    # 取出旧设备的所有进度
    old_progress = cur.execute(
        "SELECT video_path, position, duration, updated_at FROM progress WHERE device_id = ?",
        (old_id,)
    ).fetchall()

    for row in old_progress:
        video_path = row['video_path']
        # 检查保留设备是否已有该视频的进度
        existing = cur.execute(
            "SELECT position, duration, updated_at FROM progress WHERE device_id = ? AND video_path = ?",
            (keep_id, video_path)
        ).fetchone()

        if existing is None:
            # 没有冲突，直接迁移
            cur.execute(
                "INSERT INTO progress (device_id, video_path, position, duration, updated_at) VALUES (?,?,?,?,?)",
                (keep_id, video_path, row['position'], row['duration'], row['updated_at'])
            )
        else:
            # 有冲突，保留位置更大（看得更多）的那个
            if row['position'] > existing['position']:
                cur.execute(
                    "UPDATE progress SET position = ?, duration = ?, updated_at = ? WHERE device_id = ? AND video_path = ?",
                    (row['position'], row['duration'], row['updated_at'], keep_id, video_path)
                )

    # 删除旧设备的进度记录
    cur.execute("DELETE FROM progress WHERE device_id = ?", (old_id,))

# 4. 迁移观看记录
for old_id, keep_id in merge_map.items():
    cur.execute("UPDATE watch_sessions SET device_id = ? WHERE device_id = ?", (keep_id, old_id))

# 5. 删除重复设备
for old_id in merge_map:
    cur.execute("DELETE FROM devices WHERE id = ?", (old_id,))

conn.commit()

# 6. 验证
remaining = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
print(f"\n清理完成！当前设备数：{remaining}")
print("删除的重复设备 ID：")
for old_id in merge_map:
    print(f"  {old_id}")

conn.close()
