"""
AgroMind — AI Powered Smart Farming Assistant
Main Streamlit entry point.

This file is intentionally kept clean: it only wires together UI
components (see /components) and calls into the EXISTING backend
prediction / Gemini functions. No ML or AI logic lives here.
"""

import os
import streamlit as st

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="AgroMind — AI Powered Smart Farming",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.sidebar import render_sidebar
from components.hero import render_hero
from components.dashboard import render_dashboard_header
from components.prediction_form import render_crop_form, render_fertilizer_form
from components.result_card import render_crop_result, render_fertilizer_result, render_ai_explanation
from components.about import render_about
from components.footer import render_footer


# =====================================================================
# BACKEND INTEGRATION — call your EXISTING functions, do not rewrite them
# =====================================================================
# Update ONLY the import lines below so they point at your real backend
# modules/functions. Everything else in this file stays the same.
#
# Expected signatures (adjust the call sites below if yours differ):
#   predict_crop(N, P, K, temperature, humidity, ph, rainfall) -> dict
#       {"crop": str, "confidence": float, "recommendation": str,
#        "top3": [(name, prob), ...], "tips": [str, ...]}
#
#   predict_fertilizer(crop, N, P, K, soil_type) -> dict
#       {"fertilizer": str, "dosage": str, "reason": str, "status": str}
#
#   get_ai_explanation(context: dict, language: str) -> str
# =====================================================================
from crop_model import predict_crop, validate_crop_inputs
from fertilizer_model import predict_fertilizer
from gemini_explainer import get_ai_explanation

predict_crop_fn = predict_crop
predict_fertilizer_fn = predict_fertilizer
get_ai_explanation_fn = get_ai_explanation


# =====================================================================
# PAGE CONFIG + CSS INJECTION
# =====================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data(show_spinner=False)
def _read_css_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def load_css(relative_path: str):
    css = _read_css_file(os.path.join(BASE_DIR, relative_path))
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css("assets/css/main.css")


# =====================================================================
# SESSION STATE DEFAULTS
# =====================================================================
for key, default in {
    "page": "Home",
    "crop_result": None,
    "fertilizer_result": None,
    "ai_explanation": None,      # "latest" explanation, for the standalone AI Explanation page
    "ai_loading": False,         # "latest" loading flag, for the standalone AI Explanation page
    "ai_explanation_crop": None,        # Crop Recommendation page's own explanation
    "ai_loading_crop": False,
    "ai_explanation_fertilizer": None,  # Fertilizer Recommendation page's own explanation
    "ai_loading_fertilizer": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# =====================================================================
# SIDEBAR NAVIGATION
# =====================================================================
current_page = render_sidebar()


# =====================================================================
# PAGE: HOME
# =====================================================================
if current_page == "Home":
    render_hero()


# =====================================================================
# PAGE: CROP RECOMMENDATION
# =====================================================================
elif current_page == "Crop Recommendation":
    render_dashboard_header(
        "Crop Recommendation",
        "Enter your soil and climate readings to get an AI-backed crop suggestion.",
    )

    form_data = render_crop_form()

    if form_data:
        validation_warnings = validate_crop_inputs(
            form_data["nitrogen"],
            form_data["phosphorus"],
            form_data["potassium"],
            form_data["temperature"],
            form_data["humidity"],
            form_data["ph"],
            form_data["rainfall"],
        )
        if validation_warnings:
            st.error(
                "These readings are too far outside realistic soil/climate "
                "conditions for a reliable recommendation:\n\n"
                + "\n".join(f"- {w}" for w in validation_warnings)
            )
        else:
            try:
                with st.spinner("Analyzing soil & climate data..."):
                    result = predict_crop_fn(
                        form_data["nitrogen"],
                        form_data["phosphorus"],
                        form_data["potassium"],
                        form_data["temperature"],
                        form_data["humidity"],
                        form_data["ph"],
                        form_data["rainfall"],
                    )
            except Exception as e:
                st.error(f"Couldn't generate a crop recommendation: {e}")
            else:
                # Save crop form inputs for reuse in Fertilizer page
                st.session_state.crop_inputs = form_data

                st.session_state.crop_result = result
                st.session_state.ai_loading_crop = True
                st.rerun()

    if st.session_state.crop_result:
        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
        render_crop_result(st.session_state.crop_result)

        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
        if st.session_state.ai_loading_crop:
            render_ai_explanation(None, loading=True)
            try:
                explanation = get_ai_explanation_fn(
                    {"type": "crop", "result": st.session_state.crop_result},
                    st.session_state.get("crop_language", "English"),
                )
            except Exception as e:
                explanation = f"⚠️ AI explanation couldn't be generated: {e}"
            st.session_state.ai_explanation_crop = explanation
            st.session_state.ai_explanation = explanation
            st.session_state.ai_loading_crop = False
            st.session_state.ai_loading = False
            st.rerun()
        else:
            render_ai_explanation(st.session_state.ai_explanation_crop)


# =====================================================================
# PAGE: FERTILIZER RECOMMENDATION
# =====================================================================
elif current_page == "Fertilizer Recommendation":
    render_dashboard_header(
        "Fertilizer Recommendation",
        "Tell us about your crop and soil type to get the right fertilizer & dosage.",
    )

    form_data = render_fertilizer_form()

    if form_data:
        try:
            with st.spinner("Matching the best fertilizer for your field..."):
                result = predict_fertilizer_fn(
                    form_data["crop"],
                    form_data["nitrogen"],
                    form_data["phosphorus"],
                    form_data["potassium"],
                    form_data["soil_type"],
                )
        except Exception as e:
            st.error(f"Couldn't generate a fertilizer recommendation: {e}")
        else:
            st.session_state.fertilizer_result = result
            st.session_state.ai_loading_fertilizer = True
            st.rerun()

    if st.session_state.fertilizer_result:
        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
        render_fertilizer_result(st.session_state.fertilizer_result)

        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
        if st.session_state.ai_loading_fertilizer:
            render_ai_explanation(None, loading=True)
            try:
                explanation = get_ai_explanation_fn(
                    {"type": "fertilizer", "result": st.session_state.fertilizer_result},
                    st.session_state.get("fert_language", "English"),
                )
            except Exception as e:
                explanation = f"⚠️ AI explanation couldn't be generated: {e}"
            st.session_state.ai_explanation_fertilizer = explanation
            st.session_state.ai_explanation = explanation
            st.session_state.ai_loading_fertilizer = False
            st.session_state.ai_loading = False
            st.rerun()
        else:
            render_ai_explanation(st.session_state.ai_explanation_fertilizer)


# =====================================================================
# PAGE: AI EXPLANATION (standalone review page)
# =====================================================================
elif current_page == "AI Explanation":
    render_dashboard_header(
        "AI Explanation",
        "A closer look at the latest AI-generated reasoning behind your recommendation.",
    )
    render_ai_explanation(st.session_state.ai_explanation, typing_effect=False)

    if not st.session_state.ai_explanation:
        st.info("Run a Crop or Fertilizer recommendation first to generate an explanation.")


# =====================================================================
# PAGE: ABOUT
# =====================================================================
elif current_page == "About":
    render_about()


# =====================================================================
# FOOTER (all pages)
# =====================================================================
render_footer()
