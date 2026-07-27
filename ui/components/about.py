"""
About page component — feature highlights, tech stack, and
supported languages, presented as modern glass cards.
"""

import streamlit as st
from components.prediction_form import LANGUAGES

FEATURES = [
    ("🌱", "Smart Crop Recommendation", "Suggests the best crop for your field using soil nutrients, climate and rainfall data."),
    ("🧪", "Fertilizer Guidance", "Recommends the right fertilizer and dosage based on crop and soil type."),
    ("🤖", "AI-Powered Explanations", "Every recommendation comes with a clear, human-friendly explanation from Gemini AI."),
    ("🌐", "Multilingual Support", "Get explanations in your preferred regional language."),
    ("📊", "Confidence Scoring", "See how confident the model is in each recommendation before you act on it."),
    ("⚡", "Instant Results", "Predictions and explanations are generated in seconds, right in your browser."),
]

TECH_STACK = ["Machine Learning", "Random Forest", "Gemini AI", "Streamlit", "Python"]


def render_about():
    st.markdown('<div class="eyebrow fade-in">ABOUT AGROMIND</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title fade-in">Built for Smarter Farming</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub fade-in">AgroMind blends machine learning with generative AI to make agricultural decisions simple and data-driven.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 🌟 Features")
    cols = st.columns(3, gap="medium")
    for i, (icon, title, desc) in enumerate(FEATURES):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="about-card slide-up">
                    <span class="about-icon">{icon}</span>
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

    col_tech, col_lang = st.columns(2, gap="large")
    with col_tech:
        st.markdown("#### 🛠️ Technology Used")
        pills = "".join(f'<span class="tech-pill">{t}</span>' for t in TECH_STACK)
        st.markdown(f'<div class="glass-card">{pills}</div>', unsafe_allow_html=True)

    with col_lang:
        st.markdown("#### 🌐 Languages Supported")
        pills = "".join(f'<span class="tech-pill">{l}</span>' for l in LANGUAGES)
        st.markdown(f'<div class="glass-card">{pills}</div>', unsafe_allow_html=True)
