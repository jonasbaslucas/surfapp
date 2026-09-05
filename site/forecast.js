const SurfKompasForecast = (() => {
  const forecastApi = "https://api.open-meteo.com/v1/forecast";
  const marineApi = "https://marine-api.open-meteo.com/v1/marine";
  const displayDays = 8;
  const defaultSpot = "kijkduin";
  const activityDefaults = { surf: "kijkduin", kite: "scheveningen-kite", windsurf: "strand-horst" };
  const directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  const timeWindows = ["06:00", "10:00", "14:00", "18:00"];
  const cache = new Map();

  const baseNorthSeaSpot = {
    excellent_wind: ["E", "ESE", "SE", "SSE"],
    good_wind: ["NE", "ENE", "S"],
    okay_wind: ["NNE", "SSW", "SW"],
    bad_wind: ["W", "WNW", "NW", "NNW", "N"],
    excellent_swell: ["NW", "NNW", "N"],
    good_swell: ["W", "WNW", "NNE", "SW"],
    bad_swell: ["S", "SSE", "SE", "E", "ENE", "NE"],
    minimum_swell_height: 0.3,
    good_swell_height: 0.8,
    excellent_swell_height: 1.2,
    minimum_period: 6,
    good_period: 9,
    excellent_period: 12,
  };

  function spot(id, name, latitude, longitude, region, description, overrides = {}) {
    return { ...baseNorthSeaSpot, ...overrides, id, name, latitude, longitude, region, description };
  }

  const surfSpots = [
    spot("scheveningen-noord", "Scheveningen Noord", 52.1168, 4.2798, "Zuid-Holland", "Drukke klassieker met veel surfscholen, zandbanken en energie rond de pier."),
    spot("scheveningen-zuid", "Scheveningen Zuid", 52.0969, 4.2518, "Zuid-Holland", "Iets rustiger dan Noord, vaak fijn voor beginners en longboarders."),
    spot("kijkduin", "Kijkduin", 52.0558, 4.2094, "Zuid-Holland", "Mellow Haagse spot met een lokale sfeer en vaak iets meer ruimte."),
    spot("ter-heijde", "Ter Heijde", 52.0304, 4.1686, "Zuid-Holland", "Westlandse beachbreak bij de Zandmotor, soms verrassend goede banken."),
    spot("hoek-van-holland", "Hoek van Holland", 51.9893, 4.1072, "Zuid-Holland", "Ruime beachbreak bij de Nieuwe Waterweg met stroming en veel windinvloed."),
    spot("maasvlakte", "Maasvlakte", 51.9516, 4.0314, "Zuid-Holland", "Exposed spot met veel ruimte en soms de meeste swell van Zuid-Holland.", { good_swell_height: 0.9, excellent_swell_height: 1.4 }),
    spot("ouddorp", "Ouddorp", 51.8212, 3.8676, "Zuid-Holland", "Brede, toegankelijke spot met veel zandbankvariatie."),
    spot("brouwersdam", "Brouwersdam", 51.7672, 3.8495, "Zeeland", "Bekende watersportplek met wind, ruimte en makkelijk parkeren."),
    spot("domburg", "Domburg", 51.5638, 3.4985, "Zeeland", "Een van Zeeland's bekendste surfspots, vaak wat meer zuidwestelijke energie.", { good_swell: ["W", "WNW", "SW", "WSW"] }),
    spot("vlissingen", "Vlissingen", 51.4538, 3.5709, "Zeeland", "Meer getij- en windgevoelig, maar leuk wanneer Zeeland aan staat.", { good_swell: ["W", "WSW", "SW"] }),
    spot("cadzand", "Cadzand", 51.3789, 3.3897, "Zeeland", "Zuidwestelijke kustspot met zandbanken en een ontspannen strandgevoel.", { good_swell: ["W", "WSW", "SW"] }),
    spot("zandvoort", "Zandvoort", 52.3717, 4.5329, "Noord-Holland", "Breed strand, sterke surfscene en makkelijk bereikbaar vanuit Amsterdam."),
    spot("bloemendaal", "Bloemendaal", 52.4047, 4.5429, "Noord-Holland", "Ruime strandbreak met relaxte sfeer en veel plek om te leren."),
    spot("noordwijk", "Noordwijk", 52.2476, 4.4269, "Zuid-Holland", "Toegankelijke beachbreak met brede zandbodem en veel beginnersruimte."),
    spot("katwijk", "Katwijk", 52.2052, 4.3940, "Zuid-Holland", "Nuchtere kustspot met veel strand en vaak iets minder drukte."),
    spot("wijk-aan-zee", "Wijk aan Zee", 52.4929, 4.5854, "Noord-Holland", "Rauwere Noordzee-spot bij de pier, populair als er wat meer push in zit."),
    spot("ijmuiden", "IJmuiden Noordpier", 52.4610, 4.5549, "Noord-Holland", "Pier-spot met wind- en stromingsinvloed, maar vaak goede Noordzee-karakter."),
    spot("bergen-aan-zee", "Bergen aan Zee", 52.6617, 4.6283, "Noord-Holland", "Brede Noord-Hollandse beachbreak met rustige, open strandsfeer."),
    spot("texel-paal-17", "Texel Paal 17", 53.0787, 4.7438, "Waddeneilanden", "Eilandspot met open Noordzee-gevoel en vaak iets andere wind dan de Randstad."),
    spot("ameland", "Ameland", 53.4510, 5.7250, "Waddeneilanden", "Rustige Wadden-spot met exposed strand en veel ruimte."),
  ];

  const kiteSpots = [
    spot("scheveningen-kite", "Scheveningen", 52.103, 4.259, "Zuid-Holland", "Iconische Noordzeespot; let op drukte, stroming en spotzones.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW", "S"], excellent_wind: ["W", "WSW", "SW"], bad_wind: ["E", "ESE", "SE"] }),
    spot("maasvlakte-kite", "Maasvlakte 2", 51.934, 3.999, "Zuid-Holland", "Veel ruimte, open water en een stevige golfkant.", { activity: "kite", good_wind: ["W", "WSW", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE", "SE"] }),
    spot("rockanje-kite", "Rockanje", 51.872, 4.044, "Zuid-Holland", "Ondiepere sportstrandspot met veel ruimte voor een relaxte sessie.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE", "SE"] }),
    spot("hoek-kite", "Hoek van Holland", 51.989, 4.107, "Zuid-Holland", "Open strand bij de Nieuwe Waterweg; richting en stroming zijn belangrijk.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE", "SE"] }),
    spot("brouwersdam-kite", "Brouwersdam", 51.767, 3.850, "Zeeland", "Veelzijdige windspot met zeezijde en beschutter water.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("vrouwenpolder-kite", "Vrouwenpolder", 51.593, 3.624, "Zeeland", "Ruime delta-spot waar wind en getij samen de sessie bepalen.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("oostvoorne-kite", "Oostvoorne", 51.914, 4.083, "Zuid-Holland", "Beschutter water met een fijne leercurve bij de juiste richting.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("wijk-kite", "Wijk aan Zee", 52.492, 4.585, "Noord-Holland", "Noordzeespot met golven, wind en een duidelijke launchzone.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("ijmuiden-kite", "IJmuiden", 52.461, 4.555, "Noord-Holland", "Exposed strand met veel energie en stromingsinvloed.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("zandmotor-kite", "Zandmotor", 52.03, 4.17, "Zuid-Holland", "Ruimte en variatie, maar check altijd de lokale zone en stroming.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("noordwijk-kite", "Noordwijk", 52.247, 4.427, "Zuid-Holland", "Toegankelijke kustspot met open ruimte.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("zandvoort-kite", "Zandvoort", 52.372, 4.533, "Noord-Holland", "Populaire beachbreak; kies rustigere momenten.", { activity: "kite", good_wind: ["NW", "W", "WSW", "SW"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("texel-kite", "Texel", 53.079, 4.744, "Waddeneilanden", "Eilandwind met open Noordzee en veel ruimte.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("workum-kite", "Workum", 52.98, 5.43, "Friesland", "Ondiep IJsselmeerwater en een populaire kiteschoolomgeving.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("makkum-kite", "Makkum", 53.05, 5.4, "Friesland", "Lagune en IJsselmeer in één watersportgebied.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("medemblik-kite", "Medemblik", 52.77, 5.1, "Noord-Holland", "IJsselmeerwind met vlak water en ruimte.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("strand-horst-kite", "Strand Horst", 52.31, 5.53, "Gelderland", "Ondiep Wolderwijd en een bekende trainingsspot.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("oesterdam-kite", "Oesterdam", 51.48, 4.21, "Zeeland", "Beschutte getijdeplek; check waterstand en lokale regels.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("grevelingen-kite", "Grevelingenmeer", 51.72, 3.92, "Zeeland", "Beschut meer met vlakker water en veel winddagen.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("muiderberg-kite", "Muiderberg", 52.33, 5.12, "Noord-Holland", "Gooimeer-spot met vlakker water en beperkte ruimte.", { activity: "kite", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
  ];

  const windsurfSpots = kiteSpots.map((item) => ({ ...item, activity: "windsurf" }));
  windsurfSpots.splice(0, 0,
    spot("strand-horst", "Strand Horst", 52.31, 5.53, "Gelderland", "Ondiep Wolderwijd, vlak water en veel ruimte om te leren.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("makkum-wind", "Makkum Beach", 53.05, 5.4, "Friesland", "Ondiep IJsselmeerwater, geschikt voor freeride en wave.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("stavoren-wind", "Stavoren", 52.88, 5.36, "Friesland", "Open IJsselmeerwind met ruimte voor langere rakken.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("workum-wind", "Workum", 52.98, 5.43, "Friesland", "Ondiep en toegankelijk IJsselmeerwater.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("lauwersoog-wind", "Lauwersoog", 53.41, 6.2, "Groningen", "Meer en wad met wind in verschillende richtingen.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("oesterdam-wind", "Oesterdam", 51.48, 4.21, "Zeeland", "Beschutte deltawateren met getijdekarakter.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("brouwersdam-wind", "Brouwersdam", 51.767, 3.85, "Zeeland", "Zeezijde en Grevelingen in één klassiek windsurfgebied.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
    spot("westeinder-wind", "Westeinderplassen", 52.24, 4.75, "Noord-Holland", "Meerwind dicht bij Amsterdam, met beperkte ruimte rond de oevers.", { activity: "windsurf", good_wind: ["NW", "W", "SW", "S"], excellent_wind: ["W", "SW"], bad_wind: ["E", "ESE"] }),
  );
  const activitySpots = { surf: surfSpots, kite: kiteSpots, windsurf: windsurfSpots.slice(0, 20) };

  function publicSpot(item) {
    return {
      id: item.id,
      name: item.name,
      region: item.region,
      description: item.description,
      latitude: item.latitude,
      longitude: item.longitude,
    };
  }

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
    return `${baseUrl}?${new URLSearchParams(params).toString()}`;
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

  function scoreWind(item, wind) {
    if (item.excellent_wind.includes(wind)) return [30, "Excellent"];
    if (item.good_wind.includes(wind)) return [24, "Good"];
    if (item.okay_wind.includes(wind)) return [15, "Okay"];
    if (item.bad_wind.includes(wind)) return [5, "Poor"];
    return [0, "Unknown"];
  }

  function scoreSwellDirection(item, direction) {
    if (item.excellent_swell.includes(direction)) return [20, "Excellent"];
    if (item.good_swell.includes(direction)) return [14, "Good"];
    if (item.bad_swell.includes(direction)) return [4, "Poor"];
    return [0, "Unknown"];
  }

  function scoreSwellHeight(item, height) {
    if (height < item.minimum_swell_height) return [0, "Flat"];
    if (height < item.good_swell_height) return [10, "Small"];
    if (height < item.excellent_swell_height) return [20, "Good"];
    return [25, "Excellent"];
  }

  function scorePeriod(item, period) {
    if (period < item.minimum_period) return [0, "Too short"];
    if (period < item.good_period) return [10, "Short"];
    if (period < item.excellent_period) return [20, "Good"];
    return [25, "Excellent"];
  }

  function evaluateConditions(item, wind, swellDirection, swellHeight, period) {
    if (item.activity === "kite" || item.activity === "windsurf") {
      const windScore = item.excellent_wind.includes(wind) ? 30 : item.good_wind.includes(wind) ? 25 : item.okay_wind.includes(wind) ? 16 : item.bad_wind.includes(wind) ? 4 : 10;
      const speed = arguments[5] || 0;
      const gust = arguments[6] || speed;
      const idealLow = item.activity === "kite" ? 14 : 12;
      const idealHigh = item.activity === "kite" ? 26 : 28;
      const speedScore = speed < idealLow ? 6 : speed > idealHigh + 8 ? 4 : speed > idealHigh ? 15 : 25;
      const gustSpread = Math.max(0, gust - speed);
      const gustScore = gustSpread > 14 ? 5 : gustSpread > 8 ? 12 : 20;
      const waterScore = swellHeight >= 0.4 && period >= 6 ? 20 : 14;
      const total = clamp(windScore + speedScore + gustScore + waterScore, 0, 100);
      const quality = total >= 82 ? "Excellent" : total >= 66 ? "Good" : total >= 45 ? "Okay" : "Poor";
      return { total_score: total, wind_score: windScore, wind_quality: quality, swell_direction_score: waterScore, swell_direction_quality: quality, swell_height_score: speedScore, swell_height_quality: quality, period_score: gustScore, period_quality: quality, verdict: quality };
    }
    const [windScore, windQuality] = scoreWind(item, wind);
    const [swellDirectionScore, swellDirectionQuality] = scoreSwellDirection(item, swellDirection);
    const [swellHeightScore, swellHeightQuality] = scoreSwellHeight(item, swellHeight);
    const [periodScore, periodQuality] = scorePeriod(item, period);
    const totalScore = windScore + swellDirectionScore + swellHeightScore + periodScore;
    return {
      total_score: totalScore,
      wind_score: windScore,
      wind_quality: windQuality,
      swell_direction_score: swellDirectionScore,
      swell_direction_quality: swellDirectionQuality,
      swell_height_score: swellHeightScore,
      swell_height_quality: swellHeightQuality,
      period_score: periodScore,
      period_quality: periodQuality,
      verdict: totalScore >= 82 ? "Firing" : totalScore >= 66 ? "Fun" : totalScore >= 45 ? "Maybe" : "Small / Messy",
    };
  }

  function vibe(score) {
    if (score >= 82) return { key: "excellent", nl: "Board pakken", en: "Grab your board", tone_nl: "Dit is een echte go: goede push, nette richting en een raam om je dag omheen te plannen.", tone_en: "This is a proper go: good push, clean direction, and a window worth planning around." };
    if (score >= 66) return { key: "good", nl: "Leuke sessie", en: "Fun session", tone_nl: "Ziet er surfbaar en leuk uit. Check de wind nog even, maar dit kan zeker de moeite zijn.", tone_en: "Looks surfable and fun. Check the wind once more, but this one is worth a look." };
    if (score >= 50) return { key: "maybe", nl: "Goed timen", en: "Time it right", tone_nl: "Niet perfect, wel kans op wat ritjes als je het juiste moment pakt.", tone_en: "Not perfect, but there could be a few waves if you catch the right window." };
    if (score >= 35) return { key: "messy", nl: "Check later", en: "Recheck later", tone_nl: "Er kan iets in zitten, maar verwacht rommelige Noordzee met weinig zekerheid.", tone_en: "There may be something in it, but expect messy North Sea surf with low confidence." };
    return { key: "quiet", nl: "Rustige stranddag", en: "Quiet beach day", tone_nl: "Mooi voor koffie, kijken en sfeer. Minder voor echte push onder je board.", tone_en: "Good for coffee, checking the sea, and beach vibes. Less good for real push under your board." };
  }

  function wavePowerKwm(heightM, periodS) {
    return Math.max(0, 0.49 * heightM * heightM * periodS);
  }

  function energyLabel(power) {
    if (power >= 12) return { nl: "Veel power", en: "Powerful" };
    if (power >= 6) return { nl: "Goede push", en: "Good push" };
    if (power >= 2) return { nl: "Kleine push", en: "Small push" };
    return { nl: "Weinig power", en: "Low power" };
  }

  function buildSnapshot(item, weather, marine, sampleTime, now, label) {
    const windSpeedKmh = number(weather.wind_speed_10m);
    const windGustKmh = number(weather.wind_gusts_10m);
    const windDirection = degreesToCompass(weather.wind_direction_10m);
    const swellHeightM = number(marine.swell_wave_height);
    const swellPeriodS = number(marine.swell_wave_period);
    const swellDirection = degreesToCompass(marine.swell_wave_direction);
    const waveHeightM = number(marine.wave_height);
    const wavePeriodS = number(marine.wave_period);
    const waveDirection = degreesToCompass(marine.wave_direction);
    const tideM = number(marine.sea_level_height_msl);
    const seaTempC = number(marine.sea_surface_temperature);
    const airTempC = number(weather.temperature_2m);
    const apparentTempC = number(weather.apparent_temperature);
    const power = wavePowerKwm(swellHeightM, swellPeriodS);
    const breakdown = evaluateConditions(item, windDirection, swellDirection, swellHeightM, swellPeriodS, windSpeedKmh * 0.539957, windGustKmh * 0.539957);
    const score = breakdown.total_score;

    return {
      activity: item.activity || "surf",
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
        airTempC: Number(airTempC.toFixed(1)),
        feelsLikeC: Number(apparentTempC.toFixed(1)),
        seaTempC: Number(seaTempC.toFixed(1)),
        tideM: Number(tideM.toFixed(2)),
      },
      breakdown,
    };
  }

  function makeFallbackBundle(spotId, activity = "surf") {
    const item = findSpot(spotId, activity);
    const now = new Date();
    const seed = item.name.split("").reduce((sum, char) => sum + char.charCodeAt(0), 0) % 19;
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
        const fallbackSwellDirections = ["NW", "WNW", "W", "NNW", "N", "SW"];
        const fallbackWindDirections = ["E", "ENE", "SE", "S", "SW", "W"];
        const swellDirection = fallbackSwellDirections[(dayIndex + seed) % fallbackSwellDirections.length];
        const windDirection = fallbackWindDirections[(dayIndex + slotIndex + seed) % fallbackWindDirections.length];
        dayWindows.push(buildSnapshot(
          item,
          {
            wind_speed_10m: windKmh,
            wind_gusts_10m: windKmh * 1.35,
            wind_direction_10m: directions.indexOf(windDirection) * 22.5,
            temperature_2m: 18 + Math.sin(dayIndex * 0.4) * 2,
            apparent_temperature: 18 + Math.sin(dayIndex * 0.4) * 2,
          },
          {
            swell_wave_height: swellM,
            swell_wave_period: periodS,
            swell_wave_direction: directions.indexOf(swellDirection) * 22.5,
            wave_height: swellM * 1.15,
            wave_period: periodS - 0.5,
            wave_direction: directions.indexOf(swellDirection) * 22.5,
            sea_level_height_msl: 0.3 + Math.sin(dayIndex + slotIndex) * 0.45,
            sea_surface_temperature: 17 + Math.sin(dayIndex * 0.2),
          },
          sampleTime,
          now,
          timeWindows[slotIndex],
        ));
      }
      windows[String(dayIndex)] = dayWindows;
      daily.push([...dayWindows].sort((a, b) => b.score - a.score)[0]);
    }
    return {
      status: "fallback",
      generatedAt: now.toISOString(),
      spot: publicSpot(item),
      daily,
      windows,
      best: [...daily].sort((a, b) => b.score - a.score)[0],
      sourceNote: {
        nl: "Offline voorbeelddata. Live model: Open-Meteo. Spotprofiel: Nederlandse publieke spotinformatie.",
        en: "Offline sample data. Live model: Open-Meteo. Spot profile: public Dutch spot information.",
      },
    };
  }

  function findSpot(spotId, activity = "surf") {
    const list = activitySpots[activity] || surfSpots;
    return list.find((item) => item.id === spotId) || list[0];
  }

  async function fetchForecastBundle(spotId, activity = "surf") {
    const cacheKey = `${activity}:${spotId}`;
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.cachedAt < 10 * 60 * 1000) return cached.payload;

    const item = findSpot(spotId, activity);
    const now = new Date();
    const weatherUrl = buildUrl(forecastApi, {
      latitude: item.latitude,
      longitude: item.longitude,
      timezone: "Europe/Amsterdam",
      forecast_days: String(displayDays),
      hourly: "temperature_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
    });
    const marineUrl = buildUrl(marineApi, {
      latitude: item.latitude,
      longitude: item.longitude,
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
          dayWindows.push(buildSnapshot(item, weatherSample, marineSample, weatherTime || marineTime || targetTime, now, label));
        }
        if (dayWindows.length) {
          windows[String(dayIndex)] = dayWindows;
          daily.push([...dayWindows].sort((a, b) => b.score - a.score)[0]);
        }
      }

      if (!daily.length) throw new Error("No forecast windows returned");
      const payload = {
        status: "live",
        generatedAt: now.toISOString(),
        spot: publicSpot(item),
        daily,
        windows,
        best: [...daily].sort((a, b) => b.score - a.score)[0],
        sourceNote: {
          nl: item.activity === "kite"
            ? "Live Open-Meteo wind- en marinedata. Spotrichting en veiligheid afgestemd op NKV-spotinformatie."
            : item.activity === "windsurf"
              ? "Live Open-Meteo wind- en marinedata. Zee- en binnenwaterspots samengesteld uit publieke windsurfspotinformatie."
              : "Live Open-Meteo golf-, swell- en getijdata. Nabije stranden kunnen dezelfde golf-gridcel delen.",
          en: item.activity === "kite"
            ? "Live Open-Meteo wind and marine data. Spot direction and safety aligned with NKV spot information."
            : item.activity === "windsurf"
              ? "Live Open-Meteo wind and marine data. Coastal and inland spots built from public windsurf spot information."
              : "Live Open-Meteo wave, swell and tide data. Nearby beaches can share the same wave grid cell.",
        },
      };
      cache.set(cacheKey, { cachedAt: Date.now(), payload });
      return payload;
    } catch (error) {
      const payload = makeFallbackBundle(spotId, activity);
      cache.set(cacheKey, { cachedAt: Date.now(), payload });
      return payload;
    }
  }

  return {
    defaultSpot,
    activities: ["surf", "kite", "windsurf"],
    spots: surfSpots.map(publicSpot),
    getSpots: (activity) => (activitySpots[activity] || surfSpots).map(publicSpot),
    defaultSpotFor: (activity) => activityDefaults[activity] || defaultSpot,
    fetchForecastBundle,
  };
})();
