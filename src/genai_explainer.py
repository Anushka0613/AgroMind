"""
genai_explainer.py
-------------------
Generates a farmer-friendly explanation for the ML crop prediction and
fertilizer recommendation using the Google Gemini API. The explanation
can be generated in the user's selected language. If the Gemini service
is temporarily unavailable, a graceful fallback message is returned.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def _template_explanation(crop_result: dict, fert_result: dict, language: str = "English") -> str:
    """Optional rule-based fallback explanation."""
    crop = fert_result["crop"].capitalize()
    top_crop = crop_result["top_prediction"]
    confidence = crop_result["confidence"]

    lines = [
        f"Recommended crop: {top_crop} (model confidence: {confidence:.1f}%).",
        "",
        f"Soil nutrient check for {crop}:",
    ]
    status = fert_result["status"]
    ideal = fert_result["ideal"]
    inp = fert_result["input"]

    label_map = {"low": "LOW", "high": "HIGH", "ok": "OK"}
    for nutrient in ["N", "P", "K"]:
        lines.append(
            f"  - {nutrient}: your soil = {inp[nutrient]}, ideal for {crop} ~ {ideal[nutrient]} -> {label_map[status[nutrient]]}"
        )

    lines.append("")
    lines.append("Recommended fertilizer action(s):")
    for rec in fert_result["recommendations"]:
        lines.append(f"  - {rec['name']}: {rec['note']}")

    if fert_result.get("ph_note"):
        lines.append("")
        lines.append(f"Soil pH note: {fert_result['ph_note']}")

    if language != "English":
        lines.append("")
        lines.append(f"(Note: translation to {language} requires an API key — showing English template.)")

    return "\n".join(lines)


def generate_explanation(crop_result: dict, fert_result: dict, language: str = "English", focus: str = "crop") -> str:
    """
    crop_result: {"top_prediction": str, "confidence": float, "top_5": [(crop, prob), ...]}
    fert_result: output of fertilizer_logic.get_fertilizer_recommendation()
    api_key: Reserved for compatibility. Gemini API key is loaded from the environment.
    language: target language for the explanation, e.g. "Hindi", "Spanish".
    focus: "crop" (default) leads with why the crop is a good fit -- unchanged
        existing behavior for all current callers. "fertilizer" leads with the
        fertilizer recommendation instead, for callers (e.g. the Fertilizer
        Recommendation page) whose explanation should be about the fertilizer
        being shown rather than the earlier crop prediction.
    """

    if focus == "fertilizer":
        prompt = f"""You are an agricultural extension officer talking to a farmer.

Soil test vs. ideal levels for their {fert_result['crop']} crop:
- Nitrogen (N): farmer's soil = {fert_result['input']['N']}, ideal = {fert_result['ideal']['N']} -> status: {fert_result['status']['N']}
- Phosphorus (P): farmer's soil = {fert_result['input']['P']}, ideal = {fert_result['ideal']['P']} -> status: {fert_result['status']['P']}
- Potassium (K): farmer's soil = {fert_result['input']['K']}, ideal = {fert_result['ideal']['K']} -> status: {fert_result['status']['K']}
- Soil pH: farmer's soil = {fert_result['input']['ph']}, ideal = {fert_result['ideal']['ph']}

Fertilizer recommendations: {fert_result['recommendations']}
pH note: {fert_result.get('ph_note')}

Write a short (120-180 word), warm, plain-language explanation in {language} for a
smallholder farmer with no technical background. Explain:
1) exactly what fertilizer(s) to apply and why,
2) what's off in their soil in simple terms,
3) how this will help their {fert_result['crop']} crop.
Do not use bullet points with technical jargon like 'z-score' or 'std dev'. Be practical.
"""
    else:
        prompt = f"""You are an agricultural extension officer talking to a farmer.

ML model output:
- Recommended crop: {crop_result['top_prediction']} (confidence {crop_result['confidence']:.1f}%)
- Other viable options: {crop_result.get('top_5', [])}

Soil test vs. ideal levels for the recommended crop:
- Nitrogen (N): farmer's soil = {fert_result['input']['N']}, ideal = {fert_result['ideal']['N']} -> status: {fert_result['status']['N']}
- Phosphorus (P): farmer's soil = {fert_result['input']['P']}, ideal = {fert_result['ideal']['P']} -> status: {fert_result['status']['P']}
- Potassium (K): farmer's soil = {fert_result['input']['K']}, ideal = {fert_result['ideal']['K']} -> status: {fert_result['status']['K']}
- Soil pH: farmer's soil = {fert_result['input']['ph']}, ideal = {fert_result['ideal']['ph']}

Fertilizer recommendations: {fert_result['recommendations']}
pH note: {fert_result.get('ph_note')}

Write a short (120-180 word), warm, plain-language explanation in {language} for a
smallholder farmer with no technical background. Explain:
1) why this crop is a good fit,
2) what's off in their soil (if anything) in simple terms,
3) exactly what fertilizer to apply and why.
Do not use bullet points with technical jargon like 'z-score' or 'std dev'. Be practical.
"""

    start_time = time.perf_counter()

    

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        elapsed = time.perf_counter() - start_time
        print(f"Gemini response time: {elapsed:.2f} seconds")

        return response.text

    except Exception as e:
        elapsed = time.perf_counter() - start_time

        print(f"Gemini failed after {elapsed:.2f} seconds")
        print(f"Actual Gemini error: {repr(e)}")

        st.error(f"Gemini Error: {type(e).__name__}: {e}")

        return (
            f"AI explanation is temporarily unavailable.\n\n"
            f"Recommended Crop: {crop_result['top_prediction']}\n\n"
            f"Your crop and fertilizer recommendations are still valid."
        )


