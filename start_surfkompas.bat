@echo off
setlocal

cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
  set "SURFKOMPAS_UV=%USERPROFILE%\.local\bin\uv.exe"
) else (
  set "SURFKOMPAS_UV=uv"
)

if not exist "%SURFKOMPAS_UV%" if not "%SURFKOMPAS_UV%"=="uv" (
  echo SurfKompas could not find uv.
  echo Install uv or run this once in PowerShell:
  echo   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  pause
  exit /b 1
)

start "SurfKompas server" powershell -NoExit -ExecutionPolicy Bypass -Command "& '%SURFKOMPAS_UV%' run python web_app.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"

endlocal
