@echo off
echo ========================================
echo   DesktopPet - Build Script
echo ========================================
echo.

echo [1/3] Checking dependencies...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo   Installing PyQt5...
    pip install PyQt5
)
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo   Installing PyInstaller...
    pip install pyinstaller
)
echo   Dependencies OK.
echo.

echo [2/3] Cleaning old build...
if exist "dist\DesktopPet.exe" del /q "dist\DesktopPet.exe"
if exist "build" rmdir /s /q "build"
if exist "DesktopPet.spec" del /q "DesktopPet.spec"

echo [3/3] Building EXE...
python -m PyInstaller --noconsole --onefile --add-data "pet.png;." --name "DesktopPet" desktop_pet.py

if exist "dist\DesktopPet.exe" (
    echo.
    echo ========================================
    echo   Build successful!
    echo   EXE: dist\DesktopPet.exe
    echo   Double-click it to run.
    echo ========================================
) else (
    echo.
    echo [ERROR] Build failed, check messages above.
)

echo.
pause
