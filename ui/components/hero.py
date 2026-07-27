"""
Hero / landing page component for AgroMind.
Shown on the "Home" page. Contains the big title, subtitle, CTA button
that jumps to the Crop Recommendation dashboard, a low-opacity farmer
illustration used as a background layer, and a row of floating feature
chips.
"""

import base64
from pathlib import Path

import streamlit as st


@st.cache_data(show_spinner=False)
def _hero_image_data_uri():
    """
    Base64-encodes the hero illustration once (cached) so it can be used
    as a CSS background-image via a data: URI. A plain CSS url() pointing
    at the file on disk isn't reliably resolvable from inside an injected
    <style> block, so embedding it directly avoids path issues; caching
    means the file is only read/encoded once per session, not every rerun.
    """
    image_path = Path(__file__).resolve().parent.parent / "assets" / "images" / "hero_illustration.png"
    if not image_path.exists():
        return None
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def render_hero():
    bg_uri = _hero_image_data_uri()
    bg_style = f"background-image:url('{bg_uri}');" if bg_uri else ""

    st.markdown(
        f"""
        <div class="hero-section slide-up">
            <div class="hero-bg-image" style="{bg_style}"></div>
            <div class="hero-content">
                <div class="hero-badge">🍀 Smart Farming Platform</div>
                <h1 class="hero-title">🌾&thinsp;AgroMind</h1>
                <div class="hero-tagline">Intelligent Crop &amp; Fertilizer Recommendation System</div>
                <p class="hero-sub">
                Get instant, data-driven crop and fertilizer recommendations,
                with clear explanations to support informed farming decisions
                based on soil and environmental conditions.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Real Streamlit widget -- can't live inside the raw HTML block above,
    # so it's centered immediately below via a narrow middle column.
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        start_clicked = st.button(
            "🌱 Start Prediction", key="start_prediction_cta", use_container_width=True
        )

    if start_clicked:
        st.session_state.page = "Crop Recommendation"
        st.rerun()

    # Floating feature chips -- kept as a single markdown call (content
    # unchanged) so the whole block parses as one properly nested tree.
    st.markdown(
        """
        <div class="floating-row">
            <div class="floating-chip slide-up-1 float-anim">
                <span class="chip-icon">🌱</span>
                <div class="chip-title">Smart Crop Match</div>
                <div class="chip-sub">Tailored to your soil &amp; climate</div>
            </div>
            <div class="floating-chip slide-up-2 float-anim" style="animation-delay:.4s">
                <span class="chip-icon">🧪</span>
                <div class="chip-title">Precise Fertilizer</div>
                <div class="chip-sub">Right nutrients, right dose</div>
            </div>
            <div class="floating-chip slide-up-3 float-anim" style="animation-delay:.8s">
                <span class="chip-icon">🤖</span>
                <div class="chip-title">AI Explained</div>
                <div class="chip-sub">Clear reasoning, your language</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

