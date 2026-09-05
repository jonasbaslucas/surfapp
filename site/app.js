const i18n = {
  nl: {
    chooseSport: "Kies je sport",
    activityNote: "Elke sport krijgt zijn eigen conditiescore.",
    activitySurf: "Golfsurfen",
    activitySurfCopy: "Swell, periode en golfenergie",
    activityKite: "Kitesurfen",
    activityKiteCopy: "Wind, vlagen en veilige richting",
    activityWind: "Windsurfen",
    activityWindCopy: "Wind, water en ruimte om te varen",
    bestSpot: "Beste spot van vandaag",
    useSpot: "Bekijk deze spot",
    safety: "Veiligheidsstatus",
    safetyGood: "Condities zien er rustig genoeg uit",
    safetyCaution: "Let op vlagen, stroming of drukte",
    safetyStrong: "Alleen kiezen als je dit goed beheerst",
    beginnerMode: "Kustkook",
    expertMode: "Spotpro",
    eyebrow: "Nederlandse surfvoorspelling",
    heroTitle: "Vind het beste moment om te surfen.",
    heroCopy: "Een mooie, rustige forecast voor Nederlandse surfers: kies een spot, check de komende week en zoom in op 06:00, 10:00, 14:00 of 18:00.",
    spotsLabel: "Surfspots",
    score: "score",
    selectedWindow: "Surfadvies",
    weekForecast: "Vandaag + 7 dagen",
    dayParts: "Dag verdeeld in 4 momenten",
    expertDetails: "Expert details",
    proWhy: "Waarom deze score?",
    proSpot: "Spotgevoel",
    proGear: "Board & level",
    proData: "Extra data",
    wind: "Wind",
    swell: "Swell",
    energy: "Swellenergie",
    temperature: "Temperatuur",
    loading: "Forecast laden...",
    live: "Live model",
    fallback: "Voorbeelddata",
    search: "Zoek spot of regio",
    best: "Beste moment",
    gusts: "Windstoten",
    period: "Periode",
    waves: "Golven",
    tide: "Getij",
    feels: "Voelt als",
    sea: "Zee",
    sourcePrefix: "Bron",
    energyExplain: "Geschatte swellenergie in diep water",
    charmNorthSea: "Noordzee vibes",
    charmSevenDays: "8 dagen",
    charmFourWindows: "4 momenten",
    changeSpot: "Andere spot",
    changeDay: "Andere dag",
    kmh: "km/u",
  },
  en: {
    chooseSport: "Choose your sport",
    activityNote: "Each sport gets its own conditions score.",
    activitySurf: "Surfing",
    activitySurfCopy: "Swell, period and wave energy",
    activityKite: "Kitesurfing",
    activityKiteCopy: "Wind, gusts and safe direction",
    activityWind: "Windsurfing",
    activityWindCopy: "Wind, water and room to sail",
    bestSpot: "Best spot today",
    useSpot: "View this spot",
    safety: "Safety status",
    safetyGood: "Conditions look calm enough",
    safetyCaution: "Watch gusts, current or crowds",
    safetyStrong: "Only choose this if you are confident",
    beginnerMode: "Kook",
    expertMode: "Pro",
    eyebrow: "Dutch surf forecast",
    heroTitle: "Find the best time to surf.",
    heroCopy: "A clean forecast for Dutch surfers: choose a spot, scan the week, then zoom into 06:00, 10:00, 14:00 or 18:00.",
    spotsLabel: "Surf spots",
    score: "score",
    selectedWindow: "Surf advice",
    weekForecast: "Today + 7 days",
    dayParts: "Day split into 4 moments",
    expertDetails: "Expert details",
    proWhy: "Why this score?",
    proSpot: "Spot read",
    proGear: "Board & level",
    proData: "Extra data",
    wind: "Wind",
    swell: "Swell",
    energy: "Swell energy",
    temperature: "Temperature",
    loading: "Loading forecast...",
    live: "Live model",
    fallback: "Sample data",
    search: "Search spot or region",
    best: "Best window",
    gusts: "Gusts",
    period: "Period",
    waves: "Waves",
    tide: "Tide",
    feels: "Feels like",
    sea: "Sea",
    sourcePrefix: "Source",
    energyExplain: "Estimated deep-water swell energy",
    charmNorthSea: "North Sea vibes",
    charmSevenDays: "8 days",
    charmFourWindows: "4 windows",
    changeSpot: "Change spot",
    changeDay: "Change day",
    kmh: "km/h",
  },
};

let state = {
  lang: "nl",
  activity: null,
  expert: false,
  spots: [],
  selectedSpot: null,
  forecast: null,
  selectedDay: 0,
  selectedWindow: 0,
  mobileStep: "spots",
  recommendation: null,
};

const els = {
  html: document.documentElement,
  brandWord: document.querySelector(".brand-word"),
  spotCount: document.querySelector("#spotCount"),
  spotSearch: document.querySelector("#spotSearch"),
  spotList: document.querySelector("#spotList"),
  statusLabel: document.querySelector("#statusLabel"),
  spotName: document.querySelector("#spotName"),
  spotDescription: document.querySelector("#spotDescription"),
  liveWind: document.querySelector("#liveWind"),
  liveSwell: document.querySelector("#liveSwell"),
  liveEnergy: document.querySelector("#liveEnergy"),
  safetyStatus: document.querySelector("#safetyStatus"),
  scoreValue: document.querySelector("#scoreValue"),
  adviceScoreValue: document.querySelector("#adviceScoreValue"),
  vibeTitle: document.querySelector("#vibeTitle"),
  vibeText: document.querySelector("#vibeText"),
  sourceNote: document.querySelector("#sourceNote"),
  dayRail: document.querySelector("#dayRail"),
  selectedDate: document.querySelector("#selectedDate"),
  windowGrid: document.querySelector("#windowGrid"),
  windValue: document.querySelector("#windValue"),
  windMeta: document.querySelector("#windMeta"),
  swellValue: document.querySelector("#swellValue"),
  swellMeta: document.querySelector("#swellMeta"),
  energyValue: document.querySelector("#energyValue"),
  energyMeta: document.querySelector("#energyMeta"),
  tempValue: document.querySelector("#tempValue"),
  tempMeta: document.querySelector("#tempMeta"),
  modeOptions: document.querySelectorAll("[data-mode-option]"),
  expertPanel: document.querySelector("#expertPanel"),
  expertGrid: document.querySelector("#expertGrid"),
  backToSpots: document.querySelector("#backToSpots"),
  backToDays: document.querySelector("#backToDays"),
  activityGrid: document.querySelector("#activityGrid"),
  spotRecommendation: document.querySelector("#spotRecommendation"),
  recommendationName: document.querySelector("#recommendationName"),
  recommendationText: document.querySelector("#recommendationText"),
  useRecommendation: document.querySelector("#useRecommendation"),
  appShell: document.querySelector("#appShell"),
  forecastArea: document.querySelector("#forecastArea"),
};

function t(key) {
  return i18n[state.lang][key] || key;
}

function local(keyed) {
  if (!keyed) return "";
  return keyed[state.lang] || keyed.en || keyed.nl || "";
}

function localTone(vibe) {
  if (!vibe) return "";
  return state.lang === "nl" ? vibe.tone_nl : vibe.tone_en;
}

function setLanguage(lang) {
  state.lang = lang;
  els.html.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === lang);
  });
  els.brandWord.textContent = lang === "nl" ? "SurfKompas" : "SurfCompass";
  els.spotSearch.placeholder = t("search");
  syncExpertToggles();
  render();
}

function syncExpertToggles() {
  els.modeOptions.forEach((button) => {
    const isPro = button.dataset.modeOption === "pro";
    button.setAttribute("aria-pressed", String(isPro === state.expert));
    button.textContent = isPro ? t("expertMode") : t("beginnerMode");
  });
}

function scoreClass(score) {
  if (score >= 82) return "excellent";
  if (score >= 66) return "good";
  if (score >= 50) return "maybe";
  if (score >= 35) return "messy";
  return "quiet";
}

function scoreTone(score) {
  if (score >= 82) return "score-excellent";
  if (score >= 66) return "score-good";
  if (score >= 45) return "score-okay";
  return "score-bad";
}

function renderSpots() {
  const query = els.spotSearch.value.trim().toLowerCase();
  const visible = state.spots.filter((spot) => {
    return `${spot.name} ${spot.region} ${spot.description}`.toLowerCase().includes(query);
  });
  els.spotCount.textContent = visible.length;
  els.spotList.innerHTML = visible.map((spot) => `
    <button class="spot-button ${spot.id === state.selectedSpot ? "active" : ""}" type="button" data-spot="${spot.id}">
      <strong>${spot.name}</strong>
      <small>${spot.region}</small>
    </button>
  `).join("");
}

function activityName() {
  return t(state.activity === "kite" ? "activityKite" : state.activity === "windsurf" ? "activityWind" : "activitySurf");
}

function renderActivities() {
  document.querySelectorAll("[data-activity]").forEach((button) => button.classList.toggle("active", button.dataset.activity === state.activity));
}

async function loadSpots() {
  if (!state.activity) return;
  state.spots = SurfKompasForecast.getSpots(state.activity);
  state.selectedSpot = null;
  els.appShell.hidden = false;
  els.forecastArea.hidden = true;
  renderSpots();
  renderActivities();
}

async function loadForecast(spotId) {
  if (!state.activity || !spotId) return;
  state.selectedSpot = spotId;
  state.selectedDay = 0;
  state.selectedWindow = 0;
  els.vibeTitle.textContent = t("loading");
  document.body.classList.add("is-loading");
  renderSpots();
  try {
    state.forecast = await SurfKompasForecast.fetchForecastBundle(spotId, state.activity);
    els.forecastArea.hidden = false;
    render();
  } finally {
    document.body.classList.remove("is-loading");
  }
}

async function refreshRecommendation() {
  const candidates = state.spots.slice(0, 8);
  try {
    const bundles = await Promise.all(candidates.map((spot) => SurfKompasForecast.fetchForecastBundle(spot.id, state.activity)));
    const ranked = bundles.map((bundle) => ({ bundle, item: bundle.daily[0] })).sort((a, b) => b.item.score - a.item.score);
    const best = ranked[0];
    if (!best || best.bundle.spot.id === state.selectedSpot) {
      state.recommendation = null;
    } else {
      state.recommendation = { id: best.bundle.spot.id, name: best.bundle.spot.name, score: best.item.score, vibe: best.item.vibe };
    }
    renderRecommendation();
  } catch (error) {
    state.recommendation = null;
  }
}

function renderRecommendation() {
  if (!state.recommendation) {
    els.spotRecommendation.hidden = true;
    return;
  }
  els.spotRecommendation.hidden = false;
  els.recommendationName.textContent = `${state.recommendation.name} · ${state.recommendation.score}/100`;
  els.recommendationText.textContent = state.lang === "nl"
    ? `${local(state.recommendation.vibe)} past vandaag het best bij ${activityName().toLowerCase()}. Je kunt altijd een andere spot kiezen.`
    : `${local(state.recommendation.vibe)} is the best match today for ${activityName().toLowerCase()}. You can always choose another spot.`;
}

function setActivity(activity) {
  if (activity === state.activity && state.spots.length) return;
  state.activity = activity;
  state.forecast = null;
  state.recommendation = null;
  state.selectedSpot = null;
  setMobileStep("spots");
  loadSpots();
}

function setMobileStep(step) {
  state.mobileStep = step;
  document.body.classList.remove("mobile-step-spots", "mobile-step-days", "mobile-step-advice");
  document.body.classList.add(`mobile-step-${step}`);
}

function selectedWindow() {
  if (!state.forecast) return null;
  const windows = state.forecast.windows[String(state.selectedDay)] || [];
  return windows[state.selectedWindow] || windows[0] || state.forecast.daily[state.selectedDay] || state.forecast.best;
}

function renderDayRail() {
  const days = state.forecast.daily;
  els.dayRail.innerHTML = days.map((day, index) => `
    <button class="day-card ${state.selectedDay === index ? "active" : ""}" type="button" data-day="${index}">
      <span class="day-top">
        <strong>${local(day.dayLabel)}</strong>
        <span class="pill-score ${scoreTone(day.score)}">${day.score}</span>
      </span>
      <span class="day-date">${day.shortDate}</span>
      <span class="day-meta">${local(day.vibe)} · ${day.swell.heightM} m · ${day.swell.energyKwm} kW/m</span>
      <span class="day-meta">${day.wind.speedKt} kt ${day.wind.direction}</span>
    </button>
  `).join("");
}

function renderWindows() {
  const windows = state.forecast.windows[String(state.selectedDay)] || [];
  els.windowGrid.innerHTML = windows.map((item, index) => `
    <button class="window-card ${state.selectedWindow === index ? "active" : ""}" type="button" data-window="${index}">
      <span class="window-top">
        <strong>${item.hour}</strong>
        <span class="pill-score ${scoreTone(item.score)}">${item.score}</span>
      </span>
      <h4>${local(item.vibe)}</h4>
      <span class="window-meta">${item.swell.heightM} m · ${item.swell.periodS}s · ${item.wind.speedKt} kt</span>
      <span class="window-meta energy-line">${local(item.swell.energyLabel)} · ${item.swell.energyKwm} kW/m</span>
    </button>
  `).join("");
  const day = state.forecast.daily[state.selectedDay];
  els.selectedDate.textContent = `${local(day.dayLabel)} · ${day.shortDate}`;
}

function renderMetrics(item) {
  els.windValue.textContent = `${item.wind.speedKt} kt ${item.wind.direction}`;
  els.windMeta.textContent = `${t("gusts")} ${item.wind.gustKt} kt`;
  els.swellValue.textContent = `${item.swell.heightM} m ${item.swell.direction}`;
  els.swellMeta.textContent = `${item.swell.periodS}s ${t("period")} · ${t("waves")} ${item.waves.heightM} m`;
  els.energyValue.textContent = `${item.swell.energyKwm} kW/m`;
  els.energyMeta.textContent = `${local(item.swell.energyLabel)} · ${t("energyExplain")}`;
  els.tempValue.textContent = `${item.weather.airTempC} °C`;
  els.tempMeta.textContent = `${t("feels")} ${item.weather.feelsLikeC} °C · ${t("sea")} ${item.weather.seaTempC} °C`;
}

function qualityLabel(value) {
  const labels = {
    Excellent: { nl: "Top", en: "Excellent" },
    Good: { nl: "Goed", en: "Good" },
    Okay: { nl: "Oké", en: "Okay" },
    Poor: { nl: "Matig", en: "Poor" },
    Unknown: { nl: "Onzeker", en: "Unknown" },
    Flat: { nl: "Vlak", en: "Flat" },
    Small: { nl: "Klein", en: "Small" },
    "Too short": { nl: "Korte periode", en: "Short period" },
    Short: { nl: "Kort", en: "Short" },
  };
  return local(labels[value] || { nl: value, en: value });
}

function proBreakdownText(item) {
  const b = item.breakdown;
  const parts = [
    `${t("wind")} ${b.wind_score}/30 (${qualityLabel(b.wind_quality)})`,
    `${t("swell")} ${b.swell_direction_score + b.swell_height_score}/45 (${qualityLabel(b.swell_direction_quality)}, ${qualityLabel(b.swell_height_quality)})`,
    `${t("period")} ${b.period_score}/25 (${qualityLabel(b.period_quality)})`,
  ];
  return parts.join(" · ");
}

function proSpotText(item) {
  const spot = state.forecast.spot;
  const b = item.breakdown;
  if (state.lang === "nl") {
    if (b.wind_score >= 24 && b.swell_direction_score >= 14) return `${spot.name} ligt mooi voor deze combinatie: wind en swell staan allebei redelijk gunstig.`;
    if (b.wind_score < 15 && b.swell_direction_score >= 14) return `${spot.name} krijgt wel swell, maar de wind maakt het waarschijnlijk rommeliger.`;
    if (b.wind_score >= 24 && b.swell_height_score < 10) return `De wind helpt, maar er zit weinig formaat in de swell voor ${spot.name}.`;
    return `${spot.name} kan werken, maar het hangt vooral af van lokale banken en getij.`;
  }
  if (b.wind_score >= 24 && b.swell_direction_score >= 14) return `${spot.name} lines up well for this mix: wind and swell are both fairly friendly.`;
  if (b.wind_score < 15 && b.swell_direction_score >= 14) return `${spot.name} has swell, but the wind probably makes it messier.`;
  if (b.wind_score >= 24 && b.swell_height_score < 10) return `The wind helps, but the swell size is light for ${spot.name}.`;
  return `${spot.name} could work, but local banks and tide will matter most.`;
}

function proGearText(item) {
  const score = item.score;
  const height = item.swell.heightM;
  const wind = item.wind.speedKt;
  if (state.lang === "nl") {
    if (score >= 82 && height >= 1.1) return "Shortboard kan. Voor beginners alleen relaxed als je comfortabel bent met drukte en stroming.";
    if (score >= 66) return "Fish, midlength of funboard voelt logisch. Kook-modus: rustig instappen en setjes afwachten.";
    if (height < 0.6) return "Longboard, foamie of gewoon chill strandcheck. Verwacht weinig push onder je board.";
    if (wind > 20) return "Meer voor ervaren surfers: neem volume mee en verwacht chop, drift en harde paddles.";
    return "Funboard of midlength is de veilige keuze. Verwacht korte Noordzee-ritjes.";
  }
  if (score >= 82 && height >= 1.1) return "Shortboard can work. Beginners: only mellow if you are comfortable with current and crowds.";
  if (score >= 66) return "Fish, midlength or funboard makes sense. Kook mode: ease in and wait for sets.";
  if (height < 0.6) return "Longboard, foamie or just a beach check. Expect limited push under your board.";
  if (wind > 20) return "More experienced-only: bring volume and expect chop, drift and harder paddles.";
  return "Funboard or midlength is the safe call. Expect short North Sea rides.";
}

function renderExpert(item) {
  els.expertPanel.hidden = !state.expert;
  if (!state.expert) return;
  els.expertGrid.innerHTML = `
    <div class="expert-item"><span>${t("proWhy")}</span><small>${proBreakdownText(item)}</small></div>
    <div class="expert-item"><span>${t("proSpot")}</span><small>${proSpotText(item)}</small></div>
    <div class="expert-item"><span>${t("proGear")}</span><small>${proGearText(item)}</small></div>
    <div class="expert-item"><span>${t("proData")}</span><small>${t("tide")} ${item.weather.tideM} m · ${t("gusts")} ${item.wind.gustKmh} ${t("kmh")} · ${t("waves")} ${item.waves.periodS}s ${item.waves.direction}</small></div>
  `;
}

function isMobileFlow() {
  return window.matchMedia("(max-width: 720px)").matches;
}

function nudgeMobileTo(selector) {
  if (!isMobileFlow()) return;
  window.setTimeout(() => {
    document.querySelector(selector)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }, 120);
}

function render() {
  setMobileStep(state.mobileStep);
  renderSpots();
  if (!state.forecast) return;

  const item = selectedWindow();
  const spot = state.forecast.spot;
  els.statusLabel.textContent = state.forecast.status === "live" ? t("live") : t("fallback");
  els.spotName.textContent = spot.name;
  els.spotDescription.textContent = spot.description;
  els.liveWind.textContent = `${t("wind")}: ${item.wind.speedKt} kt ${item.wind.direction}`;
  els.liveSwell.textContent = `${t("swell")}: ${item.swell.heightM} m · ${item.swell.periodS}s`;
  els.liveEnergy.textContent = `${t("energy")}: ${item.swell.energyKwm} kW/m`;
  const safetyKey = item.score < 35 ? "safetyStrong" : item.score < 55 ? "safetyCaution" : "safetyGood";
  els.safetyStatus.textContent = `${t("safety")}: ${t(safetyKey)}`;
  els.safetyStatus.className = `safety-status ${item.score < 35 ? "is-strong" : item.score < 55 ? "is-caution" : "is-good"}`;
  els.scoreValue.textContent = item.score;
  els.adviceScoreValue.textContent = item.score;
  els.vibeTitle.textContent = local(item.vibe);
  els.vibeText.textContent = localTone(item.vibe);
  els.sourceNote.textContent = `${t("sourcePrefix")}: ${local(state.forecast.sourceNote)}`;

  document.querySelector(".score-medallion").className = `score-medallion ${scoreClass(item.score)} ${scoreTone(item.score)}`;
  document.querySelector(".advice-score").className = `advice-score ${scoreTone(item.score)}`;
  renderDayRail();
  renderWindows();
  renderMetrics(item);
  renderExpert(item);
  renderRecommendation();
}

document.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});

els.modeOptions.forEach((button) => {
  button.addEventListener("click", () => {
    state.expert = button.dataset.modeOption === "pro";
    syncExpertToggles();
    if (state.forecast) render();
  });
});

els.activityGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-activity]");
  if (button) setActivity(button.dataset.activity);
});

els.useRecommendation.addEventListener("click", () => {
  if (!state.recommendation) return;
  setMobileStep("days");
  loadForecast(state.recommendation.id);
  nudgeMobileTo(".forecast-area");
});

els.spotSearch.addEventListener("input", renderSpots);

els.spotList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-spot]");
  if (!button) return;
  setMobileStep("days");
  loadForecast(button.dataset.spot).then(refreshRecommendation);
  nudgeMobileTo(".forecast-area");
});

els.dayRail.addEventListener("click", (event) => {
  const button = event.target.closest("[data-day]");
  if (!button) return;
  state.selectedDay = Number(button.dataset.day);
  state.selectedWindow = 0;
  setMobileStep("advice");
  render();
  nudgeMobileTo(".forecast-area");
});

els.windowGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-window]");
  if (!button) return;
  state.selectedWindow = Number(button.dataset.window);
  setMobileStep("advice");
  render();
  nudgeMobileTo(".today-card");
});

els.backToSpots.addEventListener("click", () => {
  setMobileStep("spots");
  render();
  nudgeMobileTo(".spot-panel");
});

els.backToDays.addEventListener("click", () => {
  setMobileStep("days");
  render();
  nudgeMobileTo(".forecast-area");
});

setMobileStep("spots");
setLanguage("nl");
renderActivities();
