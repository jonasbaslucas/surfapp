# surf_spots.py


SURF_SPOTS = {
    "1": {
        "name": "Noorderstrand Scheveningen",

        # -------------------------
        # WIND
        # -------------------------

        # Offshore / best
        "excellent_wind": ["E", "SE"],

        # Cross-offshore / generally good
        "good_wind": ["NE", "S"],

        # Cross-shore / usable
        "okay_wind": ["SW", "WSW"],

        # Onshore / generally poor
        "bad_wind": ["W", "NW", "N"],


        # -------------------------
        # SWELL
        # -------------------------

        # Best swell directions
        "excellent_swell": ["NW", "NNW", "N"],

        # Still workable
        "good_swell": ["W", "WNW", "NNE", "SW"],

        # Generally poor for this spot
        "bad_swell": ["S", "SSE", "SE", "E", "ENE", "NE"],


        # -------------------------
        # WAVE SIZE
        # -------------------------

        # Below this, conditions are usually too small
        "minimum_swell_height": 0.3,

        # Around this size we start getting proper surf
        "good_swell_height": 0.8,

        # Above this is plenty of wave energy
        "excellent_swell_height": 1.2,


        # -------------------------
        # PERIOD
        # -------------------------

        # Below this = usually poor
        "minimum_period": 6,

        # Decent surf
        "good_period": 9,

        # Excellent groundswell period
        "excellent_period": 12,
    }
}