"""
fertilizer_model.py
---------------------
Integration adapter between the new Streamlit UI and the EXISTING
rule-based fertilizer advisor in AgroMind/src/fertilizer_logic.py.

No fertilizer logic lives here. This only imports and calls the existing
get_fertilizer_recommendation() (unchanged) and reshapes its (richer)
output into the {"fertilizer","dosage","reason","status"} shape that
components/result_card.py's fertilizer card expects.
"""

import sys
from pathlib import Path

import streamlit as st

UI_DIR = Path(__file__).resolve().parent
BASE_DIR = UI_DIR.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from fertilizer_logic import get_fertilizer_recommendation, load_profiles  # noqa: E402


@st.cache_resource(show_spinner="Loading crop nutrient profiles...")
def _load_profiles():
    return load_profiles()


def predict_fertilizer(crop, N, P, K, soil_type):
    """
    Calls the existing get_fertilizer_recommendation() (unchanged) and
    reshapes its output for result_card.render_fertilizer_result().

    Two inputs the fertilizer FORM doesn't collect but the backend
    requires:
      - ph: the fertilizer form has no pH field, so we reuse the pH the
        user entered on the Crop Recommendation page
        (st.session_state.crop_inputs), falling back to a neutral 6.5 if
        that page hasn't been run yet this session.
      - farm_size / unit: the fertilizer form's farm-size widget already
        stores its value in st.session_state under its own widget key
        ("fert_farm_size"), so we read it directly from there rather than
        needing app.py's call site changed. Unit is treated as "acre",
        matching the hidden label used in both forms.

    `soil_type` is collected by the UI but not used here — the backend's
    fertilizer_logic reasons purely from N/P/K/pH vs. the crop's
    data-derived ideal profile; soil_type isn't a dimension it models.
    Nothing is being dropped — it simply was never part of the existing
    rule-based engine's inputs.
    """
    profiles = _load_profiles()

    crop_inputs = st.session_state.get("crop_inputs", {})
    ph = crop_inputs.get("ph", 6.5)

    farm_size = st.session_state.get("fert_farm_size", 1.0)
    unit = "acre"

    fert_result = get_fertilizer_recommendation(
        crop=crop,
        N=N,
        P=P,
        K=K,
        ph=ph,
        farm_size=farm_size,
        unit=unit,
        profiles=profiles,
    )

    # Keep the full, detailed backend result available (per-nutrient
    # status, ideal ranges, exact dosage breakdown) in case a richer
    # fertilizer view is wanted later — nothing from the backend's real
    # output is lost, only simplified for this specific card.
    st.session_state.fertilizer_result_full = fert_result

    notes = [rec["note"] for rec in fert_result["recommendations"]]
    if fert_result.get("ph_note"):
        notes.append(fert_result["ph_note"])
    reason = " ".join(notes)

    # The backend can return MORE THAN ONE nutrient gap at once (e.g.
    # Nitrogen excess AND Potassium deficiency simultaneously). Showing
    # only recommendations[0] silently dropped every other gap, which is
    # why a real actionable product (e.g. MOP for a K deficiency) could
    # go completely unmentioned whenever a different nutrient's advisory
    # note ("Reduce Nitrogen input") happened to come first. We now
    # represent every gap the backend found, not just the first one.
    fertilizer_names = []
    dosage_parts = []
    for rec in fert_result["recommendations"]:
        fertilizer_names.append(rec["name"])

        if "dosage" not in rec:
            # A "_high" advisory-only gap (e.g. "Reduce Nitrogen input")
            # never gets a calculated dosage from the backend — there's
            # no product amount to apply, just an input reduction.
            dosage_parts.append(f"{rec['name']}: reduce application (no additional dose)")
            continue

        d = rec["dosage"]
        # The backend's "balanced/maintenance" branch builds this dict by
        # hand (dosage_per_hectare, no dosage_per_unit key, values of 0),
        # while the calculate_dosage() branch returns dosage_per_unit
        # directly — an existing shape difference inside
        # fertilizer_logic.py itself. We handle both here rather than
        # editing the backend.
        per_unit = d.get("dosage_per_unit", d.get("dosage_per_hectare", 0))
        if d.get("total_required", 0) == 0:
            dosage_parts.append(f"{rec['name']}: maintenance dose (soil already near ideal)")
        else:
            dosage_parts.append(f"{rec['name']}: {per_unit} kg/{d['unit']} ({d['total_required']} kg total)")

    fertilizer_display = " + ".join(fertilizer_names)
    dosage_display = "; ".join(dosage_parts)

    nutrient_statuses = [
        fert_result["status"]["N"],
        fert_result["status"]["P"],
        fert_result["status"]["K"],
    ]
    if "high" in nutrient_statuses:
        status = "high"
    elif "low" in nutrient_statuses:
        status = "low"
    else:
        status = "optimal"

    return {
        "fertilizer": fertilizer_display,
        "dosage": dosage_display,
        "reason": reason,
        "status": status,
    }
