"""
Result-display components: the crop recommendation hero card, the
fertilizer recommendation card, and the Gemini AI explanation chat
bubble. These components only render data handed to them — all
values are expected to come straight from the existing backend
prediction functions (see app.py).
"""

import time
import streamlit as st
import plotly.graph_objects as go

CROP_EMOJI = {
    "rice": "🌾", "wheat": "🌿", "maize": "🌽", "cotton": "☁️",
    "sugarcane": "🎋", "millet": "🌱", "groundnut": "🥜", "soybean": "🫘",
    "barley": "🌾", "chickpea": "🫛", "mustard": "🌼", "potato": "🥔",
}


def _crop_emoji(crop_name: str) -> str:
    return CROP_EMOJI.get(str(crop_name).lower(), "🌾")


def render_crop_result(result: dict):
    """
    result = {
        "crop": str,
        "confidence": float (0-100),
        "recommendation": str,
        "top3": [(crop_name, probability), ...]   # optional
        "tips": [str, ...]                         # optional
    }
    """
    crop = result.get("crop", "—")
    confidence = float(result.get("confidence", 0))
    recommendation = result.get("recommendation", "")

    with st.container(key="crop_result_hero"):
        st.markdown('<div class="result-confidence-label">🎯 RECOMMENDED CROP</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-crop-name">{crop}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result-confidence-label">Confidence: {confidence:.1f}%</div>
            <div class="confidence-track">
                <div class="confidence-fill" style="width:{min(max(confidence,0),100)}%;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if recommendation:
        st.markdown(
            f"""
            <div class="glass-card slide-up-1" style="margin-top:1rem;">
                <b>🌾 Why this crop?</b><br/>
                <span style="color:var(--text-muted);">{recommendation}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    top3 = result.get("top3")

    if top3:
        with st.container(key="crop_confidence_chart_card"):
            st.markdown(
                '<div class="section-title" style="font-size:1.35rem;">📊 Crop Confidence Analysis</div>',
                unsafe_allow_html=True,
            )

            crops = [_crop_emoji(name) + "  " + name for name, _ in top3]
            scores = [float(prob) for _, prob in top3]

            # Previously a hardcoded 3-color list was sliced against however
            # many bars there actually were; with 5 crops shown (top3's real
            # length despite the name), bars 4 and 5 had no color assigned
            # and Plotly rendered them black. Generate exactly as many
            # progressively lighter green shades as there are bars instead.
            def _green_shade(i, n):
                # Interpolates from the dark theme green to the light theme
                # green across n steps, using the same palette tokens as the
                # rest of the app (--primary-dark to --primary-light).
                dark = (0x2E, 0x7D, 0x32)   # --primary-dark
                light = (0x81, 0xC7, 0x84)  # --primary-light
                t = i / max(n - 1, 1)
                rgb = tuple(int(dark[c] + (light[c] - dark[c]) * t) for c in range(3))
                return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

            colors = [_green_shade(i, len(scores)) for i in range(len(scores))]

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=scores,
                    y=crops,
                    orientation="h",

                    marker=dict(
                        color=colors,
                        line=dict(color="rgba(0,0,0,0)", width=0),
                    ),

                    text=[f"{x:.1f}%" for x in scores],
                    textposition="outside",

                    textfont=dict(
                        size=16,
                        color="#1B2E1E",
                        family="Poppins",
                    ),

                    hovertemplate="<b>%{y}</b><br>%{x:.1f}% confidence<extra></extra>",
                )
            )

            fig.update_traces(width=0.55)

            fig.update_layout(

                height=260,

                margin=dict(
                    l=20,
                    r=55,
                    t=10,
                    b=10,
                ),

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                showlegend=False,

                font=dict(
                    family="Poppins",
                    size=16,
                    color="#1B2E1E",
                ),

                xaxis=dict(
                    range=[0,100],
                    visible=False,
                    fixedrange=True,
                ),

                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(
                        family="Poppins",
                        size=18,
                        color="#1B2E1E",
                    ),
                    fixedrange=True,
                ),
            )


            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )


    tips = result.get("tips")
    if tips:
        st.markdown('<div style="margin-top:1.4rem;" class="section-title" style="font-size:1.15rem;">💡 Growing Tips</div>', unsafe_allow_html=True)
        for tip in tips:
            st.markdown(f'<div class="tip-card" style="margin-bottom:.6rem;">💡 &nbsp;{tip}</div>', unsafe_allow_html=True)


def render_fertilizer_result(result: dict):
    """
    result = {
        "fertilizer": str,
        "dosage": str,
        "reason": str,
        "status": "optimal" | "low" | "high"   # optional, for color coding
    }
    """
    fertilizer = result.get("fertilizer", "—")
    dosage = result.get("dosage", "—")
    reason = result.get("reason", "")
    status = result.get("status", "optimal")

    border_color = {
        "optimal": "var(--primary)",
        "low": "#FFB300",
        "high": "#E53935",
    }.get(status, "var(--primary)")

    st.markdown(
        f"""
        <div class="fert-card slide-up" style="border-left-color:{border_color};">
            <div class="fert-title">🧪 {fertilizer}</div>
            <span class="fert-tag">📏 Dosage: {dosage}</span>
            <p style="margin-top:.9rem; color:var(--text-muted); line-height:1.6;">{reason}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_explanation(text: str, loading: bool = False, typing_effect: bool = False):
    """
    Renders the Gemini explanation inside a styled, scrollable chat bubble.
    Pass loading=True while the backend call is in flight to show a spinner.
    Pass typing_effect=True to reveal the text progressively (best-effort,
    optional cosmetic touch — safe to skip on reruns).
    """
    with st.container(key="ai_chat_card"):
        st.markdown(
            """
            <div class="ai-chat-header">
                <div class="ai-avatar">🤖</div>
                AI Explanation &middot; Powered by Gemini
            </div>
            """,
            unsafe_allow_html=True,
        )

        if loading:
            st.markdown(
                """
                <div class="chat-bubble">
                    Thinking about your field conditions
                    <span class="typing-dots"><span></span><span></span><span></span></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif text:
            if typing_effect:
                placeholder = st.empty()
                shown = ""
                step = max(1, len(text) // 60)
                for i in range(0, len(text), step):
                    shown = text[: i + step]
                    placeholder.markdown(
                        f'<div class="chat-bubble">{shown}</div>', unsafe_allow_html=True
                    )
                    time.sleep(0.012)
                placeholder.markdown(f'<div class="chat-bubble">{text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="chat-bubble">Run a prediction to see the AI explanation here.</div>',
                unsafe_allow_html=True,
            )
