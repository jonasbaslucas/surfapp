@echo off
setlocal

cd /d "%~dp0mobile"

where npm >nul 2>nul
if errorlevel 1 (
  echo SurfKompas Mobile needs Node.js and npm.
  echo.
  echo Install the current Node.js LTS from:
  echo   https://nodejs.org/
  echo.
  echo Then double-click this file again.
  pause
  exit /b 1
)

echo Syncing mobile app dependencies for the iPhone Expo Go version...
if exist "package-lock.json" (
  findstr /C:"57.0." "package-lock.json" >nul
  if not errorlevel 1 (
    echo Old Expo SDK 57 install detected. Cleaning mobile dependencies once...
    if exist "node_modules" rmdir /s /q "node_modules"
    if exist "package-lock.json" del /q "package-lock.json"
  )
)
call npm install --no-audit --fund=false
if errorlevel 1 (
  echo.
  echo npm install failed. Check the error above.
  pause
  exit /b 1
)

for /f "usebackq delims=" %%I in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -notlike '172.17.*' -and $_.IPAddress -notlike '172.18.*' -and $_.IPAddress -notlike '172.19.*' -and $_.IPAddress -notlike '172.20.*' }; $preferred = $ips | Where-Object { $_.InterfaceAlias -match 'Wi-Fi|Wireless|Ethernet' } | Sort-Object InterfaceMetric | Select-Object -First 1; if (-not $preferred) { $preferred = $ips | Sort-Object InterfaceMetric | Select-Object -First 1 }; if ($preferred) { $preferred.IPAddress }"`) do set "SURFKOMPAS_HOST=%%I"

if defined SURFKOMPAS_HOST (
  set "REACT_NATIVE_PACKAGER_HOSTNAME=%SURFKOMPAS_HOST%"
  echo Using laptop network address: %SURFKOMPAS_HOST%
) else (
  echo Could not auto-detect your laptop LAN IP. Expo will try LAN mode anyway.
)

echo.
echo Starting SurfKompas Mobile.
echo Install Expo Go on your iPhone, then scan the QR code from this terminal.
echo Make sure your iPhone and laptop are on the same Wi-Fi.
echo.
call npm run start

echo.
echo SurfKompas Mobile stopped. If this was unexpected, copy the error above and send it to Codex.
pause

endlocal
