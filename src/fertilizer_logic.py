"""
fertilizer_logic.py
--------------------
A data-driven, rule-based fertilizer advisor.

WHY RULE-BASED INSTEAD OF A SECOND ML CLASSIFIER?
Public "fertilizer prediction" datasets (Kaggle gdabhishek/fertilizer-prediction
and similar) only cover a handful of crops and soil types (~7-8 crops, ~99-200
rows), so a classifier trained on them cannot generalize to the 22 crops our
crop-recommendation model already knows about, and it can't explain itself.

Instead we reuse the SAME crop_recommendation.csv the crop model was trained
on. For every crop it already contains the N, P, K, pH, temperature, humidity
and rainfall values that produced good outcomes for that crop -- i.e. we can
derive the "ideal nutrient profile" per crop directly from data (mean/std per
feature), then compare the farmer's actual soil test values against that
profile to flag deficiencies or excesses, and map each gap to a standard
fertilizer product. This generalizes to all 22 crops with zero extra data
collection and is fully explainable (which real-world regulators/agronomists
actually prefer over a black-box classifier).
"""

import json
from pathlib import Path
from dosage_calculator import calculate_dosage

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = BASE_DIR / "models" / "crop_nutrient_profiles.json"

# Maps a nutrient gap to a common, easily available fertilizer product.
FERTILIZER_MAP = {
    "N_low": {"name": "Urea (46-0-0)", "nutrient": "Nitrogen", "note": "Boosts leafy growth and chlorophyll production."},
    "N_high": {"name": "Reduce Nitrogen input / avoid Urea", "nutrient": "Nitrogen", "note": "Excess N can delay flowering/fruiting and increase pest susceptibility."},
    "P_low": {"name": "DAP - Di-Ammonium Phosphate (18-46-0)", "nutrient": "Phosphorus", "note": "Supports root development and flowering."},
    "P_high": {"name": "Reduce Phosphorus input", "nutrient": "Phosphorus", "note": "Excess P can lock out micronutrients like zinc and iron."},
    "K_low": {"name": "MOP - Muriate of Potash (0-0-60)", "nutrient": "Potassium", "note": "Improves fruit quality, disease resistance and water regulation."},
    "K_high": {"name": "Reduce Potassium input", "nutrient": "Potassium", "note": "Excess K can interfere with magnesium/calcium uptake."},
    "balanced": {"name": "Balanced NPK (e.g. 19-19-19)", "nutrient": "N-P-K", "note": "Soil nutrients are already close to ideal — use a maintenance dose."},
}


def load_profiles() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


def _flag(value: float, mean: float, std: float, tolerance: float = 0.5):
    """
    Returns 'low', 'high' or 'ok' depending on how far `value` is from the
    crop's ideal `mean`, scaled by the crop's own standard deviation `std`.
    tolerance is expressed in units of std-dev (0.5 std by default).
    """
    std = std if std > 1e-6 else 1e-6
    z = (value - mean) / std
    if z < -tolerance:
        return "low"
    elif z > tolerance:
        return "high"
    return "ok"

def get_fertilizer_recommendation(
    crop: str,
    N: float,
    P: float,
    K: float,
    ph: float,
    farm_size: float,
    unit: str = "acre",
    profiles: dict = None
) -> dict:

    """
    Compares the farmer's soil test values (N, P, K, ph) against the ideal
    profile for `crop` (derived from the training data) and returns a
    structured recommendation: which nutrients are deficient/excess, the
    specific fertilizer to use, and a soil-pH note.
    """
    if profiles is None:
        profiles = load_profiles()

    crop = crop.lower()
    if crop not in profiles:
        raise ValueError(f"No nutrient profile found for crop '{crop}'.")

    prof = profiles[crop]
    mean, std = prof["mean"], prof["std"]

    n_status = _flag(N, mean["N"], std["N"])
    p_status = _flag(P, mean["P"], std["P"])
    k_status = _flag(K, mean["K"], std["K"])
    ph_status = _flag(ph, mean["ph"], std["ph"], tolerance=0.75)
    
    # Calculate nutrient deficiency (used by dosage calculator)
    nutrient_gap = {
    "N": max(0, mean["N"] - N),
    "P": max(0, mean["P"] - P),
    "K": max(0, mean["K"] - K),
    }

    gaps = []

    # Nitrogen recommendation
    if n_status != "ok":
        recommendation = FERTILIZER_MAP[f"N_{n_status}"].copy()

        if n_status == "low":
            recommendation["dosage"] = calculate_dosage(
                fertilizer_name=recommendation["name"],
                nutrient_gap=nutrient_gap["N"],
                farm_size=farm_size,
                unit=unit
        )

        gaps.append(recommendation)

# Phosphorus recommendation
    if p_status != "ok":
        recommendation = FERTILIZER_MAP[f"P_{p_status}"].copy()

        if p_status == "low":
            recommendation["dosage"] = calculate_dosage(
                fertilizer_name=recommendation["name"],
                nutrient_gap=nutrient_gap["P"],
                farm_size=farm_size,
                unit=unit
            )

        gaps.append(recommendation)

# Potassium recommendation
    if k_status != "ok":
        recommendation = FERTILIZER_MAP[f"K_{k_status}"].copy()

        if k_status == "low":
            recommendation["dosage"] = calculate_dosage(
                fertilizer_name=recommendation["name"],
                nutrient_gap=nutrient_gap["K"],
                farm_size=farm_size,
                unit=unit
            )

        gaps.append(recommendation)

# Balanced soil
    if not gaps:
        recommendation = FERTILIZER_MAP["balanced"].copy()

        recommendation["dosage"] = {
            "fertilizer": recommendation["name"],
            "dosage_per_hectare": 0,
            "farm_size": farm_size,
            "unit": unit,
            "total_required": 0
}

        gaps.append(recommendation)

    ph_note = None
    if ph_status == "low":
        ph_note = f"Soil is more acidic than ideal for {crop} (ideal ~{mean['ph']}). Consider agricultural lime to raise pH."
    elif ph_status == "high":
        ph_note = f"Soil is more alkaline than ideal for {crop} (ideal ~{mean['ph']}). Consider elemental sulfur or organic compost to lower pH."

    return {
        "crop": crop,
        "input": {"N": N, "P": P, "K": K, "ph": ph},
        "ideal": {
            "N": mean["N"],
            "P": mean["P"],
            "K": mean["K"],
            "ph": mean["ph"]
        },
        "status": {
            "N": n_status,
            "P": p_status,
            "K": k_status,
            "ph": ph_status
        },
        "nutrient_gap": nutrient_gap,
        "recommendations": gaps,
        "ph_note": ph_note,
}

if __name__ == "__main__":
    profiles = load_profiles()
    # quick manual test
    
    result = get_fertilizer_recommendation(
    "rice",
    N=40,
    P=80,
    K=20,
    ph=5.0,
    farm_size=2,
    unit="acre",
    profiles=profiles
)
    import pprint
    pprint.pprint(result)
