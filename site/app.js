const i18n = {
  nl: {
    beginnerMode: "Beginner",
    expertMode: "Expert",
    eyebrow: "Nederlandse surfvoorspelling",
    heroTitle: "Vind het beste moment om te surfen.",
    heroCopy: "Een mooie, rustige forecast voor Nederlandse surfers: kies een spot, check de komende week en zoom in op 06:00, 10:00, 14:00 of 18:00.",
    spotsLabel: "Surfspots",
    score: "score",
    selectedWindow: "Gekozen surfraam",
    weekForecast: "Komende 7 dagen",
    dayParts: "Dag verdeeld in 4 momenten",
    expertDetails: "Expert details",
    wind: "Wind",
    swell: "Swell",
    energy: "Swellenergie",
    temperature: "Temperatuur",
    loading: "Forecast laden...",
    live: "Live model",
    fallback: "Voorbeelddata",
    search: "Zoek spot of regio",
    best: "Beste moment",
    gusts: "stoten",
    period: "periode",
    waves: "golven",
    tide: "tij",
    feels: "voelt als",
    sea: "zee",
    sourcePrefix: "Bron",
    energyExplain: "Geschatte deep-water swell power",
    charmNorthSea: "Noordzee vibes",
    charmSevenDays: "7 dagen",
    charmFourWindows: "4 momenten",
  },
  en: {
    beginnerMode: "Beginner",
    expertMode: "Expert",
    eyebrow: "Dutch surf forecast",
    heroTitle: "Find the best time to surf.",
    heroCopy: "A clean forecast for Dutch surfers: choose a spot, scan the week, then zoom into 06:00, 10:00, 14:00 or 18:00.",
    spotsLabel: "Surf spots",
    score: "score",
    selectedWindow: "Selected surf window",
    weekForecast: "Next 7 days",
    dayParts: "Day split into 4 moments",
    expertDetails: "Expert details",
    wind: "Wind",
    swell: "Swell",
    energy: "Swell energy",
    temperature: "Temperature",
    loading: "Loading forecast...",
    live: "Live model",
    fallback: "Sample data",
    search: "Search spot or region",
    best: "Best window",
    gusts: "gusts",
    period: "period",
    waves: "waves",
    tide: "tide",
    feels: "feels",
    sea: "sea",
    sourcePrefix: "Source",
    energyExplain: "Estimated deep-water swell power",
    charmNorthSea: "North Sea vibes",
    charmSevenDays: "7 days",
    charmFourWindows: "4 windows",
  },
};

let state = {
  lang: "nl",
  expert: false,
  spots: [],
  selectedSpot: null,
  forecast: null,
  selectedDay: 0,
  selectedWindow: 0,
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
  scoreValue: document.querySelector("#scoreValue"),
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
  expertToggle: document.querySelector("#expertToggle"),
  expertPanel: document.querySelector("#expertPanel"),
  expertGrid: document.querySelector("#expertGrid"),
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
  els.expertToggle.querySelector("span").textContent = state.expert ? t("expertMode") : t("beginnerMode");
  render();
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

async function loadSpots() {
  state.spots = SurfKompasForecast.spots;
  state.selectedSpot = state.selectedSpot || SurfKompasForecast.defaultSpot;
  renderSpots();
}

async function loadForecast(spotId) {
  state.selectedSpot = spotId;
  state.selectedDay = 0;
  state.selectedWindow = 0;
  els.vibeTitle.textContent = t("loading");
  renderSpots();
  state.forecast = await SurfKompasForecast.fetchForecastBundle(spotId);
  render();
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
  els.tempValue.textContent = `${item.weather.airTempC} C`;
  els.tempMeta.textContent = `${t("feels")} ${item.weather.feelsLikeC} C · ${t("sea")} ${item.weather.seaTempC} C`;
}

function renderExpert(item) {
  els.expertPanel.hidden = !state.expert;
  if (!state.expert) return;
  const b = item.breakdown;
  els.expertGrid.innerHTML = `
    <div class="expert-item"><span>${t("wind")}</span><small>${b.wind_score}/30 · ${b.wind_quality}</small></div>
    <div class="expert-item"><span>${t("swell")}</span><small>${b.swell_direction_score}/20 · ${b.swell_direction_quality}</small></div>
    <div class="expert-item"><span>${t("energy")}</span><small>${item.swell.energyKwm} kW/m · ${item.swell.periodS}s</small></div>
    <div class="expert-item"><span>${t("tide")}</span><small>${item.weather.tideM} m</small></div>
    <div class="expert-item"><span>${t("gusts")}</span><small>${item.wind.gustKmh} km/u · ${item.wind.gustKt} kt</small></div>
    <div class="expert-item"><span>${t("waves")}</span><small>${item.waves.heightM} m · ${item.waves.periodS}s · ${item.waves.direction}</small></div>
    <div class="expert-item"><span>Coords</span><small>${state.forecast.spot.latitude}, ${state.forecast.spot.longitude}</small></div>
    <div class="expert-item"><span>${t("score")}</span><small>${b.total_score}/100 · ${b.verdict}</small></div>
  `;
}

function render() {
  renderSpots();
  if (!state.forecast) return;

  const item = selectedWindow();
  const spot = state.forecast.spot;
  els.statusLabel.textContent = state.forecast.status === "live" ? t("live") : t("fallback");
  els.spotName.textContent = spot.name;
  els.spotDescription.textContent = spot.description;
  els.scoreValue.textContent = item.score;
  els.vibeTitle.textContent = local(item.vibe);
  els.vibeText.textContent = localTone(item.vibe);
  els.sourceNote.textContent = `${t("sourcePrefix")}: ${local(state.forecast.sourceNote)}`;

  document.querySelector(".score-medallion").className = `score-medallion ${scoreClass(item.score)} ${scoreTone(item.score)}`;
  renderDayRail();
  renderWindows();
  renderMetrics(item);
  renderExpert(item);
}

document.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});

els.expertToggle.addEventListener("click", () => {
  state.expert = !state.expert;
  els.expertToggle.classList.toggle("active", state.expert);
  els.expertToggle.setAttribute("aria-pressed", String(state.expert));
  els.expertToggle.querySelector("span").textContent = state.expert ? t("expertMode") : t("beginnerMode");
  render();
});

els.spotSearch.addEventListener("input", renderSpots);

els.spotList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-spot]");
  if (!button) return;
  loadForecast(button.dataset.spot);
});

els.dayRail.addEventListener("click", (event) => {
  const button = event.target.closest("[data-day]");
  if (!button) return;
  state.selectedDay = Number(button.dataset.day);
  state.selectedWindow = 0;
  render();
});

els.windowGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-window]");
  if (!button) return;
  state.selectedWindow = Number(button.dataset.window);
  render();
});

setLanguage("nl");
loadSpots().then(() => loadForecast(state.selectedSpot));
