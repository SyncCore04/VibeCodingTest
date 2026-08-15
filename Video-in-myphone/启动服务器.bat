@echo off
chcp 65001 >nul
title 局域网视频流媒体服务器
cd /d "%~dp0"
echo ========================================
echo   局域网视频流媒体服务器 启动中...
echo ========================================
echo.
echo  视频目录: D:\电视剧
echo  访问地址: http://localhost:5000
echo.
echo  手机访问请用电脑的局域网IP替换 localhost
echo  按 Ctrl+C 可停止服务器
echo.
echo ========================================
echo.
python app.py
echo.
echo 服务器已停止，按任意键关闭窗口...
pause >nul
