"""Componentes de interfaz (catálogo, detalle, formulario de placeholders)
del Módulo de Plantillas de Radiología Intervencionista.

Aislado del resto de la app: solo lo usa `pages/01_Plantillas_RI.py`.
Reutiliza el mismo lenguaje visual "glass" de app.py, pero con su propio
bloque de estilos (cada página de Streamlit corre su script por separado,
así que el CSS de app.py no se hereda aquí).
"""

import html as html_lib

import streamlit as st

from .datos_seed import PLANTILLAS, por_categoria, obtener_por_id


def esc(valor):
    return html_lib.escape(str(valor))


def inyectar_estilos():
    st.markdown(
        """
        <style>
        html, body, .stApp {
            background: radial-gradient(circle at 18% -8%, #163259 0%, #081226 42%, #02040a 100%);
            color: #e8edf7;
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { display: none; }
        .block-container { max-width: 1080px; margin: 0 auto; padding-top: 2rem; padding-bottom: 4rem; }
        html, body, [class*="css"] {
            font-family: -apple-system, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
        }

        .hero-row { text-align: center; margin: 0.4rem 0 2.1rem; }
        .hero-badge {
            display: inline-flex; align-items: center; gap: .55rem;
            font-size: 1.05rem; font-weight: 700; letter-spacing: .01em;
            padding: .55rem 1.35rem; border-radius: 999px;
            background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.16);
            backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
            box-shadow: 0 10px 34px rgba(0,0,0,.45);
        }
        .hero-sub { margin-top: .85rem; color: #9fb4d9; font-size: .92rem; }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(150deg, rgba(255,255,255,.07), rgba(56,189,248,.045));
            border: 1px solid rgba(255,255,255,.14) !important;
            border-radius: 26px !important;
            backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
            box-shadow: 0 10px 44px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.06);
            padding: .3rem; margin-bottom: 1.5rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 1.3rem 1.5rem; }

        .card-label {
            font-size: .76rem; letter-spacing: .09em; text-transform: uppercase;
            color: #7fb8ff; font-weight: 700; margin-bottom: .9rem;
            display: flex; align-items: center; gap: .45rem;
        }

        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
            background: rgba(255,255,255,.055) !important;
            border: 1px solid rgba(255,255,255,.16) !important;
            border-radius: 14px !important; color: #eef3ff !important;
        }
        [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p {
            color: #a9c3ec !important; font-size: .84rem !important; font-weight: 600 !important;
        }
        [data-testid="stExpander"] {
            background: rgba(255,255,255,.045);
            border: 1px solid rgba(255,255,255,.12) !important; border-radius: 18px !important;
        }
        [data-testid="stButton"] button {
            background: linear-gradient(135deg, rgba(56,189,248,.20), rgba(99,102,241,.20));
            border: 1px solid rgba(148,197,255,.4) !important; border-radius: 999px !important;
            color: #eaf4ff !important; font-weight: 600 !important;
            box-shadow: 0 6px 20px rgba(56,189,248,.18);
            transition: box-shadow .2s ease, border-color .2s ease;
        }
        [data-testid="stButton"] button:hover {
            border-color: rgba(148,197,255,.8) !important; box-shadow: 0 8px 28px rgba(56,189,248,.32);
        }

        .cat-tag {
            font-size: .68rem; letter-spacing: .06em; text-transform: uppercase; font-weight: 700;
            display: inline-flex; padding: .3rem .8rem; border-radius: 999px; margin-bottom: 1rem;
            background: rgba(56,189,248,.12); color: #7fd4ff; border: 1px solid rgba(56,189,248,.35);
        }
        .plantilla-card {
            background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.12);
            border-left: 4px solid rgba(56,189,248,.65); border-radius: 18px;
            padding: 1rem 1.2rem; backdrop-filter: blur(12px); margin-bottom: .8rem;
        }
        .plantilla-nombre { font-weight: 700; font-size: 1rem; color: #eaf4ff; }
        .plantilla-guia { font-size: .74rem; color: #7fa8d9; margin-top: .15rem; }

        .informe-titulo { font-size: 1.35rem; font-weight: 700; color: #eaf4ff; margin-bottom: .1rem; }
        .informe-guia { font-size: .82rem; color: #7fa8d9; margin-bottom: 1.4rem; }
        .informe-seccion {
            margin-bottom: 1.1rem; padding: .9rem 1.1rem; border-radius: 16px;
            background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.1);
        }
        .informe-seccion-titulo {
            font-size: .74rem; letter-spacing: .07em; text-transform: uppercase; font-weight: 700;
            color: #7fb8ff; margin-bottom: .4rem;
        }
        .informe-seccion-texto { font-size: .9rem; line-height: 1.55; color: #d7e3f7; white-space: pre-wrap; }
        .ph-tag {
            color: #fbbf24; background: rgba(251,191,36,.12); border-radius: 6px; padding: 0 .25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _resaltar_placeholders(texto: str) -> str:
    import re

    def _sub(match):
        return f'<span class="ph-tag">[{esc(match.group(1))}]</span>'

    return re.sub(r"\[([^\]]+)\]", _sub, esc(texto))


def render_hero():
    st.markdown(
        """
        <div class="hero-row">
            <span class="hero-badge">📋 Plantillas RI</span>
            <div class="hero-sub">
                Informes estructurados para Radiología Intervencionista general / corporal
                &middot; SIR &middot; CIRSE &middot; RSNA &middot; ACR
            </div>
            <div style="margin-top:.9rem;">
                <a href="/" target="_self" class="hero-badge" style="font-size:.82rem; text-decoration:none;">💊 Volver a Anticoag·RI</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _seleccionar_plantilla(plantilla_id: str):
    st.session_state["plantilla_ri_seleccionada"] = plantilla_id


def render_catalogo():
    st.info(
        "Catálogo de plantillas de informe para procedimientos de intervencionismo "
        "general/corporal (no incluye hemodinamia ni neurointervencionismo). "
        "Uso como apoyo a la redacción; siempre adaptar al caso clínico real.",
        icon="📋",
    )

    for categoria, plantillas in por_categoria().items():
        with st.container(border=True):
            st.markdown(f'<span class="cat-tag">{esc(categoria.value)}</span>', unsafe_allow_html=True)
            for plantilla in plantillas:
                st.markdown(
                    f'<div class="plantilla-card">'
                    f'<div class="plantilla-nombre">{esc(plantilla.nombre)}</div>'
                    f'<div class="plantilla-guia">Ref.: {esc(plantilla.guia_referencia)}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.button(
                    f"Ver plantilla → {plantilla.nombre}",
                    key=f"btn_ver_{plantilla.id}",
                    width="stretch",
                    on_click=_seleccionar_plantilla,
                    args=(plantilla.id,),
                )


def render_formulario_placeholders(plantilla) -> dict:
    valores = {}
    placeholders = plantilla.placeholders()
    if not placeholders:
        return valores

    with st.expander("✏️ Completar datos del caso (opcional)", expanded=False):
        st.caption("Complete los campos que quiera reemplazar en el informe; los que deje vacíos se mantienen entre corchetes.")
        for ph in placeholders:
            key = f"ph_{plantilla.id}_{ph}"
            valores[ph] = st.text_input(ph.capitalize(), key=key, placeholder=f"[{ph}]")
    return valores


def render_detalle(plantilla_id: str):
    plantilla = obtener_por_id(plantilla_id)
    if plantilla is None:
        st.warning("No se encontró la plantilla seleccionada.")
        st.button("← Volver al catálogo", on_click=_seleccionar_plantilla, args=(None,))
        return

    st.button("← Volver al catálogo", on_click=_seleccionar_plantilla, args=(None,))

    with st.container(border=True):
        st.markdown(f'<span class="cat-tag">{esc(plantilla.categoria.value)}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="informe-titulo">{esc(plantilla.nombre)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="informe-guia">Referencia: {esc(plantilla.guia_referencia)}</div>', unsafe_allow_html=True)

        valores = render_formulario_placeholders(plantilla)

        for titulo, texto in plantilla.campos():
            valores_no_vacios = {k: v for k, v in valores.items() if v}
            texto_final = texto
            for ph, val in valores_no_vacios.items():
                texto_final = texto_final.replace(f"[{ph}]", val)
            st.markdown(
                f'<div class="informe-seccion">'
                f'<div class="informe-seccion-titulo">{esc(titulo)}</div>'
                f'<div class="informe-seccion-texto">{_resaltar_placeholders(texto_final) if texto_final == texto else esc(texto_final)}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.markdown('<div class="card-label">📄 Texto final (listo para copiar)</div>', unsafe_allow_html=True)
        valores_no_vacios = {k: v for k, v in valores.items() if v}
        st.code(plantilla.texto_completo(valores_no_vacios), language=None)


def render_modulo():
    inyectar_estilos()
    render_hero()

    seleccionada = st.session_state.get("plantilla_ri_seleccionada")
    if seleccionada:
        render_detalle(seleccionada)
    else:
        render_catalogo()
