# surf_logic.py


def score_wind(spot, wind):
    """
    Score the wind direction from 0-30.
    """

    if wind in spot["excellent_wind"]:
        return 30, "Excellent"

    elif wind in spot["good_wind"]:
        return 24, "Good"

    elif wind in spot["okay_wind"]:
        return 15, "Okay"

    elif wind in spot["bad_wind"]:
        return 5, "Poor"

    else:
        return 0, "Unknown"


def score_swell_direction(spot, swell_direction):
    """
    Score the swell direction from 0-20.
    """

    if swell_direction in spot["excellent_swell"]:
        return 20, "Excellent"

    elif swell_direction in spot["good_swell"]:
        return 14, "Good"

    elif swell_direction in spot["bad_swell"]:
        return 4, "Poor"

    else:
        return 0, "Unknown"


def score_swell_height(spot, swell_height):
    """
    Score the swell height from 0-25.
    """

    if swell_height < spot["minimum_swell_height"]:
        return 0, "Too small"

    elif swell_height < spot["good_swell_height"]:
        return 10, "Small"

    elif swell_height < spot["excellent_swell_height"]:
        return 20, "Good"

    else:
        return 25, "Excellent"


def score_period(spot, period):
    """
    Score the swell period from 0-25.
    """

    if period < spot["minimum_period"]:
        return 0, "Too short"

    elif period < spot["good_period"]:
        return 10, "Short"

    elif period < spot["excellent_period"]:
        return 20, "Good"

    else:
        return 25, "Excellent"


def evaluate_conditions(
    spot,
    wind,
    swell_direction,
    swell_height,
    period
):
    """
    Evaluate the complete surf conditions.
    """

    wind_score, wind_quality = score_wind(spot, wind)

    swell_direction_score, swell_direction_quality = (
        score_swell_direction(spot, swell_direction)
    )

    swell_height_score, swell_height_quality = (
        score_swell_height(spot, swell_height)
    )

    period_score, period_quality = score_period(
        spot,
        period
    )

    total_score = (
        wind_score
        + swell_direction_score
        + swell_height_score
        + period_score
    )

    # --------------------------------
    # VERDICT
    # --------------------------------

    if total_score >= 80:
        verdict = "🟢 DEFINITELY GO"

    elif total_score >= 65:
        verdict = "🟢 GOOD TO SURF"

    elif total_score >= 50:
        verdict = "🟡 MAYBE"

    elif total_score >= 35:
        verdict = "🟠 POOR"

    else:
        verdict = "🔴 DON'T GO"

    return {
        "total_score": total_score,
        "wind_score": wind_score,
        "wind_quality": wind_quality,
        "swell_direction_score": swell_direction_score,
        "swell_direction_quality": swell_direction_quality,
        "swell_height_score": swell_height_score,
        "swell_height_quality": swell_height_quality,
        "period_score": period_score,
        "period_quality": period_quality,
        "verdict": verdict,
    }