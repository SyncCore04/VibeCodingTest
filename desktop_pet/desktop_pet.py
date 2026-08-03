#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
桌面宠物程序 - Windows Desktop Pet
透明窗口、无边框、始终置顶，支持拖动、点击互动、对话气泡、右键菜单、滚轮缩放
"""

import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QMenu, QAction
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QPoint, QRect, QEasingCurve
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPainterPath, QPen
)


def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容 PyInstaller 打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


# 随机对话列表
DIALOGUES = [
    "你好呀~",
    "今天也要开心哦！",
    "抱抱~",
    "嘿嘿，想我了吗？",
    "我会一直陪着你的！",
    "别太累了，休息一下吧~",
    "你是最棒的！",
    "嘿嘿嘿~",
    "今天天气真好呀！",
    "给你比个心~",
    "我在这里哦！",
    "一起来玩吧！",
    "哼，不理你了！",
    "想吃好吃的...",
    "困了，想睡觉觉~",
    "你在干嘛呀？",
    "今天的你也很可爱呢！",
    "加油加油！",
    "偷偷看着你~",
    "最喜欢你了！",
    "哇！被发现了~",
    "嘿嘿，戳我干嘛~",
    "陪你一起努力！",
    "心情好棒呀！",
]


class SpeechBubble(QWidget):
    """对话气泡窗口 - 独立透明窗口，显示在宠物上方"""

    def __init__(self, text, pet_pos, pet_width):
        super().__init__()

        self.text = text
        self.pet_pos = pet_pos
        self.pet_width = pet_width
        self._closing = False

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 字体与文字尺寸计算
        self.font = QFont("Microsoft YaHei", 11, QFont.Bold)
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()

        # 气泡尺寸
        self.bubble_w = text_width + 36
        self.bubble_h = text_height + 22
        self.tail_h = 12

        total_w = int(self.bubble_w)
        total_h = int(self.bubble_h + self.tail_h)
        self.setFixedSize(total_w, total_h)

        # 定位在宠物正上方
        pet_cx = pet_pos.x() + pet_width // 2
        bx = pet_cx - total_w // 2
        by = pet_pos.y() - total_h - 5

        # 边界保护：上方不够则放下方
        self.below = False
        screen = QApplication.desktop().availableGeometry()
        if by < screen.top() + 5:
            by = pet_pos.y() + pet_width + 5
            self.below = True

        if bx < screen.left() + 5:
            bx = screen.left() + 5
        if bx + total_w > screen.right() - 5:
            bx = screen.right() - total_w - 5

        self.move(bx, by)

        # 淡入
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(250)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()

        # 定时自动关闭（先淡出再关闭）
        self.lifetime = QTimer(self)
        self.lifetime.setSingleShot(True)
        self.lifetime.timeout.connect(self._fade_out)
        self.lifetime.start(2500)

    def _fade_out(self):
        if self._closing:
            return
        self._closing = True
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.close)
        self.fade_out.start()

    def force_close(self):
        self._closing = True
        self.lifetime.stop()
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bw = int(self.bubble_w)
        bh = int(self.bubble_h)
        br = QRect(0, 0, bw, bh)

        # 外阴影描边（淡灰色）
        painter.setPen(QPen(QColor(180, 180, 180, 80), 1))
        painter.setBrush(QColor(255, 255, 255, 255))
        painter.drawRoundedRect(br, 14, 14)

        # 尾巴三角形
        tail = QPainterPath()
        cx = bw / 2
        if self.below:
            # 尾巴在上方，指向上方（宠物在下方）
            tail.moveTo(cx - 9, 1)
            tail.lineTo(cx + 9, 1)
            tail.lineTo(cx, 1 - self.tail_h + 1)
        else:
            # 尾巴在下方，指向下方（宠物在下方）
            tail.moveTo(cx - 9, bh - 1)
            tail.lineTo(cx + 9, bh - 1)
            tail.lineTo(cx, bh + self.tail_h - 1)
        tail.closeSubpath()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 255))
        painter.drawPath(tail)

        # 文字
        painter.setPen(QColor(70, 70, 70))
        painter.setFont(self.font)
        painter.drawText(br, Qt.AlignCenter, self.text)


class DesktopPet(QWidget):
    """桌面宠物主窗口"""

    def __init__(self):
        super().__init__()

        # ---- 状态 ----
        self.current_size = 150
        self.min_size = 60
        self.max_size = 400
        self.is_dragging = False
        self.drag_start = QPoint()
        self.win_start = QPoint()
        self.animation = None
        self.bubble = None
        self.always_on_top = True
        self.interaction_idx = 0

        # ---- UI 初始化 ----
        self._init_window()
        self._load_image()
        self._init_menu()

        self.show()

    # ==================== 初始化 ====================

    def _init_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)

        # 默认放在屏幕右下角
        screen = QApplication.desktop().availableGeometry()
        self.move(
            screen.right() - self.current_size - 50,
            screen.bottom() - self.current_size - 50
        )

    def _load_image(self):
        path = resource_path("pet.png")
        self.original_pixmap = QPixmap(path)
        if self.original_pixmap.isNull():
            # 占位
            self.original_pixmap = QPixmap(200, 200)
            self.original_pixmap.fill(QColor(255, 120, 120, 200))
        self._apply_size()

    def _apply_size(self):
        """按 current_size 缩放图片并调整窗口"""
        scaled = self.original_pixmap.scaled(
            self.current_size, self.current_size,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        w, h = scaled.width(), scaled.height()
        self.image_label.setGeometry(0, 0, w, h)
        self.resize(w, h)

    def _init_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

    # ==================== 右键菜单 ====================

    def _show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 6px;
                font-family: "Microsoft YaHei";
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 40px 6px 24px;
                border-radius: 5px;
                color: #333333;
            }
            QMenu::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QMenu::separator {
                height: 1px;
                background: #e8e8e8;
                margin: 5px 12px;
            }
            QMenu::menu-indicator {
                image: none;
            }
        """)

        # --- 调整大小子菜单 ---
        size_menu = menu.addMenu("  📐  调整大小")

        for label, size in [("  小", 80), ("  中", 150),
                             ("  大", 250), ("  超大", 400)]:
            act = QAction(label + f" ({size}px)", self)
            act.triggered.connect(lambda checked, s=size: self._set_size(s))
            size_menu.addAction(act)

        menu.addSeparator()

        # --- 置顶开关 ---
        top_act = QAction("  📌  取消置顶" if self.always_on_top
                          else "  📌  窗口置顶", self)
        top_act.triggered.connect(self._toggle_top)
        menu.addAction(top_act)

        menu.addSeparator()

        # --- 退出 ---
        quit_act = QAction("  ❌  退出程序", self)
        quit_act.triggered.connect(self._quit)
        menu.addAction(quit_act)

        menu.exec_(self.mapToGlobal(pos))

    def _set_size(self, size):
        self.current_size = max(self.min_size, min(self.max_size, size))
        self._apply_size()

    def _toggle_top(self):
        self.always_on_top = not self.always_on_top
        if self.always_on_top:
            self.setWindowFlags(
                self.windowFlags() | Qt.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowStaysOnTopHint
            )
        self.show()

    def _quit(self):
        if self.bubble:
            self.bubble.force_close()
        QApplication.quit()

    # ==================== 鼠标事件 ====================

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_start = event.globalPos()
            self.win_start = self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            offset = event.globalPos() - self.drag_start
            if offset.manhattanLength() > 5:
                self.is_dragging = True
                self.move(self.win_start + offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.is_dragging:
                self._interact()
            self.is_dragging = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = 10 if delta > 0 else -10
        new_size = self.current_size + step
        self.current_size = max(self.min_size, min(self.max_size, new_size))
        self._apply_size()

    def resizeEvent(self, event):
        """窗口大小变化时同步图片标签"""
        self.image_label.setGeometry(0, 0, self.width(), self.height())

    # ==================== 互动动画 ====================

    def _interact(self):
        """点击触发互动：轮流播放动画 + 随机气泡"""
        if self.animation and self.animation.state() == QPropertyAnimation.Running:
            return

        anims = [self._anim_jump, self._anim_squash, self._anim_shake]
        anims[self.interaction_idx % len(anims)]()
        self.interaction_idx += 1

        self._show_bubble()

    def _anim_jump(self):
        """跳跃 - 抛物线"""
        g = self.geometry()
        h = 80
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(700)
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            y_off = -h * 4 * t * (1 - t)
            anim.setKeyValueAt(t, QRect(g.x(), g.y() + int(y_off),
                                        g.width(), g.height()))
        anim.start()
        self.animation = anim

    def _anim_squash(self):
        """压扁回弹"""
        g = self.geometry()
        bottom = g.y() + g.height()
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(650)

        h_comp = int(g.height() * 0.55)
        h_stretch = int(g.height() * 1.12)

        anim.setKeyValueAt(0.0, g)
        anim.setKeyValueAt(0.25, QRect(g.x(), bottom - h_comp,
                                       g.width(), h_comp))
        anim.setKeyValueAt(0.55, QRect(g.x(), bottom - h_stretch,
                                       g.width(), h_stretch))
        anim.setKeyValueAt(0.8, QRect(g.x(), bottom - int(g.height() * 0.95),
                                      g.width(), int(g.height() * 0.95)))
        anim.setKeyValueAt(1.0, g)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        anim.start()
        self.animation = anim

    def _anim_shake(self):
        """左右抖动"""
        g = self.geometry()
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(500)

        def r(dx):
            return QRect(g.x() + dx, g.y(), g.width(), g.height())

        anim.setKeyValueAt(0.0, r(0))
        anim.setKeyValueAt(0.12, r(-15))
        anim.setKeyValueAt(0.25, r(15))
        anim.setKeyValueAt(0.38, r(-12))
        anim.setKeyValueAt(0.5, r(12))
        anim.setKeyValueAt(0.62, r(-8))
        anim.setKeyValueAt(0.75, r(8))
        anim.setKeyValueAt(0.88, r(-4))
        anim.setKeyValueAt(1.0, r(0))
        anim.start()
        self.animation = anim

    def _show_bubble(self):
        if self.bubble:
            self.bubble.force_close()

        text = random.choice(DIALOGUES)
        self.bubble = SpeechBubble(text, self.pos(), self.width())
        self.bubble.show()

    # ==================== 关闭 ====================

    def closeEvent(self, event):
        if self.bubble:
            self.bubble.force_close()
        event.accept()


def main():
    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    pet = DesktopPet()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
