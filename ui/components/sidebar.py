"""
Sidebar navigation component for AgroMind.
Renders the brand header + nav buttons, and manages page switching
through st.session_state["page"].
"""

import streamlit as st

# Pages exposed in the sidebar: (session key, icon, display label)
NAV_ITEMS = [
    ("Home", "🏠", "Home"),
    ("Crop Recommendation", "🌱", "Crop Recommendation"),
    ("Fertilizer Recommendation", "🧪", "Fertilizer Recommendation"),
    ("AI Explanation", "🤖", "AI Explanation"),
    ("About", "ℹ️", "About"),
]


def render_sidebar():
    """Draws the AgroMind sidebar and returns the currently selected page."""

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    with st.sidebar:
        # Brand header
        st.markdown(
            """
            <div class="sidebar-brand">
                <span class="logo-emoji">🌾</span>
                <div>
                    <div class="brand-text">AgroMind</div>
                    <div class="brand-sub">AI Smart Farming</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Nav buttons
        for key, icon, label in NAV_ITEMS:
            is_active = st.session_state.page == key
            wrapper_key = f"nav_wrap_{key.replace(' ', '_')}"
            with st.container(key=wrapper_key):
                if is_active:
                    st.markdown('<div class="nav-active-marker"></div>', unsafe_allow_html=True)
                if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()

        st.markdown(
            """
            <div class="sidebar-footer-note">
                🌾 Smart Farming Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.page
