"""
Premium input forms for the Crop Recommendation and Fertilizer
Recommendation pages. These components only collect input values —
they never call ML/Gemini logic directly. app.py wires the returned
values into the existing backend functions.
"""

import streamlit as st

LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Marathi", "Bengali", "Kannada", "Punjabi"]

SOIL_TYPES = ["Loamy", "Sandy", "Clayey", "Black", "Red", "Alluvial"]

# Fallback crop list used only for the Fertilizer form's crop selector
# when a crop prediction hasn't been run yet. Must match crops the
# backend actually has a nutrient profile for (derived from the same
# 22-crop crop_recommendation.csv the ML model was trained on) --
# previously this list included 8 crops (Wheat, Sugarcane, Millet,
# Groundnut, Soybean, Barley, Mustard, Potato) with no backend profile
# at all, which crashed get_fertilizer_recommendation() with an
# unhandled ValueError the moment one was selected.
DEFAULT_CROPS = [
    "Rice", "Maize", "Chickpea", "Cotton", "Jute", "Coffee",
    "Coconut", "Papaya", "Orange", "Apple", "Muskmelon", "Watermelon",
]


def render_crop_form():
    """Renders the crop-recommendation input form inside a glass card.

    Returns a dict of inputs when the user submits, otherwise None.
    """
    with st.form("crop_prediction_form", clear_on_submit=False):

        st.markdown(
            '<div class="section-title" style="font-size:1.35rem;">🌱 Enter Your Farm Details</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-sub">Fill in your soil &amp; climate readings for an instant recommendation</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.markdown('<div class="form-group-label">🧪 Nitrogen (N)</div>', unsafe_allow_html=True)
            nitrogen = st.slider("kg/ha", 0, 140, 60, key="crop_n", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">🌡️ Temperature</div>', unsafe_allow_html=True)
            temperature = st.slider("°C", 0.0, 50.0, 25.0, key="crop_temp", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">⚗️ Soil pH</div>', unsafe_allow_html=True)
            ph = st.slider("pH", 0.0, 14.0, 6.5, key="crop_ph", label_visibility="collapsed")

        with col2:
            st.markdown('<div class="form-group-label">🧪 Phosphorus (P)</div>', unsafe_allow_html=True)
            phosphorus = st.slider("kg/ha", 0, 140, 45, key="crop_p", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">💧 Humidity</div>', unsafe_allow_html=True)
            humidity = st.slider("%", 0.0, 100.0, 65.0, key="crop_hum", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">🌧️ Rainfall</div>', unsafe_allow_html=True)
            rainfall = st.slider("mm", 0.0, 300.0, 120.0, key="crop_rain", label_visibility="collapsed")

        with col3:
            st.markdown('<div class="form-group-label">🧪 Potassium (K)</div>', unsafe_allow_html=True)
            potassium = st.slider("kg/ha", 0, 140, 45, key="crop_k", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">📏 Farm Size</div>', unsafe_allow_html=True)
            farm_size = st.number_input("acres", min_value=0.1, max_value=1000.0, value=2.0, step=0.5, key="crop_farm_size", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">🌐 Language for AI Explanation</div>', unsafe_allow_html=True)
            language = st.selectbox("Language", LANGUAGES, key="crop_language", label_visibility="collapsed")

        st.markdown('<div class="predict-btn-wrap">', unsafe_allow_html=True)
        submitted = st.form_submit_button("🔍  Get Crop Recommendation", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        return {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph,
            "rainfall": rainfall,
            "farm_size": farm_size,
            "language": language,
        }
    return None


def render_fertilizer_form():
    """Renders the fertilizer-recommendation input form inside a glass card.

    Returns a dict of inputs when the user submits, otherwise None.
    """
    crop_options = list(DEFAULT_CROPS)
    crop_result = st.session_state.get("crop_result") or {}
    crop_inputs = st.session_state.get("crop_inputs", {})
    predicted_crop = crop_result.get("crop")
    if predicted_crop and predicted_crop not in crop_options:
        crop_options = [predicted_crop] + crop_options
    default_index = crop_options.index(predicted_crop) if predicted_crop in crop_options else 0

    with st.form("fertilizer_prediction_form", clear_on_submit=False):
        st.markdown(
            '<div class="section-title" style="font-size:1.35rem;">🧪 Enter Crop &amp; Soil Details</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-sub">We\'ll match the right fertilizer and dosage for your field</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.markdown('<div class="form-group-label">🌾 Crop</div>', unsafe_allow_html=True)
            crop = st.selectbox("Crop", crop_options, index=default_index, key="fert_crop", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">🧪 Nitrogen (N)</div>', unsafe_allow_html=True)
            nitrogen = st.slider(
                "kg/ha",
                0,
                140,
                crop_inputs.get("nitrogen", 60),
                key="fert_n",
                label_visibility="collapsed"
            )

            st.markdown('<div class="form-group-label">📏 Farm Size (acres)</div>', unsafe_allow_html=True)
            farm_size = st.number_input(
                "Farm Size",
                min_value=0.1,
                max_value=1000.0,
                value=crop_inputs.get("farm_size", 2.0),
                step=0.5,
                key="fert_farm_size",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown('<div class="form-group-label">🪨 Soil Type</div>', unsafe_allow_html=True)
            soil_type = st.selectbox("Soil Type", SOIL_TYPES, key="fert_soil", label_visibility="collapsed")

            st.markdown('<div class="form-group-label">🧪 Phosphorus (P)</div>', unsafe_allow_html=True)
            phosphorus = st.slider("kg/ha", 0, 140, crop_inputs.get("phosphorus", 45), key="fert_p", label_visibility="collapsed")

        with col3:
            st.markdown('<div class="form-group-label">🌐 Language for AI Explanation</div>', unsafe_allow_html=True)
            default_language = crop_inputs.get("language", "English")

            language = st.selectbox(
                "Language",
                LANGUAGES,
                index=LANGUAGES.index(default_language) if default_language in LANGUAGES else 0,
                key="fert_language",
                label_visibility="collapsed"
            )

            st.markdown('<div class="form-group-label">🧪 Potassium (K)</div>', unsafe_allow_html=True)
            potassium = st.slider(
                "kg/ha",
                0,
                140,
                crop_inputs.get("potassium", 45),
                key="fert_k",
                label_visibility="collapsed"
            )

        st.markdown('<div class="predict-btn-wrap">', unsafe_allow_html=True)
        submitted = st.form_submit_button("🔍  Get Fertilizer Recommendation", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        return {
            "crop": crop,
            "soil_type": soil_type,
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "farm_size": farm_size,
            "language": language,
        }
