from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen

from surf_logic import evaluate_conditions
from surf_spots import DEFAULT_SPOT, SURF_SPOTS


BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR / "site"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
MARINE_API = "https://marine-api.open-meteo.com/v1/marine"
DISPLAY_DAYS = 7
CACHE_TTL_SECONDS = 10 * 60

DIRECTIONS = [
    "N", "NNE", "NE", "ENE",
    "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW",
]

TIME_WINDOWS = [
    (6, "06:00"),
    (10, "10:00"),
    (14, "14:00"),
    (18, "18:00"),
]

LIVE_CACHE = {}


def clamp(value, low, high):
    return max(low, min(high, value))


def safe_float(value, default=0.0):
    try:
        return default if value is None else float(value)
    except (TypeError, ValueError):
        return default


def degrees_to_compass(degrees):
    return DIRECTIONS[int((degrees + 11.25) // 22.5) % 16]


def fetch_json(url):
    with urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def build_url(base_url, params):
    return f"{base_url}?{urlencode(params, doseq=True)}"


def parse_time(value):
    return value if isinstance(value, datetime) else datetime.fromisoformat(value)


def nearest_snapshot(series, target_time, target_date=None):
    times = series.get("time", [])
    if not times:
        return None, None

    parsed_times = [parse_time(item) for item in times]
    indices = range(len(parsed_times))
    if target_date is not None:
        indices = [index for index, item in enumerate(parsed_times) if item.date() == target_date]
        if not indices:
            return None, None

    best_index = min(indices, key=lambda index: abs((parsed_times[index] - target_time).total_seconds()))
    return {key: values[best_index] for key, values in series.items() if key != "time"}, parsed_times[best_index]


def day_label(sample_time, now):
    if sample_time.date() == now.date():
        return {"nl": "Vandaag", "en": "Today"}
    if sample_time.date() == (now + timedelta(days=1)).date():
        return {"nl": "Morgen", "en": "Tomorrow"}
    return {"nl": sample_time.strftime("%a"), "en": sample_time.strftime("%a")}


def vibe(score):
    if score >= 82:
        return {
            "key": "excellent",
            "nl": "Pak je board",
            "en": "Grab your board",
            "tone_nl": "Dit is zo'n raam waar je je dag omheen plant.",
            "tone_en": "This is the kind of window you plan around.",
        }
    if score >= 66:
        return {
            "key": "good",
            "nl": "Ziet er lekker uit",
            "en": "Looks tasty",
            "tone_nl": "Goede kans op een leuke sessie, met een paar details om te checken.",
            "tone_en": "A fun session is on the table, with a few details to check.",
        }
    if score >= 50:
        return {
            "key": "maybe",
            "nl": "Even goed timen",
            "en": "Time it well",
            "tone_nl": "Niet perfect, maar met het juiste moment kan het best leuk worden.",
            "tone_en": "Not perfect, but the right window could be fun.",
        }
    if score >= 35:
        return {
            "key": "messy",
            "nl": "Koffie en check later",
            "en": "Coffee, then recheck",
            "tone_nl": "Er zit misschien iets in, maar verwacht rommelige Noordzee.",
            "tone_en": "There may be something in it, but expect messy North Sea surf.",
        }
    return {
        "key": "quiet",
        "nl": "Meer strandwandeling",
        "en": "More beach walk",
        "tone_nl": "Vandaag voelt zachter; leuk voor sfeer, minder voor echte push.",
        "tone_en": "A softer beach day; nice atmosphere, less real push.",
    }


def wave_power_kwm(height_m, period_s):
    # Deep-water approximation: P ~= 0.49 * Hs^2 * Te. We use swell period as Te proxy.
    return max(0.0, 0.49 * height_m * height_m * period_s)


def energy_label(power):
    if power >= 12:
        return {"nl": "veel power", "en": "powerful"}
    if power >= 6:
        return {"nl": "goede push", "en": "good push"}
    if power >= 2:
        return {"nl": "kleine push", "en": "small push"}
    return {"nl": "weinig power", "en": "low power"}


def build_snapshot(spot, weather, marine, sample_time, now):
    wind_speed_kmh = safe_float(weather.get("wind_speed_10m"))
    wind_gust_kmh = safe_float(weather.get("wind_gusts_10m"))
    wind_direction = degrees_to_compass(safe_float(weather.get("wind_direction_10m")))
    swell_height_m = safe_float(marine.get("swell_wave_height"))
    swell_period_s = safe_float(marine.get("swell_wave_period"))
    swell_direction = degrees_to_compass(safe_float(marine.get("swell_wave_direction")))
    wave_height_m = safe_float(marine.get("wave_height"))
    wave_period_s = safe_float(marine.get("wave_period"))
    wave_direction = degrees_to_compass(safe_float(marine.get("wave_direction")))
    tide_m = safe_float(marine.get("sea_level_height_msl"))
    sea_temp_c = safe_float(marine.get("sea_surface_temperature"))
    air_temp_c = safe_float(weather.get("temperature_2m"))
    apparent_temp_c = safe_float(weather.get("apparent_temperature"))
    power = wave_power_kwm(swell_height_m, swell_period_s)
    summary = evaluate_conditions(spot, wind_direction, swell_direction, swell_height_m, swell_period_s)
    score = summary["total_score"]

    return {
        "time": sample_time.isoformat(timespec="minutes"),
        "hour": sample_time.strftime("%H:%M"),
        "date": sample_time.strftime("%Y-%m-%d"),
        "dayLabel": day_label(sample_time, now),
        "shortDate": sample_time.strftime("%d-%m"),
        "score": score,
        "vibe": vibe(score),
        "wind": {
            "speedKmh": round(wind_speed_kmh, 1),
            "speedKt": round(wind_speed_kmh * 0.539957, 1),
            "gustKmh": round(wind_gust_kmh, 1),
            "gustKt": round(wind_gust_kmh * 0.539957, 1),
            "direction": wind_direction,
        },
        "swell": {
            "heightM": round(swell_height_m, 2),
            "periodS": round(swell_period_s, 1),
            "direction": swell_direction,
            "energyKwm": round(power, 1),
            "energyLabel": energy_label(power),
        },
        "waves": {
            "heightM": round(wave_height_m, 2),
            "periodS": round(wave_period_s, 1),
            "direction": wave_direction,
        },
        "weather": {
            "airTempC": round(air_temp_c, 1),
            "feelsLikeC": round(apparent_temp_c, 1),
            "seaTempC": round(sea_temp_c, 1),
            "tideM": round(tide_m, 2),
        },
        "breakdown": summary,
    }


def make_fallback_bundle(spot_key, now):
    spot = SURF_SPOTS[spot_key]
    daily = []
    windows = {}
    seed = sum(ord(char) for char in spot["name"]) % 19
    for day_index in range(DISPLAY_DAYS):
        day = now + timedelta(days=day_index)
        day_windows = []
        for slot_index, (hour, label) in enumerate(TIME_WINDOWS):
            t = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            wind_kmh = clamp(15 + math.sin(day_index + slot_index * 0.7) * 8 + seed * 0.25, 4, 38)
            swell_m = clamp(0.45 + math.cos(day_index * 0.8 + seed) * 0.22 + seed * 0.025, 0.2, 1.8)
            period_s = clamp(6.4 + math.sin(day_index * 0.6 + slot_index) * 2.4, 4.5, 13)
            directions = ["NW", "WNW", "W", "NNW", "N", "SW"]
            wind_dirs = ["E", "ENE", "SE", "S", "SW", "W"]
            summary = evaluate_conditions(spot, wind_dirs[(day_index + slot_index + seed) % len(wind_dirs)], directions[(day_index + seed) % len(directions)], swell_m, period_s)
            score = summary["total_score"]
            power = wave_power_kwm(swell_m, period_s)
            item = {
                "time": t.isoformat(timespec="minutes"),
                "hour": label,
                "date": t.strftime("%Y-%m-%d"),
                "dayLabel": day_label(t, now),
                "shortDate": t.strftime("%d-%m"),
                "score": score,
                "vibe": vibe(score),
                "wind": {
                    "speedKmh": round(wind_kmh, 1),
                    "speedKt": round(wind_kmh * 0.539957, 1),
                    "gustKmh": round(wind_kmh * 1.35, 1),
                    "gustKt": round(wind_kmh * 0.539957 * 1.35, 1),
                    "direction": wind_dirs[(day_index + slot_index + seed) % len(wind_dirs)],
                },
                "swell": {
                    "heightM": round(swell_m, 2),
                    "periodS": round(period_s, 1),
                    "direction": directions[(day_index + seed) % len(directions)],
                    "energyKwm": round(power, 1),
                    "energyLabel": energy_label(power),
                },
                "waves": {
                    "heightM": round(swell_m * 1.15, 2),
                    "periodS": round(period_s - 0.5, 1),
                    "direction": directions[(day_index + seed) % len(directions)],
                },
                "weather": {
                    "airTempC": round(18 + math.sin(day_index * 0.4) * 2, 1),
                    "feelsLikeC": round(18 + math.sin(day_index * 0.4) * 2, 1),
                    "seaTempC": round(17 + math.sin(day_index * 0.2), 1),
                    "tideM": round(0.3 + math.sin(day_index + slot_index) * 0.45, 2),
                },
                "breakdown": summary,
            }
            day_windows.append(item)
        windows[str(day_index)] = day_windows
        daily.append(max(day_windows, key=lambda item: item["score"]))

    return {
        "status": "fallback",
        "generatedAt": now.isoformat(timespec="minutes"),
        "spot": public_spot(spot_key),
        "daily": daily,
        "windows": windows,
        "best": max(daily, key=lambda item: item["score"]),
        "sourceNote": {
            "nl": "Offline voorbeelddata. Verbind met internet voor live modeldata.",
            "en": "Offline sample data. Connect to the internet for live model data.",
        },
    }


def public_spot(key):
    spot = SURF_SPOTS[key]
    return {
        "id": key,
        "name": spot["name"],
        "region": spot.get("region", ""),
        "description": spot.get("description", ""),
        "latitude": spot["latitude"],
        "longitude": spot["longitude"],
    }


def fetch_forecast_bundle(spot_key):
    if spot_key not in SURF_SPOTS:
        spot_key = DEFAULT_SPOT

    cache_entry = LIVE_CACHE.get(spot_key)
    if cache_entry:
        cached_at, payload = cache_entry
        if (datetime.now() - cached_at).total_seconds() < CACHE_TTL_SECONDS:
            return payload

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    spot = SURF_SPOTS[spot_key]
    weather_url = build_url(
        FORECAST_API,
        {
            "latitude": spot["latitude"],
            "longitude": spot["longitude"],
            "timezone": "Europe/Amsterdam",
            "forecast_days": DISPLAY_DAYS,
            "hourly": ",".join([
                "temperature_2m",
                "apparent_temperature",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ]),
        },
    )
    marine_url = build_url(
        MARINE_API,
        {
            "latitude": spot["latitude"],
            "longitude": spot["longitude"],
            "timezone": "Europe/Amsterdam",
            "forecast_days": DISPLAY_DAYS,
            "cell_selection": "sea",
            "hourly": ",".join([
                "wave_height",
                "wave_period",
                "wave_direction",
                "swell_wave_height",
                "swell_wave_period",
                "swell_wave_direction",
                "sea_level_height_msl",
                "sea_surface_temperature",
            ]),
        },
    )

    try:
        weather = fetch_json(weather_url)["hourly"]
        marine = fetch_json(marine_url)["hourly"]
        daily = []
        windows = {}

        for day_index in range(DISPLAY_DAYS):
            date = (now + timedelta(days=day_index)).date()
            day_windows = []
            for _, label in TIME_WINDOWS:
                target = datetime.combine(date, datetime.min.time()).replace(hour=int(label[:2]))
                weather_sample, weather_time = nearest_snapshot(weather, target, date)
                marine_sample, marine_time = nearest_snapshot(marine, target, date)
                if not weather_sample or not marine_sample:
                    continue
                sample_time = weather_time or marine_time or target
                snapshot = build_snapshot(spot, weather_sample, marine_sample, sample_time, now)
                snapshot["hour"] = label
                day_windows.append(snapshot)

            if day_windows:
                windows[str(day_index)] = day_windows
                daily.append(max(day_windows, key=lambda item: item["score"]))

        if not daily:
            raise ValueError("No forecast windows returned")

        payload = {
            "status": "live",
            "generatedAt": now.isoformat(timespec="minutes"),
            "spot": public_spot(spot_key),
            "daily": daily,
            "windows": windows,
            "best": max(daily, key=lambda item: item["score"]),
            "sourceNote": {
                "nl": "Live Open-Meteo modeldata. Nabije stranden kunnen dezelfde golf-gridcel delen.",
                "en": "Live Open-Meteo model data. Nearby beaches can share the same wave-grid cell.",
            },
        }
    except (HTTPError, URLError, KeyError, TypeError, ValueError):
        payload = make_fallback_bundle(spot_key, now)

    LIVE_CACHE[spot_key] = (datetime.now(), payload)
    return payload


def json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def static_response(handler, path):
    if path == "/":
        path = "/index.html"
    target = (SITE_DIR / path.lstrip("/")).resolve()
    if not str(target).startswith(str(SITE_DIR.resolve())) or not target.exists() or target.is_dir():
        handler.send_error(404)
        return

    content_types = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }
    body = target.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", content_types.get(target.suffix.lower(), "application/octet-stream"))
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store" if target.suffix in {".html", ".js", ".css"} else "public, max-age=86400")
    handler.end_headers()
    handler.wfile.write(body)


class SurfRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/spots":
            json_response(self, {"defaultSpot": DEFAULT_SPOT, "spots": [public_spot(key) for key in SURF_SPOTS]})
            return

        if parsed.path == "/api/forecast":
            spot_key = params.get("spot", [DEFAULT_SPOT])[0]
            json_response(self, fetch_forecast_bundle(spot_key))
            return

        static_response(self, parsed.path)

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), SurfRequestHandler)
    print("SurfKompas running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
