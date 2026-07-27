"""
Dashboard component — the header strip shown at the top of the
Crop Recommendation and Fertilizer Recommendation pages once the
user has entered the app (via the "Start Prediction" CTA or the
sidebar). Wraps the stat cards from cards.py with a section title.
"""

import streamlit as st
from components.cards import render_stat_cards


def render_dashboard_header(title: str, subtitle: str):
    st.markdown(f'<div class="eyebrow fade-in">AGROMIND DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title fade-in">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub fade-in">{subtitle}</div>', unsafe_allow_html=True)

    render_stat_cards()

    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
