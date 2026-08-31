const forecastApi = "https://api.open-meteo.com/v1/forecast";
const marineApi = "https://marine-api.open-meteo.com/v1/marine";
const displayDays = 7;
const directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
const timeWindows = ["06:00", "10:00", "14:00", "18:00"];

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function number(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function degreesToCompass(degrees) {
  return directions[Math.floor((number(degrees) + 11.25) / 22.5) % 16];
}

function buildUrl(baseUrl, params) {
  const query = new URLSearchParams(params);
  return `${baseUrl}?${query.toString()}`;
}

function parseLocalTime(value) {
  return new Date(value);
}

function sameDate(left, right) {
  return left.getFullYear() === right.getFullYear() && left.getMonth() === right.getMonth() && left.getDate() === right.getDate();
}

function nearestSnapshot(series, targetTime, targetDate) {
  const times = series.time || [];
  let bestIndex = -1;
  let bestDistance = Number.POSITIVE_INFINITY;
  times.forEach((value, index) => {
    const sampleTime = parseLocalTime(value);
    if (!sameDate(sampleTime, targetDate)) return;
    const distance = Math.abs(sampleTime.getTime() - targetTime.getTime());
    if (distance < bestDistance) {
      bestDistance = distance;
      bestIndex = index;
    }
  });
  if (bestIndex < 0) return [null, null];
  const sample = {};
  Object.entries(series).forEach(([key, values]) => {
    if (key !== "time") sample[key] = values[bestIndex];
  });
  return [sample, parseLocalTime(times[bestIndex])];
}

function formatDate(date) {
  return `${String(date.getDate()).padStart(2, "0")}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function dayLabel(sampleTime, now) {
  const tomorrow = new Date(now);
  tomorrow.setDate(now.getDate() + 1);
  if (sameDate(sampleTime, now)) return { nl: "Vandaag", en: "Today" };
  if (sameDate(sampleTime, tomorrow)) return { nl: "Morgen", en: "Tomorrow" };
  return {
    nl: sampleTime.toLocaleDateString("nl-NL", { weekday: "short" }),
    en: sampleTime.toLocaleDateString("en-US", { weekday: "short" }),
  };
}

function scoreWind(spot, wind) {
  if (spot.excellent_wind.includes(wind)) return [30, "Excellent"];
  if (spot.good_wind.includes(wind)) return [24, "Good"];
  if (spot.okay_wind.includes(wind)) return [15, "Okay"];
  if (spot.bad_wind.includes(wind)) return [5, "Poor"];
  return [0, "Unknown"];
}

function scoreSwellDirection(spot, direction) {
  if (spot.excellent_swell.includes(direction)) return [20, "Excellent"];
  if (spot.good_swell.includes(direction)) return [14, "Good"];
  if (spot.bad_swell.includes(direction)) return [4, "Poor"];
  return [0, "Unknown"];
}

function scoreSwellHeight(spot, height) {
  if (height < spot.minimum_swell_height) return [0, "Too small"];
  if (height < spot.good_swell_height) return [10, "Small"];
  if (height < spot.excellent_swell_height) return [20, "Good"];
  return [25, "Excellent"];
}

function scorePeriod(spot, period) {
  if (period < spot.minimum_period) return [0, "Too short"];
  if (period < spot.good_period) return [10, "Short"];
  if (period < spot.excellent_period) return [20, "Good"];
  return [25, "Excellent"];
}

function evaluateConditions(spot, wind, swellDirection, swellHeight, period) {
  const [windScore, windQuality] = scoreWind(spot, wind);
  const [swellDirectionScore, swellDirectionQuality] = scoreSwellDirection(spot, swellDirection);
  const [swellHeightScore, swellHeightQuality] = scoreSwellHeight(spot, swellHeight);
  const [periodScore, periodQuality] = scorePeriod(spot, period);
  return {
    total_score: windScore + swellDirectionScore + swellHeightScore + periodScore,
    wind_score: windScore,
    wind_quality: windQuality,
    swell_direction_score: swellDirectionScore,
    swell_direction_quality: swellDirectionQuality,
    swell_height_score: swellHeightScore,
    swell_height_quality: swellHeightQuality,
    period_score: periodScore,
    period_quality: periodQuality,
  };
}

function vibe(score) {
  if (score >= 82) return { key: "excellent", nl: "Pak je board", en: "Grab your board", tone_nl: "Dit is zo'n raam waar je je dag omheen plant.", tone_en: "This is the kind of window you plan around." };
  if (score >= 66) return { key: "good", nl: "Ziet er lekker uit", en: "Looks tasty", tone_nl: "Goede kans op een leuke sessie, met een paar details om te checken.", tone_en: "A fun session is on the table, with a few details to check." };
  if (score >= 50) return { key: "maybe", nl: "Even goed timen", en: "Time it well", tone_nl: "Niet perfect, maar met het juiste moment kan het best leuk worden.", tone_en: "Not perfect, but the right window could be fun." };
  if (score >= 35) return { key: "messy", nl: "Koffie en check later", en: "Coffee, then recheck", tone_nl: "Er zit misschien iets in, maar verwacht rommelige Noordzee.", tone_en: "There may be something in it, but expect messy North Sea surf." };
  return { key: "quiet", nl: "Meer strandwandeling", en: "More beach walk", tone_nl: "Vandaag voelt zachter; leuk voor sfeer, minder voor echte push.", tone_en: "A softer beach day; nice atmosphere, less real push." };
}

function wavePowerKwm(heightM, periodS) {
  return Math.max(0, 0.49 * heightM * heightM * periodS);
}

function energyLabel(power) {
  if (power >= 12) return { nl: "veel power", en: "powerful" };
  if (power >= 6) return { nl: "goede push", en: "good push" };
  if (power >= 2) return { nl: "kleine push", en: "small push" };
  return { nl: "weinig power", en: "low power" };
}

function buildSnapshot(spot, weather, marine, sampleTime, now, label) {
  const windSpeedKmh = number(weather.wind_speed_10m);
  const windGustKmh = number(weather.wind_gusts_10m);
  const windDirection = degreesToCompass(weather.wind_direction_10m);
  const swellHeightM = number(marine.swell_wave_height);
  const swellPeriodS = number(marine.swell_wave_period);
  const swellDirection = degreesToCompass(marine.swell_wave_direction);
  const waveHeightM = number(marine.wave_height);
  const wavePeriodS = number(marine.wave_period);
  const waveDirection = degreesToCompass(marine.wave_direction);
  const power = wavePowerKwm(swellHeightM, swellPeriodS);
  const breakdown = evaluateConditions(spot, windDirection, swellDirection, swellHeightM, swellPeriodS);
  const score = breakdown.total_score;

  return {
    time: sampleTime.toISOString(),
    hour: label,
    date: sampleTime.toISOString().slice(0, 10),
    dayLabel: dayLabel(sampleTime, now),
    shortDate: formatDate(sampleTime),
    score,
    vibe: vibe(score),
    wind: {
      speedKmh: Number(windSpeedKmh.toFixed(1)),
      speedKt: Number((windSpeedKmh * 0.539957).toFixed(1)),
      gustKmh: Number(windGustKmh.toFixed(1)),
      gustKt: Number((windGustKmh * 0.539957).toFixed(1)),
      direction: windDirection,
    },
    swell: {
      heightM: Number(swellHeightM.toFixed(2)),
      periodS: Number(swellPeriodS.toFixed(1)),
      direction: swellDirection,
      energyKwm: Number(power.toFixed(1)),
      energyLabel: energyLabel(power),
    },
    waves: {
      heightM: Number(waveHeightM.toFixed(2)),
      periodS: Number(wavePeriodS.toFixed(1)),
      direction: waveDirection,
    },
    weather: {
      airTempC: Number(number(weather.temperature_2m).toFixed(1)),
      feelsLikeC: Number(number(weather.apparent_temperature).toFixed(1)),
      seaTempC: Number(number(marine.sea_surface_temperature).toFixed(1)),
      tideM: Number(number(marine.sea_level_height_msl).toFixed(2)),
    },
    breakdown,
  };
}

function fallbackBundle(spot) {
  const now = new Date();
  const seed = spot.name.split("").reduce((sum, char) => sum + char.charCodeAt(0), 0) % 19;
  const daily = [];
  const windows = {};
  for (let dayIndex = 0; dayIndex < displayDays; dayIndex += 1) {
    const dayWindows = [];
    for (let slotIndex = 0; slotIndex < timeWindows.length; slotIndex += 1) {
      const sampleTime = new Date(now);
      sampleTime.setDate(now.getDate() + dayIndex);
      sampleTime.setHours(Number(timeWindows[slotIndex].slice(0, 2)), 0, 0, 0);
      const windKmh = clamp(15 + Math.sin(dayIndex + slotIndex * 0.7) * 8 + seed * 0.25, 4, 38);
      const swellM = clamp(0.45 + Math.cos(dayIndex * 0.8 + seed) * 0.22 + seed * 0.025, 0.2, 1.8);
      const periodS = clamp(6.4 + Math.sin(dayIndex * 0.6 + slotIndex) * 2.4, 4.5, 13);
      const directionsFallback = ["NW", "WNW", "W", "NNW", "N", "SW"];
      const windDirections = ["E", "ENE", "SE", "S", "SW", "W"];
      const marine = {
        swell_wave_height: swellM,
        swell_wave_period: periodS,
        swell_wave_direction: directions.indexOf(directionsFallback[(dayIndex + seed) % directionsFallback.length]) * 22.5,
        wave_height: swellM * 1.15,
        wave_period: periodS - 0.5,
        wave_direction: directions.indexOf(directionsFallback[(dayIndex + seed) % directionsFallback.length]) * 22.5,
        sea_level_height_msl: 0.3 + Math.sin(dayIndex + slotIndex) * 0.45,
        sea_surface_temperature: 17 + Math.sin(dayIndex * 0.2),
      };
      const weather = {
        wind_speed_10m: windKmh,
        wind_gusts_10m: windKmh * 1.35,
        wind_direction_10m: directions.indexOf(windDirections[(dayIndex + slotIndex + seed) % windDirections.length]) * 22.5,
        temperature_2m: 18 + Math.sin(dayIndex * 0.4) * 2,
        apparent_temperature: 18 + Math.sin(dayIndex * 0.4) * 2,
      };
      dayWindows.push(buildSnapshot(spot, weather, marine, sampleTime, now, timeWindows[slotIndex]));
    }
    windows[String(dayIndex)] = dayWindows;
    daily.push([...dayWindows].sort((a, b) => b.score - a.score)[0]);
  }
  return { status: "fallback", spot, daily, windows, best: [...daily].sort((a, b) => b.score - a.score)[0] };
}

export async function fetchForecastBundle(spot) {
  const now = new Date();
  const weatherUrl = buildUrl(forecastApi, {
    latitude: spot.latitude,
    longitude: spot.longitude,
    timezone: "Europe/Amsterdam",
    forecast_days: String(displayDays),
    hourly: "temperature_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
  });
  const marineUrl = buildUrl(marineApi, {
    latitude: spot.latitude,
    longitude: spot.longitude,
    timezone: "Europe/Amsterdam",
    forecast_days: String(displayDays),
    cell_selection: "sea",
    hourly: "wave_height,wave_period,wave_direction,swell_wave_height,swell_wave_period,swell_wave_direction,sea_level_height_msl,sea_surface_temperature",
  });

  try {
    const [weatherResponse, marineResponse] = await Promise.all([fetch(weatherUrl), fetch(marineUrl)]);
    if (!weatherResponse.ok || !marineResponse.ok) throw new Error("Forecast request failed");
    const weather = (await weatherResponse.json()).hourly;
    const marine = (await marineResponse.json()).hourly;
    const daily = [];
    const windows = {};

    for (let dayIndex = 0; dayIndex < displayDays; dayIndex += 1) {
      const targetDate = new Date(now);
      targetDate.setDate(now.getDate() + dayIndex);
      const dayWindows = [];
      for (const label of timeWindows) {
        const targetTime = new Date(targetDate);
        targetTime.setHours(Number(label.slice(0, 2)), 0, 0, 0);
        const [weatherSample, weatherTime] = nearestSnapshot(weather, targetTime, targetDate);
        const [marineSample, marineTime] = nearestSnapshot(marine, targetTime, targetDate);
        if (!weatherSample || !marineSample) continue;
        dayWindows.push(buildSnapshot(spot, weatherSample, marineSample, weatherTime || marineTime || targetTime, now, label));
      }
      if (dayWindows.length) {
        windows[String(dayIndex)] = dayWindows;
        daily.push([...dayWindows].sort((a, b) => b.score - a.score)[0]);
      }
    }
    if (!daily.length) throw new Error("No forecast windows");
    return { status: "live", spot, daily, windows, best: [...daily].sort((a, b) => b.score - a.score)[0] };
  } catch (error) {
    return fallbackBundle(spot);
  }
}
