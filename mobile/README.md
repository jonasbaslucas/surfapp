# SurfKompas Mobile

Native mobile version of SurfKompas built with Expo and React Native.

The app fetches Open-Meteo weather and marine data directly, so it does not need the local Python web server while running on a phone.

## Run locally

Install dependencies:

```powershell
cd mobile
npm install
```

Start Expo:

```powershell
npm start
```

Then install **Expo Go** on your phone and scan the QR code.

This project uses Expo SDK 54 so it works with the normal iPhone App Store version of Expo Go.

If your iPhone says it cannot connect to the server, use the tunnel starter from the repository root:

```powershell
..\start_surfkompas_mobile_tunnel.bat
```

Tunnel mode is slower, but it avoids many Wi-Fi and Windows firewall issues.

## Build app-store binaries

Install and log in to EAS:

```powershell
npm install -g eas-cli
eas login
eas init
```

Build Android and iOS:

```powershell
eas build --platform all --profile production
```

Submit when the store accounts are ready:

```powershell
eas submit --platform android
eas submit --platform ios
```

Before publishing, change `ios.bundleIdentifier` and `android.package` in `app.json` if you want a different permanent app id.
