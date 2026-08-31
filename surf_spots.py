# surf_spots.py


BASE_NORTH_SEA_SPOT = {
    "excellent_wind": ["E", "ESE", "SE", "SSE"],
    "good_wind": ["NE", "ENE", "S"],
    "okay_wind": ["NNE", "SSW", "SW"],
    "bad_wind": ["W", "WNW", "NW", "NNW", "N"],
    "excellent_swell": ["NW", "NNW", "N"],
    "good_swell": ["W", "WNW", "NNE", "SW"],
    "bad_swell": ["S", "SSE", "SE", "E", "ENE", "NE"],
    "minimum_swell_height": 0.3,
    "good_swell_height": 0.8,
    "excellent_swell_height": 1.2,
    "minimum_period": 6,
    "good_period": 9,
    "excellent_period": 12,
}


def spot(name, latitude, longitude, region, description, **overrides):
    data = {
        **BASE_NORTH_SEA_SPOT,
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "region": region,
        "description": description,
    }
    data.update(overrides)
    return data


SURF_SPOTS = {
    "scheveningen-noord": spot(
        "Scheveningen Noord",
        52.1168,
        4.2798,
        "Zuid-Holland",
        "Drukke klassieker met veel surfscholen, zandbanken en energie rond de pier.",
    ),
    "scheveningen-zuid": spot(
        "Scheveningen Zuid",
        52.0969,
        4.2518,
        "Zuid-Holland",
        "Iets rustiger dan Noord, vaak fijn voor beginners en longboarders.",
    ),
    "kijkduin": spot(
        "Kijkduin",
        52.0558,
        4.2094,
        "Zuid-Holland",
        "Mellow Haagse spot met een lokale sfeer en vaak iets meer ruimte.",
    ),
    "ter-heijde": spot(
        "Ter Heijde",
        52.0304,
        4.1686,
        "Zuid-Holland",
        "Westlandse beachbreak bij de Zandmotor, soms verrassend goede banken.",
    ),
    "hoek-van-holland": spot(
        "Hoek van Holland",
        51.9893,
        4.1072,
        "Zuid-Holland",
        "Ruime beachbreak bij de Nieuwe Waterweg met stroming en veel windinvloed.",
    ),
    "maasvlakte": spot(
        "Maasvlakte",
        51.9516,
        4.0314,
        "Zuid-Holland",
        "Exposed spot met veel ruimte en soms de meeste swell van Zuid-Holland.",
        good_swell_height=0.9,
        excellent_swell_height=1.4,
    ),
    "ouddorp": spot(
        "Ouddorp",
        51.8212,
        3.8676,
        "Zuid-Holland",
        "Brede, toegankelijke spot met veel zandbankvariatie.",
    ),
    "brouwersdam": spot(
        "Brouwersdam",
        51.7672,
        3.8495,
        "Zeeland",
        "Bekende watersportplek met wind, ruimte en makkelijk parkeren.",
    ),
    "domburg": spot(
        "Domburg",
        51.5638,
        3.4985,
        "Zeeland",
        "Een van Zeeland's bekendste surfspots, vaak wat meer zuidwestelijke energie.",
        good_swell=["W", "WNW", "SW", "WSW"],
    ),
    "vlissingen": spot(
        "Vlissingen",
        51.4538,
        3.5709,
        "Zeeland",
        "Meer getij- en windgevoelig, maar leuk wanneer Zeeland aan staat.",
        good_swell=["W", "WSW", "SW"],
    ),
    "cadzand": spot(
        "Cadzand",
        51.3789,
        3.3897,
        "Zeeland",
        "Zuidwestelijke kustspot met zandbanken en een ontspannen strandgevoel.",
        good_swell=["W", "WSW", "SW"],
    ),
    "zandvoort": spot(
        "Zandvoort",
        52.3717,
        4.5329,
        "Noord-Holland",
        "Breed strand, sterke surfscene en makkelijk bereikbaar vanuit Amsterdam.",
    ),
    "bloemendaal": spot(
        "Bloemendaal",
        52.4047,
        4.5429,
        "Noord-Holland",
        "Ruime strandbreak met relaxte sfeer en veel plek om te leren.",
    ),
    "noordwijk": spot(
        "Noordwijk",
        52.2476,
        4.4269,
        "Zuid-Holland",
        "Toegankelijke beachbreak met brede zandbodem en veel beginnersruimte.",
    ),
    "katwijk": spot(
        "Katwijk",
        52.2052,
        4.3940,
        "Zuid-Holland",
        "Nuchtere kustspot met veel strand en vaak iets minder drukte.",
    ),
    "wijk-aan-zee": spot(
        "Wijk aan Zee",
        52.4929,
        4.5854,
        "Noord-Holland",
        "Rauwere Noordzee-spot bij de pier, populair als er wat meer push in zit.",
    ),
    "ijmuiden": spot(
        "IJmuiden Noordpier",
        52.4610,
        4.5549,
        "Noord-Holland",
        "Pier-spot met wind- en stromingsinvloed, maar vaak goede Noordzee-karakter.",
    ),
    "bergen-aan-zee": spot(
        "Bergen aan Zee",
        52.6617,
        4.6283,
        "Noord-Holland",
        "Brede Noord-Hollandse beachbreak met rustige, open strandsfeer.",
    ),
    "texel-paal-17": spot(
        "Texel Paal 17",
        53.0787,
        4.7438,
        "Waddeneilanden",
        "Eilandspot met open Noordzee-gevoel en vaak iets andere wind dan de Randstad.",
    ),
    "ameland": spot(
        "Ameland",
        53.4510,
        5.7250,
        "Waddeneilanden",
        "Rustige Wadden-spot met exposed strand en veel ruimte.",
    ),
}


DEFAULT_SPOT = "kijkduin"
