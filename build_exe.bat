@echo off
echo Building AI Bartender Portable...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "BartenderAI_Portable" rmdir /s /q "BartenderAI_Portable"

REM Build with PyInstaller
python -m PyInstaller --onefile --clean --noconfirm --name=BartenderAI --console --add-data="voice;voice" --add-data=".env;." --hidden-import=edge_tts --hidden-import=edge_tts.communicate --hidden-import=edge_tts.tts --hidden-import=edge_tts.utils --hidden-import=edge_tts.exceptions --hidden-import=cv2 --hidden-import=openai --hidden-import=dotenv --hidden-import=flask --collect-all edge_tts --collect-all cv2 bartender_ai.py

if exist "dist\BartenderAI.exe" (
    echo.
    echo ✅ Build successful!
    echo 📁 Executable created: dist\BartenderAI.exe
    echo.
    
    REM Create portable folder
    if not exist "BartenderAI_Portable" mkdir "BartenderAI_Portable"
    copy "dist\BartenderAI.exe" "BartenderAI_Portable\"
    
    REM Copy data folders if they exist
    if exist "voice" xcopy "voice" "BartenderAI_Portable\voice\" /E /I /Y
    if exist ".env" copy ".env" "BartenderAI_Portable\"
    
    REM Create voice folder if it doesn't exist
    if not exist "BartenderAI_Portable\voice" mkdir "BartenderAI_Portable\voice"
    
    echo 📦 Portable package created: BartenderAI_Portable\
    echo.
    echo Ready to distribute!
    echo Just share the BartenderAI_Portable folder.
    echo.
    echo To run: Double-click BartenderAI.exe
    echo Server will start on http://localhost:5000
) else (
    echo ❌ Build failed!
)

echo.
pause
