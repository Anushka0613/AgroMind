"""
crop_model.py
--------------
Integration adapter between the new Streamlit UI and the EXISTING trained
crop-recommendation model in AgroMind/models/ (crop_model.pkl,
label_encoder.pkl).

No ML logic lives here. This loads the same artifacts and runs the same
predict_proba() call that src/app.py (the original UI) already used, and
reshapes the output into the dict shape components/result_card.py expects.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

UI_DIR = Path(__file__).resolve().parent
BASE_DIR = UI_DIR.parent
MODEL_DIR = BASE_DIR / "models"

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Real min/max observed in the actual training dataset
# (data/crop_recommendation.csv, 2200 rows). The model itself will still
# accept any numeric input -- it's a classifier, it always returns *some*
# crop -- but a prediction on values far outside this range is
# meaningless extrapolation, not a real recommendation. This is used to
# gate obviously out-of-distribution inputs (e.g. all sliders at their
# absolute min/max) before they ever reach predict_proba(), rather than
# silently returning an unreliable answer. The model is unchanged.
REALISTIC_RANGES = {
    "N": (0, 140),
    "P": (5, 145),
    "K": (5, 205),
    "temperature": (8.8, 43.7),
    "humidity": (14.0, 100.0),
    "ph": (3.5, 9.9),
    "rainfall": (20.0, 298.6),
}

FIELD_LABELS = {
    "N": "Nitrogen (N)",
    "P": "Phosphorus (P)",
    "K": "Potassium (K)",
    "temperature": "Temperature",
    "humidity": "Humidity",
    "ph": "Soil pH",
    "rainfall": "Rainfall",
}


def validate_crop_inputs(N, P, K, temperature, humidity, ph, rainfall):
    """
    Checks each input against the range the model was actually trained
    on. Returns a list of human-readable warning strings -- empty if
    every input falls within that range.
    """
    values = {"N": N, "P": P, "K": K, "temperature": temperature,
              "humidity": humidity, "ph": ph, "rainfall": rainfall}
    warnings = []
    for key, value in values.items():
        lo, hi = REALISTIC_RANGES[key]
        if value < lo or value > hi:
            warnings.append(
                f"{FIELD_LABELS[key]} = {value} is outside the range the model "
                f"was trained on ({lo}–{hi})."
            )
    return warnings


@st.cache_resource(show_spinner="Loading AgroMind's crop model...")
def _load_artifacts():
    model = joblib.load(MODEL_DIR / "crop_model.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    return model, label_encoder


def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Runs the existing trained crop_model.pkl (same artifacts and logic as
    the original src/app.py) and reshapes the output for
    result_card.render_crop_result().

    Returns:
        {
            "crop": str,
            "confidence": float (0-100),
            "top3": [(crop_name, probability_pct), ...]   # top 5, kept as top3 key for UI compatibility
        }

    Note: the trained model + label encoder only produce a crop name and a
    confidence distribution. They do not produce a natural-language
    "why this crop" blurb or "growing tips" — that's what the existing
    Gemini explainer (genai_explainer.py) is for, which app.py already
    calls and renders separately via render_ai_explanation(). So this
    adapter intentionally leaves "recommendation" and "tips" unset rather
    than inventing placeholder text; result_card.py already handles their
    absence gracefully (those sections just don't render).
    """
    model, label_encoder = _load_artifacts()

    input_df = pd.DataFrame(
        [[N, P, K, temperature, humidity, ph, rainfall]], columns=FEATURES
    )

    probs = model.predict_proba(input_df)[0]
    top_idx = np.argsort(probs)[::-1][:5]
    top_crops = label_encoder.inverse_transform(top_idx)
    top_probs = probs[top_idx] * 100

    top_prediction = str(top_crops[0])
    confidence = float(top_probs[0])

    return {
        "crop": top_prediction.capitalize(),
        "confidence": confidence,
        "top3": [
            (str(crop).capitalize(), round(float(p), 1))
            for crop, p in zip(top_crops.tolist(), top_probs.tolist())
        ],
    }
