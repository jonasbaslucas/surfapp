import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  ImageBackground,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import { defaultSpot, findSpot, surfSpots } from "./src/surfSpots";
import { fetchForecastBundle } from "./src/surfForecast";

const heroImage = require("./assets/surfkompas-hero.png");
const boardImage = require("./assets/surfboards-poster.png");

const copy = {
  nl: {
    brand: "SurfKompas",
    eyebrow: "Nederlandse surfvoorspelling",
    intro: "Kies een spot, check de komende week en zoom in op ochtend, middag of avond.",
    live: "Live model",
    fallback: "Voorbeelddata",
    week: "Komende 7 dagen",
    moments: "Momenten vandaag",
    wind: "Wind",
    swell: "Swell",
    energy: "Energie",
    temp: "Temp",
    expert: "Expert",
    beginner: "Beginner",
    refresh: "Ververs",
    gusts: "stoten",
    period: "periode",
    waves: "golven",
    tide: "tij",
    source: "Open-Meteo modeldata · nabijgelegen stranden kunnen dezelfde golf-gridcel delen.",
  },
  en: {
    brand: "SurfCompass",
    eyebrow: "Dutch surf forecast",
    intro: "Choose a spot, scan the week, then zoom into morning, midday or evening.",
    live: "Live model",
    fallback: "Sample data",
    week: "Next 7 days",
    moments: "Daily windows",
    wind: "Wind",
    swell: "Swell",
    energy: "Energy",
    temp: "Temp",
    expert: "Expert",
    beginner: "Beginner",
    refresh: "Refresh",
    gusts: "gusts",
    period: "period",
    waves: "waves",
    tide: "tide",
    source: "Open-Meteo model data · nearby beaches can share the same wave-grid cell.",
  },
};

function local(value, lang) {
  return value?.[lang] || value?.nl || value?.en || "";
}

function scoreTone(score) {
  if (score >= 82) return styles.scoreExcellent;
  if (score >= 66) return styles.scoreGood;
  if (score >= 45) return styles.scoreOkay;
  return styles.scoreBad;
}

function scoreBorder(score) {
  if (score >= 82) return "#11633f";
  if (score >= 66) return "#38a96f";
  if (score >= 45) return "#eda63a";
  return "#d84f42";
}

function Metric({ label, value, sub, highlighted }) {
  return (
    <View style={[styles.metric, highlighted && styles.metricHighlighted]}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
      <Text style={styles.metricSub}>{sub}</Text>
    </View>
  );
}

export default function App() {
  const [lang, setLang] = useState("nl");
  const [expert, setExpert] = useState(false);
  const [spotId, setSpotId] = useState(defaultSpot);
  const [forecast, setForecast] = useState(null);
  const [dayIndex, setDayIndex] = useState(0);
  const [windowIndex, setWindowIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const t = copy[lang];
  const spot = useMemo(() => findSpot(spotId), [spotId]);
  const windows = forecast?.windows?.[String(dayIndex)] || [];
  const selected = windows[windowIndex] || forecast?.daily?.[dayIndex] || forecast?.best;

  async function load(nextSpot = spot) {
    setLoading(true);
    const data = await fetchForecastBundle(nextSpot);
    setForecast(data);
    setDayIndex(0);
    setWindowIndex(0);
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => {
    load(spot);
  }, [spotId]);

  function onRefresh() {
    setRefreshing(true);
    load(spot);
  }

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" />
      <ScrollView
        style={styles.screen}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#147f8f" />}
      >
        <ImageBackground source={heroImage} style={styles.hero} imageStyle={styles.heroImage}>
          <View style={styles.heroOverlay}>
            <View style={styles.topRow}>
              <View style={styles.brandRow}>
                <Text style={styles.brand}>{t.brand}</Text>
                <View style={styles.compass} />
              </View>
              <View style={styles.switcher}>
                {["nl", "en"].map((item) => (
                  <TouchableOpacity key={item} onPress={() => setLang(item)} style={[styles.langButton, lang === item && styles.langActive]}>
                    <Text style={[styles.langText, lang === item && styles.langTextActive]}>{item.toUpperCase()}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <Text style={styles.eyebrow}>{t.eyebrow}</Text>
            <Text style={styles.title}>{lang === "nl" ? "Wanneer is het de moeite?" : "When is it worth paddling out?"}</Text>
            <Text style={styles.intro}>{t.intro}</Text>
          </View>
        </ImageBackground>

        <View style={styles.content}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.spotRail}>
            {surfSpots.map((item) => (
              <TouchableOpacity
                key={item.id}
                onPress={() => setSpotId(item.id)}
                style={[styles.spotChip, item.id === spotId && styles.spotChipActive]}
              >
                <Text style={[styles.spotName, item.id === spotId && styles.spotTextActive]}>{item.name}</Text>
                <Text style={[styles.spotRegion, item.id === spotId && styles.spotSubActive]}>{item.region}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {loading || !selected ? (
            <View style={styles.loadingCard}>
              <ActivityIndicator color="#147f8f" />
              <Text style={styles.loadingText}>Forecast laden...</Text>
            </View>
          ) : (
            <>
              <View style={styles.mainCard}>
                <ImageBackground source={boardImage} style={styles.boardArt} imageStyle={styles.boardImage}>
                  <View style={styles.boardShade} />
                </ImageBackground>
                <View style={styles.cardHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.status}>{forecast.status === "live" ? t.live : t.fallback}</Text>
                    <Text style={styles.location}>{forecast.spot.name}</Text>
                    <Text style={styles.description}>{forecast.spot.description}</Text>
                  </View>
                  <View style={[styles.scoreBubble, scoreTone(selected.score)]}>
                    <Text style={styles.scoreText}>{selected.score}</Text>
                    <Text style={styles.scoreLabel}>score</Text>
                  </View>
                </View>
                <Text style={styles.vibe}>{local(selected.vibe, lang)}</Text>
                <Text style={styles.vibeText}>{lang === "nl" ? selected.vibe.tone_nl : selected.vibe.tone_en}</Text>
              </View>

              <View style={styles.modeRow}>
                <Text style={styles.sectionTitle}>{t.week}</Text>
                <TouchableOpacity onPress={() => setExpert((value) => !value)} style={styles.modeButton}>
                  <Text style={styles.modeText}>{expert ? t.expert : t.beginner}</Text>
                </TouchableOpacity>
              </View>

              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.dayRail}>
                {forecast.daily.map((day, index) => (
                  <TouchableOpacity
                    key={`${day.date}-${index}`}
                    onPress={() => {
                      setDayIndex(index);
                      setWindowIndex(0);
                    }}
                    style={[styles.dayCard, index === dayIndex && { borderColor: scoreBorder(day.score), borderWidth: 2 }]}
                  >
                    <View style={styles.smallTop}>
                      <Text style={styles.dayLabel}>{local(day.dayLabel, lang)}</Text>
                      <View style={[styles.smallScore, scoreTone(day.score)]}>
                        <Text style={styles.smallScoreText}>{day.score}</Text>
                      </View>
                    </View>
                    <Text style={styles.date}>{day.shortDate}</Text>
                    <Text style={styles.dayMeta}>{local(day.vibe, lang)}</Text>
                    <Text style={styles.dayMeta}>{day.swell.heightM} m · {day.wind.speedKt} kt</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              <Text style={styles.sectionTitle}>{t.moments}</Text>
              <View style={styles.windowGrid}>
                {windows.map((item, index) => (
                  <TouchableOpacity
                    key={`${item.hour}-${index}`}
                    onPress={() => setWindowIndex(index)}
                    style={[styles.windowCard, index === windowIndex && { borderColor: scoreBorder(item.score), borderWidth: 2 }]}
                  >
                    <View style={styles.smallTop}>
                      <Text style={styles.windowHour}>{item.hour}</Text>
                      <View style={[styles.smallScore, scoreTone(item.score)]}>
                        <Text style={styles.smallScoreText}>{item.score}</Text>
                      </View>
                    </View>
                    <Text style={styles.windowVibe}>{local(item.vibe, lang)}</Text>
                    <Text style={styles.dayMeta}>{item.swell.heightM} m · {item.swell.periodS}s · {item.wind.speedKt} kt</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <View style={styles.metricGrid}>
                <Metric label={t.wind} value={`${selected.wind.speedKt} kt ${selected.wind.direction}`} sub={`${t.gusts}: ${selected.wind.gustKt} kt`} />
                <Metric label={t.swell} value={`${selected.swell.heightM} m ${selected.swell.direction}`} sub={`${t.period}: ${selected.swell.periodS}s`} />
                <Metric label={t.energy} value={`${selected.swell.energyKwm} kW/m`} sub={local(selected.swell.energyLabel, lang)} highlighted />
                <Metric label={t.temp} value={`${selected.weather.airTempC}°C`} sub={`${t.sea}: ${selected.weather.seaTempC}°C`} />
              </View>

              {expert && (
                <View style={styles.expertCard}>
                  <Text style={styles.sectionTitle}>{t.expert}</Text>
                  <Text style={styles.expertLine}>{t.waves}: {selected.waves.heightM} m · {selected.waves.periodS}s · {selected.waves.direction}</Text>
                  <Text style={styles.expertLine}>{t.tide}: {selected.weather.tideM} m</Text>
                  <Text style={styles.expertLine}>{t.gusts}: {selected.wind.gustKmh} km/h</Text>
                  <Text style={styles.expertLine}>Wind score: {selected.breakdown.wind_score} · Swell score: {selected.breakdown.swell_height_score}</Text>
                </View>
              )}

              <Text style={styles.source}>{t.source}</Text>
            </>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#f5efe3",
  },
  screen: {
    flex: 1,
    backgroundColor: "#f5efe3",
  },
  hero: {
    minHeight: 360,
  },
  heroImage: {
    resizeMode: "cover",
  },
  heroOverlay: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 22,
    paddingBottom: 46,
    backgroundColor: "rgba(5, 21, 29, 0.42)",
    justifyContent: "space-between",
  },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  brand: {
    color: "#fffaf0",
    fontSize: 28,
    fontWeight: "900",
  },
  compass: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: "rgba(255,255,255,.86)",
  },
  switcher: {
    flexDirection: "row",
    padding: 3,
    borderRadius: 999,
    backgroundColor: "rgba(20,37,44,.48)",
  },
  langButton: {
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 999,
  },
  langActive: {
    backgroundColor: "#fffaf0",
  },
  langText: {
    color: "#fffaf0",
    fontWeight: "800",
  },
  langTextActive: {
    color: "#14252c",
  },
  eyebrow: {
    color: "#ffdca0",
    fontSize: 12,
    fontWeight: "900",
    textTransform: "uppercase",
  },
  title: {
    color: "#fffaf0",
    fontSize: 43,
    lineHeight: 46,
    fontWeight: "900",
    letterSpacing: -1,
    maxWidth: 340,
  },
  intro: {
    color: "rgba(255,255,255,.88)",
    fontSize: 16,
    lineHeight: 24,
    maxWidth: 330,
  },
  content: {
    marginTop: -28,
    paddingBottom: 36,
  },
  spotRail: {
    paddingHorizontal: 16,
    gap: 10,
  },
  spotChip: {
    width: 164,
    padding: 13,
    borderRadius: 22,
    backgroundColor: "rgba(255,250,240,.94)",
    borderWidth: 1,
    borderColor: "rgba(20,37,44,.1)",
  },
  spotChipActive: {
    backgroundColor: "#14252c",
  },
  spotName: {
    color: "#14252c",
    fontSize: 15,
    fontWeight: "900",
  },
  spotRegion: {
    marginTop: 4,
    color: "#66777c",
    fontSize: 12,
  },
  spotTextActive: {
    color: "#fffaf0",
  },
  spotSubActive: {
    color: "rgba(255,250,240,.72)",
  },
  loadingCard: {
    margin: 16,
    padding: 26,
    borderRadius: 28,
    backgroundColor: "#fffaf0",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 12,
    color: "#66777c",
  },
  mainCard: {
    margin: 16,
    padding: 18,
    borderRadius: 30,
    backgroundColor: "#fffaf0",
    shadowColor: "#112c34",
    shadowOpacity: 0.16,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 10 },
    elevation: 5,
    overflow: "hidden",
  },
  boardArt: {
    position: "absolute",
    right: -48,
    top: 0,
    width: 180,
    height: 180,
    opacity: 0.22,
  },
  boardImage: {
    resizeMode: "cover",
  },
  boardShade: {
    flex: 1,
    backgroundColor: "rgba(255,250,240,.14)",
  },
  cardHeader: {
    flexDirection: "row",
    gap: 14,
    alignItems: "flex-start",
  },
  status: {
    color: "#ef7858",
    fontSize: 12,
    fontWeight: "900",
    textTransform: "uppercase",
  },
  location: {
    marginTop: 4,
    color: "#14252c",
    fontSize: 34,
    lineHeight: 36,
    fontWeight: "900",
  },
  description: {
    marginTop: 8,
    color: "#66777c",
    fontSize: 14,
    lineHeight: 20,
  },
  scoreBubble: {
    width: 82,
    height: 82,
    borderRadius: 41,
    alignItems: "center",
    justifyContent: "center",
  },
  scoreExcellent: {
    backgroundColor: "#11633f",
  },
  scoreGood: {
    backgroundColor: "#38a96f",
  },
  scoreOkay: {
    backgroundColor: "#eda63a",
  },
  scoreBad: {
    backgroundColor: "#d84f42",
  },
  scoreText: {
    color: "white",
    fontSize: 30,
    lineHeight: 31,
    fontWeight: "900",
  },
  scoreLabel: {
    color: "rgba(255,255,255,.78)",
    fontSize: 11,
    fontWeight: "800",
  },
  vibe: {
    marginTop: 18,
    color: "#14252c",
    fontSize: 26,
    lineHeight: 29,
    fontWeight: "900",
  },
  vibeText: {
    marginTop: 7,
    color: "#66777c",
    fontSize: 15,
    lineHeight: 22,
  },
  modeRow: {
    marginHorizontal: 16,
    marginTop: 4,
    marginBottom: 10,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  sectionTitle: {
    color: "#14252c",
    fontSize: 19,
    fontWeight: "900",
  },
  modeButton: {
    paddingHorizontal: 13,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: "#147f8f",
  },
  modeText: {
    color: "white",
    fontWeight: "900",
  },
  dayRail: {
    paddingHorizontal: 16,
    gap: 10,
    paddingBottom: 12,
  },
  dayCard: {
    width: 126,
    minHeight: 132,
    padding: 12,
    borderRadius: 22,
    backgroundColor: "rgba(255,250,240,.94)",
    borderWidth: 1,
    borderColor: "rgba(20,37,44,.1)",
  },
  smallTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  dayLabel: {
    flex: 1,
    color: "#14252c",
    fontSize: 14,
    fontWeight: "900",
  },
  smallScore: {
    minWidth: 35,
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 999,
    alignItems: "center",
  },
  smallScoreText: {
    color: "white",
    fontSize: 12,
    fontWeight: "900",
  },
  date: {
    marginTop: 8,
    color: "#66777c",
    fontSize: 12,
  },
  dayMeta: {
    marginTop: 7,
    color: "#66777c",
    fontSize: 12,
    lineHeight: 17,
  },
  windowGrid: {
    paddingHorizontal: 16,
    marginTop: 10,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  windowCard: {
    width: "48.5%",
    minHeight: 126,
    padding: 13,
    borderRadius: 22,
    backgroundColor: "rgba(255,250,240,.94)",
    borderWidth: 1,
    borderColor: "rgba(20,37,44,.1)",
  },
  windowHour: {
    color: "#14252c",
    fontSize: 15,
    fontWeight: "900",
  },
  windowVibe: {
    marginTop: 10,
    color: "#14252c",
    fontSize: 16,
    lineHeight: 19,
    fontWeight: "900",
  },
  metricGrid: {
    marginTop: 16,
    paddingHorizontal: 16,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  metric: {
    width: "48.5%",
    padding: 15,
    borderRadius: 22,
    backgroundColor: "rgba(255,250,240,.94)",
    borderWidth: 1,
    borderColor: "rgba(20,37,44,.1)",
  },
  metricHighlighted: {
    backgroundColor: "rgba(247,191,85,.22)",
  },
  metricLabel: {
    color: "#66777c",
    fontSize: 12,
    fontWeight: "800",
  },
  metricValue: {
    marginTop: 7,
    color: "#14252c",
    fontSize: 20,
    fontWeight: "900",
  },
  metricSub: {
    marginTop: 6,
    color: "#66777c",
    fontSize: 12,
    lineHeight: 17,
  },
  expertCard: {
    margin: 16,
    padding: 18,
    borderRadius: 24,
    backgroundColor: "rgba(20,37,44,.06)",
  },
  expertLine: {
    marginTop: 9,
    color: "#44575c",
    fontSize: 14,
    lineHeight: 20,
  },
  source: {
    marginHorizontal: 18,
    marginTop: 4,
    color: "#66777c",
    fontSize: 12,
    lineHeight: 18,
    textAlign: "center",
  },
});
