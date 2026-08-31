# SurfKompas

## Local setup

Create a project virtual environment and install dependencies:

```powershell
& "$env:USERPROFILE\.local\bin\uv.exe" sync
```

Run the new SurfKompas website locally:

```powershell
& "$env:USERPROFILE\.local\bin\uv.exe" run python web_app.py
```

Then open `http://127.0.0.1:8000`.

On Windows you can also double-click `start_surfkompas.bat` to start the local server and open the site without PyCharm.

The website is now split into a Cloudflare-ready static frontend plus an optional
local Python server for development:

- `site/index.html` is the app shell.
- `site/styles.css` contains the modern SurfKompas design.
- `site/forecast.js` fetches Open-Meteo directly in the browser.
- `site/app.js` handles spot selection, language, expert mode, days, and time windows.
- `web_app.py` is only used to preview the static site locally.

The forecast currently uses Open-Meteo public weather and marine model data.
Swell energy is shown as an estimated deep-water wave power value in kW/m.

## Cloudflare Pages deployment

The `site/` folder is Cloudflare-ready: it is now a static frontend that fetches
Open-Meteo directly in the browser, so it does not need the local Python server
when deployed.

Recommended Cloudflare Pages settings:

```text
Framework preset: None
Build command: leave empty
Build output directory: site
Root directory: /
Production branch: `codex/fix-windsock` for this pushed branch, or `main` after you merge it
```

If you connect Cloudflare Pages to GitHub, every push to the production branch
will trigger a new deployment automatically.

If Cloudflare is configured to run `npx wrangler deploy`, the repository also
includes `wrangler.jsonc`, which points Wrangler at the static `site/` folder.

## Mobile app

There is now a first Expo/React Native mobile version in `mobile/`.
It fetches the forecast directly from Open-Meteo, so it can run on a phone without the local Python server.

```powershell
cd mobile
npm install
npm start
```

Install Expo Go on your phone and scan the QR code to test it.

On Windows you can also double-click `start_surfkompas_mobile.bat`.
If your iPhone cannot connect to the QR-code server, double-click `start_surfkompas_mobile_tunnel.bat` instead.

## Desktop app

The older desktop prototype still runs with:

```powershell
& "$env:USERPROFILE\.local\bin\uv.exe" run python main.py
```

For PyCharm, point the interpreter at `.venv\Scripts\python.exe`.

The desktop app ships a small in-repo `customtkinter` compatibility shim, so the only
external dependency is Pillow.
