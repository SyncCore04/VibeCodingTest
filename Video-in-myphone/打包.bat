@echo off
chcp 65001 >nul
title 打包 - 回映 Rewind
cd /d "%~dp0"

REM ========== Python 路径配置 ==========
REM 如果你的 python 命令直接能用，把下面一行改成 set PYTHON=python
set PYTHON=C:\Users\Apollo\AppData\Local\Python\pythoncore-3.14-64\python.exe

echo ========================================
echo   回映 Rewind - 打包为单个 exe
echo ========================================
echo.
echo   Python: %PYTHON%
echo.

REM 检查 Python 是否存在
if not exist "%PYTHON%" (
    echo [错误] 找不到 Python: %PYTHON%
    echo 请编辑此 bat 文件，修改 PYTHON 变量为你的 python.exe 路径
    pause
    exit /b 1
)

REM 检查是否安装了 PyInstaller
"%PYTHON%" -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [信息] 未检测到 PyInstaller，正在安装...
    "%PYTHON%" -m pip install pyinstaller
    echo.
)

REM 执行打包
echo [信息] 正在打包，请稍候...
"%PYTHON%" -m PyInstaller --onefile ^
    --add-data "templates;templates" ^
    --name "VideoStreamServer" ^
    --clean ^
    --noconfirm ^
    app.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成！
echo   输出文件: dist\VideoStreamServer.exe
echo ========================================
echo.
echo 使用说明:
echo   1. 将 VideoStreamServer.exe 放到任意目录
echo   2. （可选）同目录创建 video_dir.txt，写入视频文件夹路径
echo      例如: D:\电视剧
echo      不创建则默认使用 D:\电视剧
echo   3. 双击 VideoStreamServer.exe 启动
echo   4. 播放页: http://localhost:5000
echo      仪表盘: http://localhost:5000/admin
echo.
pause
