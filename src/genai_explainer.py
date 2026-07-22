"""
genai_explainer.py
-------------------
Turns the ML crop prediction + rule-based fertilizer recommendation into a
plain-language explanation a farmer can act on, in the language of their
choice. Uses the Anthropic API if a key is supplied; otherwise falls back to
a clear, deterministic template so the app still works with zero API cost.
"""

import os
import streamlit as st
from google import genai


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
print("\nAvailable Models:\n")

for model in client.models.list():
    print(model.name)
def _template_explanation(crop_result: dict, fert_result: dict, language: str = "English") -> str:
    """Deterministic, no-API-key-needed fallback explanation."""
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


def generate_explanation(crop_result: dict, fert_result: dict, api_key: str = None, language: str = "English") -> str:
    """
    crop_result: {"top_prediction": str, "confidence": float, "top_5": [(crop, prob), ...]}
    fert_result: output of fertilizer_logic.get_fertilizer_recommendation()
    api_key: Anthropic API key (optional). If not supplied, falls back to template.
    language: target language for the explanation, e.g. "Hindi", "Spanish".
    """
    # Gemini client is already initialized above.
    # We will always try Gemini first.
    
    try:
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
Do not use bullet points with technical jargon like 'z-score' or 'std dev'. Be practical."""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        raise e