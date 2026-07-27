"""
Simple footer component shown at the bottom of every page.
"""

import streamlit as st


def render_footer():
    st.markdown(
        """
        <div class="app-footer">
            🍀 Empowering Smarter Farming &nbsp;&middot;&nbsp;
            <span class="brand">AgroMind</span> © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
