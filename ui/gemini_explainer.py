"""
gemini_explainer.py
---------------------
Integration adapter between the new Streamlit UI and the EXISTING Gemini
explanation module in AgroMind/src/genai_explainer.py.

No Gemini/prompt logic lives here. This only imports and calls the
existing generate_explanation() (unchanged) and adapts the
(crop_result, fert_result, language) inputs it requires from the
simplified session-state dicts the new UI's app.py maintains.
"""

import sys
from pathlib import Path

import streamlit as st

UI_DIR = Path(__file__).resolve().parent
BASE_DIR = UI_DIR.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from genai_explainer import generate_explanation  # noqa: E402
from fertilizer_logic import get_fertilizer_recommendation  # noqa: E402
from fertilizer_model import _load_profiles  # noqa: E402 -- reuse the existing st.cache_resource-cached loader instead of re-reading crop_nutrient_profiles.json from disk on every call


def _crop_result_for_backend():
    """
    Reshapes crop_model.py's simplified {"crop","confidence","top3"} dict
    (stored in st.session_state.crop_result) into the
    {"top_prediction","confidence","top_5"} shape generate_explanation()
    expects.
    """
    ui_crop_result = st.session_state.get("crop_result") or {}
    return {
        "top_prediction": ui_crop_result.get("crop", ""),
        "confidence": ui_crop_result.get("confidence", 0.0),
        "top_5": ui_crop_result.get("top3", []),
    }


def _fert_result_for_backend():
    """
    generate_explanation() needs the FULL, rich output of
    get_fertilizer_recommendation() (status/ideal/recommendations/ph_note
    per nutrient) — not the simplified card dict fertilizer_model.py
    returns to the UI.

    - If the Fertilizer Recommendation page has already been run this
      session, fertilizer_model.py already stashed that exact real
      result in st.session_state.fertilizer_result_full — reuse it as-is
      (accurate farm size, accurate everything).
    - Otherwise (the user is on the Crop Recommendation page and hasn't
      visited Fertilizer Recommendation yet this session), we compute a
      real one right now from the same N/P/K/ph values the user just
      submitted and the same unmodified backend function — so the
      explanation is grounded in a genuine soil-vs-ideal analysis, not
      placeholder text. Farm size isn't collected on the Crop page, so a
      nominal 1 acre is used purely to satisfy the function's required
      parameter — this only affects the dosage *total_required* number
      buried inside the recommendations list passed to the prompt, not
      the nutrient status / ideal-range analysis the crop-page
      explanation is actually about.
    """
    cached = st.session_state.get("fertilizer_result_full")
    if cached:
        return cached

    crop_inputs = st.session_state.get("crop_inputs") or {}
    crop_result = st.session_state.get("crop_result") or {}
    crop = crop_result.get("crop", "")

    if not crop or not crop_inputs:
        return None

    return get_fertilizer_recommendation(
        crop=crop,
        N=crop_inputs.get("nitrogen", 0),
        P=crop_inputs.get("phosphorus", 0),
        K=crop_inputs.get("potassium", 0),
        ph=crop_inputs.get("ph", 6.5),
        farm_size=1,
        unit="acre",
        profiles=_load_profiles(),
    )


def get_ai_explanation(context: dict, language: str = "English") -> str:
    """
    Matches the get_ai_explanation(context, language) signature app.py
    already calls, where context is either:
        {"type": "crop", "result": <crop_model.py output>}
        {"type": "fertilizer", "result": <fertilizer_model.py output>}

    Calls the existing generate_explanation() (unchanged) underneath.
    """
    result_type = context.get("type")

    crop_result = _crop_result_for_backend()

    if result_type == "fertilizer":
        fert_result = st.session_state.get("fertilizer_result_full")
    else:
        fert_result = _fert_result_for_backend()

    if not fert_result or not crop_result.get("top_prediction"):
        return (
            "AI explanation needs a predicted crop and soil nutrient "
            "readings — please run the Crop Recommendation step first."
        )

    return generate_explanation(crop_result, fert_result, language, focus=result_type or "crop")
