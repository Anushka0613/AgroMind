"""
Reusable card widgets: top dashboard stat cards + small tip cards.
Pure presentation components — no prediction logic lives here.
"""

import streamlit as st


def render_stat_cards():
    """
    Top statistic cards shown at the head of every dashboard page.
    Pulls latest values from session_state so cards update live
    after a prediction is made, and show a friendly placeholder before that.
    """
    crop_result = st.session_state.get("crop_result")
    fert_result = st.session_state.get("fertilizer_result")

    recommended_crop = crop_result["crop"] if crop_result else "—"
    fertilizer = fert_result["fertilizer"] if fert_result else "—"

    if crop_result:
        conf = crop_result.get("confidence", 0)
        soil_health = "Excellent" if conf >= 85 else "Good" if conf >= 60 else "Fair"
    else:
        soil_health = "—"

    ai_status = "Online ✅" if st.session_state.get("ai_explanation") else "Idle"

    stats = [
        ("🌾", "Recommended Crop", recommended_crop),
        ("🧪", "Fertilizer", fertilizer),
        ("🌍", "Soil Health", soil_health),
        ("🤖", "AI Status", ai_status),
    ]

    cols = st.columns(4, gap="medium")
    for col, (icon, label, value) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card slide-up">
                    <div class="stat-icon">{icon}</div>
                    <div>
                        <div class="stat-label">{label}</div>
                        <div class="stat-value">{value}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_tip_card(icon: str, text: str):
    st.markdown(
        f"""
        <div class="tip-card">
            <span style="font-size:1.3rem;">{icon}</span>
            <span style="margin-left:.4rem;">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
