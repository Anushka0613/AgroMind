"""
app.py
-------
Streamlit front-end for the AI Crop & Fertilizer Recommendation System.

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
MODEL_DIR = BASE_DIR / "models"
sys.path.append(str(SRC_DIR))

from fertilizer_logic import get_fertilizer_recommendation, load_profiles
from genai_explainer import generate_explanation

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

st.set_page_config(page_title="AI Crop & Fertilizer Advisor", page_icon="🌾", layout="wide")


@st.cache_resource
def load_artifacts():
    model = joblib.load(MODEL_DIR / "crop_model.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    profiles = load_profiles()
    return model, label_encoder, profiles


model, label_encoder, profiles = load_artifacts()

st.title("🌾 AI-Powered Crop & Fertilizer Recommendation System")
st.caption(
    "Enter your soil test values and local climate data to get a crop recommendation, "
    "a fertilizer plan, and a plain-language explanation."
)

with st.sidebar:
    st.header("Soil & Climate Inputs")
    N = st.slider("Nitrogen - N (kg/ha)", 0, 140, 60)
    P = st.slider("Phosphorus - P (kg/ha)", 5, 145, 50)
    K = st.slider("Potassium - K (kg/ha)", 5, 205, 45)
    temperature = st.slider("Temperature (°C)", 8.0, 44.0, 25.0)
    humidity = st.slider("Relative Humidity (%)", 14.0, 100.0, 70.0)
    ph = st.slider("Soil pH", 3.5, 10.0, 6.5)
    rainfall = st.slider("Rainfall (mm)", 20.0, 300.0, 100.0)

    st.divider()
    st.header("Farm Information")

    farm_size = st.number_input(
        "Farm Size",
        min_value=0.1,
        value=1.0,
        step=0.1
    )

    unit = st.selectbox(
        "Unit",
        ["acre", "hectare"]
    )
    st.divider()
    st.header("GenAI Explanation (optional)")
    api_key = st.text_input("Anthropic API key", type="password", help="Leave blank to use the free template explanation instead.")
    language = st.selectbox("Explanation language", ["English", "Hindi", "Spanish", "French", "Punjabi", "Marathi"])
    run_btn = st.button("🔍 Get Recommendation", type="primary", use_container_width=True)

if run_btn:
    input_df = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], columns=FEATURES)

    probs = model.predict_proba(input_df)[0]
    top_idx = np.argsort(probs)[::-1][:5]
    top_crops = label_encoder.inverse_transform(top_idx)
    top_probs = probs[top_idx] * 100

    top_prediction = top_crops[0]
    confidence = top_probs[0]

    crop_result = {
        "top_prediction": top_prediction,
        "confidence": confidence,
        "top_5": list(zip(top_crops.tolist(), [round(p, 1) for p in top_probs.tolist()])),
    }

    try:
        fert_result = get_fertilizer_recommendation(
            crop=top_prediction,
            N=N,
            P=P,
            K=K,
            ph=ph,
            farm_size=farm_size,
            unit=unit,
            profiles=profiles
            )
        st.success("Fertilizer recommendation generated successfully!")
    except ValueError as e:
        st.error(str(e))
        st.stop()
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🌱 Recommended Crop")
        st.metric(label="Top recommendation", value=top_prediction.capitalize(), delta=f"{confidence:.1f}% confidence")

        st.write("**Other viable options:**")
        chart_df = pd.DataFrame({"Crop": top_crops, "Confidence (%)": top_probs}).set_index("Crop")
        st.bar_chart(chart_df)

    with col2:
        st.subheader("🧪 Fertilizer Plan")
        status_df = pd.DataFrame({
            "Nutrient": ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Soil pH"],
            "Your Soil": [fert_result["input"]["N"], fert_result["input"]["P"], fert_result["input"]["K"], fert_result["input"]["ph"]],
            "Ideal for Crop": [fert_result["ideal"]["N"], fert_result["ideal"]["P"], fert_result["ideal"]["K"], fert_result["ideal"]["ph"]],
            "Status": [fert_result["status"]["N"].upper(), fert_result["status"]["P"].upper(), fert_result["status"]["K"].upper(), fert_result["status"]["ph"].upper()],
        })
        st.dataframe(status_df, hide_index=True, use_container_width=True)

        st.write("**Recommended action(s):**")

        for rec in fert_result["recommendations"]:
            st.markdown(f"- **{rec['name']}** — {rec['note']}")

    # Show dosage if available
            if "dosage" in rec:
                d = rec["dosage"]

                st.info(
                f"""
            📦 **Dosage Recommendation**

            • Recommended dose: **{d['dosage_per_unit']} kg/{d['unit']}**

            • Standard recommendation: **{d['dosage_per_hectare']} kg/hectare**

            • Total fertilizer required: **{d['total_required']} kg**
            """
                )    

        if fert_result.get("ph_note"):
            st.info(fert_result["ph_note"])

    st.divider()
    st.subheader("💬 Farmer-Friendly Explanation")
    with st.spinner("Generating explanation..."):
        explanation = generate_explanation(crop_result, fert_result, api_key=api_key, language=language)
    st.write(explanation)

else:
    st.info("Set your soil and climate values in the sidebar, then click **Get Recommendation**.")
    st.subheader("How this works")
    st.markdown("""
    1. **Crop model** — a Random Forest trained on 2,200 soil/climate samples across 22 crops predicts the best-fit crop(s) for your conditions.
    2. **Fertilizer advisor** — a rule-based engine compares your soil's N, P, K and pH against the ideal profile for the recommended crop (derived from the same training data) and flags deficiencies or excesses.
    3. **GenAI layer** — an LLM (or a built-in template if no API key is given) turns the numbers into a short, practical explanation in your preferred language.
    """)
