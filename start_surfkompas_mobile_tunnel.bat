@echo off
setlocal

cd /d "%~dp0mobile"

where npm >nul 2>nul
if errorlevel 1 (
  echo SurfKompas Mobile needs Node.js and npm.
  echo Install the current Node.js LTS from https://nodejs.org/
  pause
  exit /b 1
)

echo Syncing mobile app dependencies...
call npm install --no-audit --fund=false
if errorlevel 1 (
  echo.
  echo npm install failed. Check the error above.
  pause
  exit /b 1
)

echo.
echo Starting SurfKompas Mobile in tunnel mode.
echo Use this if the normal QR code cannot connect over Wi-Fi.
echo Tunnel mode can be slower, but it avoids many router/firewall problems.
echo.
call npm run start:tunnel

echo.
echo SurfKompas Mobile tunnel stopped. If this was unexpected, copy the error above and send it to Codex.
pause

endlocal
