@echo off
REM Start a new cmd window that serves the templates folder, then open browser to user index
start "Static Server" cmd /k "cd /d "%~dp0templates" && python -m http.server 5501"
timeout /t 1 >nul
start "" "http://127.0.0.1:5501/user/index.html"
