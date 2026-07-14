"""Página adicional (multipage Streamlit) — Módulo de Plantillas de RI.

Este archivo es 100% nuevo y aditivo: Streamlit lo detecta automáticamente
por vivir en `pages/`, sin necesidad de tocar `app.py`. No importa ni
modifica nada de la lógica de anticoagulación existente.
"""

import streamlit as st

from plantillas_ri.ui import render_modulo

st.set_page_config(
    page_title="Plantillas RI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_modulo()
