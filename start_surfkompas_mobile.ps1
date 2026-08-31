$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$mobileRoot = Join-Path $projectRoot "mobile"
Set-Location $mobileRoot

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Host "SurfKompas Mobile needs Node.js and npm." -ForegroundColor Red
  Write-Host ""
  Write-Host "Install the current Node.js LTS from:"
  Write-Host "  https://nodejs.org/"
  Write-Host ""
  Read-Host "Press Enter to close"
  exit 1
}

try {
  Write-Host "Syncing mobile app dependencies for the iPhone Expo Go version..." -ForegroundColor Cyan
  $lockFile = Join-Path $mobileRoot "package-lock.json"
  $nodeModules = Join-Path $mobileRoot "node_modules"
  if ((Test-Path $lockFile) -and ((Get-Content -Raw $lockFile) -match "57\.0\.")) {
    Write-Host "Old Expo SDK 57 install detected. Cleaning mobile dependencies once..." -ForegroundColor Yellow
    if (Test-Path $nodeModules) {
      Remove-Item -LiteralPath $nodeModules -Recurse -Force
    }
    Remove-Item -LiteralPath $lockFile -Force
  }
  npm install --no-audit --fund=false

  if ($LASTEXITCODE -ne 0) {
    throw "npm install failed with exit code $LASTEXITCODE"
  }

  $hostIp = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {
      $_.IPAddress -notlike "127.*" -and
      $_.IPAddress -notlike "169.254.*" -and
      $_.IPAddress -notlike "172.17.*" -and
      $_.IPAddress -notlike "172.18.*" -and
      $_.IPAddress -notlike "172.19.*" -and
      $_.IPAddress -notlike "172.20.*"
    } |
    Sort-Object @{ Expression = { if ($_.InterfaceAlias -match "Wi-Fi|Wireless|Ethernet") { 0 } else { 1 } } }, InterfaceMetric |
    Select-Object -First 1 -ExpandProperty IPAddress

  if ($hostIp) {
    $env:REACT_NATIVE_PACKAGER_HOSTNAME = $hostIp
    Write-Host "Using laptop network address: $hostIp" -ForegroundColor Cyan
  } else {
    Write-Host "Could not auto-detect your laptop LAN IP. Expo will try LAN mode anyway." -ForegroundColor Yellow
  }

  Write-Host ""
  Write-Host "Starting SurfKompas Mobile." -ForegroundColor Green
  Write-Host "Install Expo Go on your iPhone, then scan the QR code from this terminal."
  Write-Host "Make sure your iPhone and laptop are on the same Wi-Fi."
  Write-Host ""
  npm run start

  if ($LASTEXITCODE -ne 0) {
    throw "npm start failed with exit code $LASTEXITCODE"
  }
} catch {
  Write-Host ""
  Write-Host "SurfKompas Mobile crashed:" -ForegroundColor Red
  Write-Host $_
} finally {
  Write-Host ""
  Read-Host "Press Enter to close"
}
