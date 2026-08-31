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
  return {
    ...baseNorthSeaSpot,
    ...overrides,
    id,
    name,
    latitude,
    longitude,
    region,
    description,
  };
}

export const defaultSpot = "kijkduin";

export const surfSpots = [
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
  spot("katwijk", "Katwijk", 52.2052, 4.394, "Zuid-Holland", "Nuchtere kustspot met veel strand en vaak iets minder drukte."),
  spot("wijk-aan-zee", "Wijk aan Zee", 52.4929, 4.5854, "Noord-Holland", "Rauwere Noordzee-spot bij de pier, populair als er wat meer push in zit."),
  spot("ijmuiden", "IJmuiden Noordpier", 52.461, 4.5549, "Noord-Holland", "Pier-spot met wind- en stromingsinvloed, maar vaak goede Noordzee-karakter."),
  spot("bergen-aan-zee", "Bergen aan Zee", 52.6617, 4.6283, "Noord-Holland", "Brede Noord-Hollandse beachbreak met rustige, open strandsfeer."),
  spot("texel-paal-17", "Texel Paal 17", 53.0787, 4.7438, "Waddeneilanden", "Eilandspot met open Noordzee-gevoel en vaak iets andere wind dan de Randstad."),
  spot("ameland", "Ameland", 53.451, 5.725, "Waddeneilanden", "Rustige Wadden-spot met exposed strand en veel ruimte."),
];

export function findSpot(id) {
  return surfSpots.find((item) => item.id === id) || surfSpots.find((item) => item.id === defaultSpot);
}
