"""
score_calculations.py
---------------------

ROI
Breakeven
Hybrid Score
Helpers
"""

# ==========================================================
# ROI
# ==========================================================


def roi_raw(gain: float, cost: float) -> float:
    """
    Returns raw ROI.

    gain per second / cost
    """

    if cost <= 0:
        return 0.0

    return gain / cost


# ==========================================================
# ROI SCALE FACTOR
# ==========================================================


def roi_scale_factor(roi_values: list[float]) -> int:
    """
    Finds a scaling factor that keeps
    ROI values readable.

    Example:

    0.000001
        ↓
    factor 100000
        ↓
    0.1
    """

    if not roi_values:
        return 1

    max_roi = max(roi_values)

    factor = 1

    while max_roi * factor < 0.01:
        factor *= 100

    return factor


# ==========================================================
# APPLY ROI FACTOR
# ==========================================================


def scaled_roi(roi_value: float, factor: int) -> float:

    return roi_value * factor


# ==========================================================
# ROI DISPLAY
# ==========================================================


def roi_percent(roi_value: float, factor: int = 1) -> float:

    return roi_value * factor * 100


# ==========================================================
# BREAKEVEN
# ==========================================================


def breakeven_seconds(cost: float, gain: float) -> float:
    """
    Cost / Gain

    Always returns seconds.

    Used for calculations.
    """

    if gain <= 0:
        return float("inf")

    return cost / gain


# ==========================================================
# BREAKEVEN DISPLAY
# ==========================================================


def format_breakeven(seconds: float) -> str:

    if seconds < 60:
        return f"{seconds:.1f} sec"

    minutes = seconds / 60

    if minutes < 60:
        return f"{minutes:.1f} min"

    hours = minutes / 60

    if hours < 24:
        return f"{hours:.1f} hr"

    days = hours / 24

    if days < 365:
        return f"{days:.1f} day"

    years = days / 365

    return f"{years:.1f} yr"


# ==========================================================
# NORMALIZE
# ==========================================================


def normalize(value: float, min_value: float, max_value: float) -> float:

    if max_value == min_value:
        return 100.0

    return ((value - min_value) / (max_value - min_value)) * 100


# ==========================================================
# ROI SCORE
# ==========================================================


def roi_score(roi_value: float, min_roi: float, max_roi: float) -> float:
    """
    Higher ROI is better.
    """

    return normalize(roi_value, min_roi, max_roi)


# ==========================================================
# BREAKEVEN SCORE
# ==========================================================


def breakeven_score(
    breakeven_value: float, min_breakeven: float, max_breakeven: float
) -> float:
    """
    Lower breakeven is better.
    """

    raw_score = normalize(breakeven_value, min_breakeven, max_breakeven)

    return 100 - raw_score


# ==========================================================
# HYBRID SCORE
# ==========================================================


def hybrid_score(roi_score_value: float, breakeven_score_value: float) -> float:
    """
    50% ROI
    50% Breakeven
    """

    return roi_score_value * 0.50 + breakeven_score_value * 0.50
