@echo off
chcp 65001 >nul
title 回映 Rewind - 视频服务器
cd /d "%~dp0"

REM ========== Python 路径配置 ==========
set PYTHON=C:\Users\Apollo\AppData\Local\Python\pythoncore-3.14-64\python.exe

if not exist "%PYTHON%" (
    echo [错误] 找不到 Python: %PYTHON%
    echo 请编辑此 bat 文件，修改 PYTHON 变量为你的 python.exe 路径
    pause
    exit /b 1
)

echo ========================================
echo   回映 Rewind - 视频服务器启动中...
echo ========================================
echo.
echo   Python: %PYTHON%
echo   播放页: http://localhost:5000
echo   仪表盘: http://localhost:5000/admin
echo.
echo   手机访问请用电脑局域网IP替换 localhost
echo   按 Ctrl+C 可停止服务器
echo ========================================
echo.
"%PYTHON%" app.py
echo.
echo 服务器已停止，按任意键关闭窗口...
pause >nul
