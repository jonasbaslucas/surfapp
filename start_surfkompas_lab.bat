@echo off
setlocal

cd /d "%~dp0site"
echo Starting the SurfKompas lab preview on http://127.0.0.1:8788
start "SurfKompas lab server" powershell -NoExit -ExecutionPolicy Bypass -Command "python -m http.server 8788"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8788"

endlocal
