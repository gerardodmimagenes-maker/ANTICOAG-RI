import html as html_lib
from datetime import datetime, date, timedelta

import streamlit as st

from reglas import (
    FUENTE,
    RIESGO_BAJO,
    RIESGO_ALTO,
    PROCEDIMIENTOS,
    CATALOGO_FARMACOS,
    procedimiento_a_riesgo,
    calcular_crcl_cockcroft_gault,
    calcular_inr,
    evaluar_aspirina,
    evaluar_p2y12,
    evaluar_avk,
    evaluar_hbpm,
    evaluar_hnf,
    evaluar_naco_xa,
    evaluar_dabigatran,
)

st.set_page_config(
    page_title="Anticoagulación en Radiología Intervencionista",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def esc(valor):
    return html_lib.escape(str(valor))


# ---------------------------------------------------------------------------
# Estilos — experiencia inmersiva tipo "glass" sobre fondo azul profundo
# ---------------------------------------------------------------------------
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
        [data-testid="stToolbar"] { right: 1rem; }
        .block-container {
            max-width: 1080px;
            margin: 0 auto;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        html, body, [class*="css"] {
            font-family: -apple-system, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
        }

        /* ---------- Hero ---------- */
        .hero-row { text-align: center; margin: 0.4rem 0 2.1rem; }
        .hero-badge {
            display: inline-flex; align-items: center; gap: .55rem;
            font-size: 1.05rem; font-weight: 700; letter-spacing: .01em;
            padding: .55rem 1.35rem; border-radius: 999px;
            background: rgba(255,255,255,.07);
            border: 1px solid rgba(255,255,255,.16);
            backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
            box-shadow: 0 10px 34px rgba(0,0,0,.45);
        }
        .hero-sub { margin-top: .85rem; color: #9fb4d9; font-size: .92rem; }

        /* ---------- Glass card (st.container(border=True)) ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(150deg, rgba(255,255,255,.07), rgba(56,189,248,.045));
            border: 1px solid rgba(255,255,255,.14) !important;
            border-radius: 26px !important;
            backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
            box-shadow: 0 10px 44px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.06);
            padding: .3rem;
            margin-bottom: 1.5rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 1.3rem 1.5rem; }

        .card-label {
            font-size: .76rem; letter-spacing: .09em; text-transform: uppercase;
            color: #7fb8ff; font-weight: 700; margin-bottom: .9rem;
            display: flex; align-items: center; gap: .45rem;
        }

        /* ---------- Widgets ---------- */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTextArea"] textarea {
            background: rgba(255,255,255,.055) !important;
            border: 1px solid rgba(255,255,255,.16) !important;
            border-radius: 14px !important;
            color: #eef3ff !important;
        }
        [data-baseweb="select"] > div {
            background: rgba(255,255,255,.055) !important;
            border-color: rgba(255,255,255,.16) !important;
            border-radius: 14px !important;
        }
        [data-baseweb="tag"] {
            background: linear-gradient(135deg, #38bdf8, #6366f1) !important;
            border-radius: 999px !important;
        }
        [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p {
            color: #a9c3ec !important; font-size: .84rem !important; font-weight: 600 !important;
        }
        [data-testid="stRadio"] > div[role="radiogroup"] {
            background: rgba(255,255,255,.05); border-radius: 999px; padding: 5px; gap: 2px !important;
            border: 1px solid rgba(255,255,255,.08);
        }
        [data-testid="stRadio"] label {
            border-radius: 999px !important; padding: 4px 12px !important;
        }
        [data-testid="stExpander"] {
            background: rgba(255,255,255,.045);
            border: 1px solid rgba(255,255,255,.12) !important;
            border-radius: 18px !important;
        }
        [data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
            background: linear-gradient(135deg, rgba(56,189,248,.20), rgba(99,102,241,.20));
            border: 1px solid rgba(148,197,255,.4) !important;
            border-radius: 999px !important;
            color: #eaf4ff !important; font-weight: 600 !important;
            box-shadow: 0 6px 20px rgba(56,189,248,.18);
            transition: box-shadow .2s ease, border-color .2s ease;
        }
        [data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
            border-color: rgba(148,197,255,.8) !important;
            box-shadow: 0 8px 28px rgba(56,189,248,.32);
        }
        [data-testid="stAlertContainer"], [data-testid="stAlert"] {
            border-radius: 18px !important;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,.14) !important;
        }

        /* ---------- Píldora de riesgo ---------- */
        .risk-pill {
            display: inline-flex; align-items: center; gap: .5rem;
            padding: .55rem 1.2rem; border-radius: 999px;
            font-weight: 700; font-size: .9rem; margin-top: .4rem;
            backdrop-filter: blur(8px);
        }
        .risk-pill.risk-low {
            background: rgba(52,211,153,.12); color: #6ee7b7;
            border: 1px solid rgba(110,231,183,.4); box-shadow: 0 0 26px rgba(52,211,153,.22);
        }
        .risk-pill.risk-high {
            background: rgba(248,113,113,.12); color: #fca5a5;
            border: 1px solid rgba(252,165,165,.4); box-shadow: 0 0 26px rgba(248,113,113,.22);
        }

        /* ---------- Timeline ---------- */
        .timeline-card {
            position: relative; overflow: hidden;
            background: linear-gradient(160deg, rgba(255,255,255,.065), rgba(56,189,248,.05));
            border: 1px solid rgba(255,255,255,.15);
            border-radius: 30px;
            padding: 2.3rem 1.8rem 2.6rem;
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 14px 60px rgba(0,0,0,.5);
            margin: .4rem 0 1.8rem;
        }
        .timeline-card::before {
            content: ""; position: absolute; width: 460px; height: 460px; border-radius: 50%;
            background: radial-gradient(circle, rgba(56,189,248,.18), transparent 70%);
            top: -220px; left: 50%; transform: translateX(-50%); pointer-events: none;
        }
        .timeline-card-header { position: relative; z-index: 1; margin-bottom: 2.4rem; }
        .timeline-track { position: relative; }
        .timeline-line {
            position: absolute; top: 50%; left: 3%; right: 3%; height: 3px; transform: translateY(-50%);
            background: linear-gradient(90deg, rgba(56,189,248,.05), rgba(56,189,248,.65) 47%, #fbbf24 50%, rgba(52,211,153,.65) 53%, rgba(52,211,153,.05));
            border-radius: 6px;
        }
        .tl-node { position: absolute; top: 50%; width: 0; height: 0; }
        .tl-dot {
            position: absolute; left: 0; top: 0; transform: translate(-50%, -50%);
            width: 14px; height: 14px; border-radius: 50%;
            background: #38bdf8; box-shadow: 0 0 12px rgba(56,189,248,.75);
            border: 2px solid rgba(255,255,255,.55); z-index: 3;
        }
        .tl-restart .tl-dot { background: #34d399; box-shadow: 0 0 12px rgba(52,211,153,.75); }
        .tl-dot-main {
            width: 30px; height: 30px; font-size: 14px;
            display: flex; align-items: center; justify-content: center;
            background: radial-gradient(circle, #fde68a, #fbbf24);
            box-shadow: 0 0 28px rgba(251,191,36,.8);
            border: 2px solid rgba(255,255,255,.75); z-index: 4;
            animation: pulseDay0 2.6s ease-in-out infinite;
        }
        @keyframes pulseDay0 {
            0%, 100% { box-shadow: 0 0 22px rgba(251,191,36,.7); }
            50% { box-shadow: 0 0 40px rgba(251,191,36,1); }
        }
        .tl-card {
            position: absolute; left: 0; transform: translateX(-50%);
            width: 128px; padding: .5rem .55rem; border-radius: 14px;
            background: rgba(8,14,28,.85); border: 1px solid rgba(255,255,255,.15);
            backdrop-filter: blur(6px); z-index: 2; text-align: center;
        }
        .tl-card-top { bottom: 20px; }
        .tl-card-bottom { top: 20px; }
        .tl-card-main {
            bottom: 27px; width: 152px;
            background: rgba(251,191,36,.15); border-color: rgba(251,191,36,.55);
        }
        .tl-day { font-weight: 700; font-size: .84rem; color: #eaf4ff; }
        .tl-drug { font-size: .71rem; color: #9fb4d9; margin-top: 1px; }
        .tl-date { font-size: .65rem; color: #6c84ab; margin-top: 2px; }

        .tl-extra-chips { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.6rem; position: relative; z-index: 1; }
        .chip {
            padding: .5rem 1rem; border-radius: 999px; font-size: .82rem; font-weight: 600;
            border: 1px solid rgba(255,255,255,.16); backdrop-filter: blur(8px);
        }
        .chip-ok { background: rgba(52,211,153,.12); color: #8ff0c8; border-color: rgba(110,231,183,.4); }
        .chip-alert {
            background: rgba(248,113,113,.16); color: #ffb4b4;
            border-color: rgba(252,165,165,.5); box-shadow: 0 0 20px rgba(248,113,113,.35);
        }

        /* ---------- Tarjetas de detalle ---------- */
        .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 1rem; }
        .detail-card {
            background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.12);
            border-left: 4px solid rgba(56,189,248,.65); border-radius: 18px;
            padding: 1.1rem 1.3rem; backdrop-filter: blur(12px);
        }
        .detail-card.accent-ok { border-left-color: rgba(52,211,153,.75); }
        .detail-card.accent-alert { border-left-color: rgba(248,113,113,.85); background: rgba(248,113,113,.06); }
        .detail-head { display: flex; justify-content: space-between; gap: .6rem; flex-wrap: wrap; align-items: baseline; }
        .detail-farmaco { font-weight: 700; font-size: 1.02rem; color: #eaf4ff; }
        .detail-tag { font-size: .66rem; color: #7fa8d9; text-transform: uppercase; letter-spacing: .05em; }
        .detail-accion { margin: .35rem 0 .7rem; font-weight: 600; color: #bcd4ff; font-size: .87rem; }
        .detail-row { margin-bottom: .35rem; font-size: .85rem; line-height: 1.4; }
        .detail-k { color: #7fa8d9; font-weight: 600; margin-right: .4rem; }
        .detail-v { color: #d7e3f7; }
        .detail-note {
            margin-top: .45rem; font-size: .78rem; color: #a9c3ec;
            background: rgba(255,255,255,.045); border-radius: 10px; padding: .4rem .6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inyectar_estilos()

DEFAULTS = {
    "nombre_paciente": "Paciente_Anónimo",
    "fecha_procedimiento": date.today() + timedelta(days=7),
    "modo_riesgo": "Elegir de una lista",
    "riesgo_manual": RIESGO_ALTO,
    "crcl_directo": 90,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

LABEL_A_CLAVE = {meta["label"]: clave for clave, meta in CATALOGO_FARMACOS.items()}

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-row">
        <span class="hero-badge">💊 Anticoag·RI</span>
        <div class="hero-sub">Manejo periprocedimiento de anticoagulantes · Radiología Intervencionista</div>
        <div style="margin-top:.9rem;">
            <a href="/Plantillas_RI" target="_self" class="hero-badge" style="font-size:.82rem; text-decoration:none;">📋 Plantillas de informes RI</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Esta herramienta es un apoyo a la decisión clínica. No reemplaza el juicio clínico "
    "individualizado, los protocolos institucionales vigentes ni la interconsulta con "
    "Hematología/Cardiología cuando corresponda.",
    icon="⚕️",
)

# ---------------------------------------------------------------------------
# Barra flotante 1 — Paciente & Procedimiento
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="card-label">🧑‍⚕️ Paciente &amp; procedimiento</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.1, 1, 1.3])
    with c1:
        nombre_paciente = st.text_input("Paciente / ID", key="nombre_paciente")
        medico = st.text_input("Médico responsable", key="perfil_medico", placeholder="Dr. / Dra. ...")
    with c2:
        fecha_procedimiento = st.date_input("Fecha del procedimiento", key="fecha_procedimiento")
        if fecha_procedimiento is None:
            fecha_procedimiento = DEFAULTS["fecha_procedimiento"]
            st.caption("⚠️ Ingrese una fecha válida; se usará una fecha provisional.")
        modo_riesgo = st.radio(
            "Definir riesgo por:",
            ["Elegir de una lista", "Definir manualmente"],
            key="modo_riesgo",
            label_visibility="collapsed",
        )
    with c3:
        if modo_riesgo == "Elegir de una lista":
            todos_los_procedimientos = PROCEDIMIENTOS[RIESGO_BAJO] + PROCEDIMIENTOS[RIESGO_ALTO]
            procedimiento = st.selectbox("Procedimiento planeado", todos_los_procedimientos, key="procedimiento_elegido")
            riesgo = procedimiento_a_riesgo(procedimiento)
        else:
            procedimiento = st.text_input("Nombre del procedimiento", key="procedimiento_manual", placeholder="Ej: Biopsia renal ecoguiada")
            riesgo = st.radio("Clasificación de riesgo", [RIESGO_BAJO, RIESGO_ALTO], key="riesgo_manual", horizontal=True)

        pill_class = "risk-low" if riesgo == RIESGO_BAJO else "risk-high"
        pill_icon = "🟢" if riesgo == RIESGO_BAJO else "🔴"
        st.markdown(f'<div class="risk-pill {pill_class}">{pill_icon} {esc(riesgo)}</div>', unsafe_allow_html=True)

    with st.expander("Ver clasificación de referencia"):
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Bajo riesgo**")
            for p in PROCEDIMIENTOS[RIESGO_BAJO]:
                st.caption(f"• {p}")
        with colB:
            st.markdown("**Alto riesgo**")
            for p in PROCEDIMIENTOS[RIESGO_ALTO]:
                st.caption(f"• {p}")

# ---------------------------------------------------------------------------
# Barra flotante 2 — Medicación actual
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="card-label">💊 Medicación actual del paciente</div>', unsafe_allow_html=True)
    etiquetas_elegidas = st.multiselect(
        "Antiagregantes / anticoagulantes que el paciente recibe actualmente:",
        options=list(LABEL_A_CLAVE.keys()),
        placeholder="Escriba o seleccione uno o más fármacos...",
    )
    claves_elegidas = {LABEL_A_CLAVE[etq] for etq in etiquetas_elegidas}

    detalles = {}
    hbpm_sel = "hbpm" in claves_elegidas
    avk_sel = bool(claves_elegidas & {"warfarina", "acenocumarol"})
    naco_seleccionados = bool(claves_elegidas & {"rivaroxaban", "apixaban", "edoxaban", "dabigatran"})

    bloques_activos = [b for b in (hbpm_sel, avk_sel) if b]
    if bloques_activos:
        cols = st.columns(len(bloques_activos))
        idx = 0

        if hbpm_sel:
            with cols[idx]:
                detalles["hbpm_dosis"] = st.radio("Dosis de HBPM", ["Profiláctica", "Terapéutica"], key="hbpm_dosis", horizontal=True)
            idx += 1

        if avk_sel:
            with cols[idx]:
                if "inr_actual_input" not in st.session_state:
                    st.session_state["inr_actual_input"] = 0.0
                detalles["inr_actual"] = st.number_input(
                    "INR actual (si disponible)", min_value=0.0, max_value=10.0, step=0.1, format="%.1f", key="inr_actual_input",
                )
                with st.expander("Calcular INR con datos de laboratorio (PT / ISI)"):
                    st.caption(
                        "INR = (PT del paciente / PT control o valor normal medio del laboratorio) ^ ISI. "
                        "El ISI y el PT control figuran en el reporte del laboratorio o en el inserto del reactivo."
                    )
                    for _k, _v in (("pt_paciente_txt", "14.0"), ("pt_control_txt", "12.0"), ("isi_reactivo_txt", "1.00")):
                        if _k not in st.session_state:
                            st.session_state[_k] = _v

                    ci1, ci2, ci3 = st.columns(3)
                    with ci1:
                        st.text_input("PT paciente (seg)", key="pt_paciente_txt")
                    with ci2:
                        st.text_input("PT control (seg)", key="pt_control_txt")
                    with ci3:
                        st.text_input("ISI", key="isi_reactivo_txt")

                    def _parsear_numero(texto):
                        try:
                            return float(str(texto).strip().replace(",", "."))
                        except (TypeError, ValueError):
                            return None

                    def _aplicar_inr_calculado():
                        pt_paciente = _parsear_numero(st.session_state.pt_paciente_txt)
                        pt_control = _parsear_numero(st.session_state.pt_control_txt)
                        isi_reactivo = _parsear_numero(st.session_state.isi_reactivo_txt)
                        if pt_paciente is None or pt_control is None or isi_reactivo is None:
                            st.session_state["_inr_calc_error"] = "Revise que los 3 valores sean numéricos (ej: 13.5)."
                            return
                        inr_calc = calcular_inr(pt_paciente, pt_control, isi_reactivo)
                        if inr_calc is None:
                            st.session_state["_inr_calc_error"] = "Los valores deben ser mayores a 0."
                            return
                        st.session_state["_inr_calc_error"] = None
                        st.session_state["inr_actual_input"] = round(inr_calc, 1)

                    st.button("Calcular y usar este INR", width="stretch", on_click=_aplicar_inr_calculado)
                    if st.session_state.get("_inr_calc_error"):
                        st.warning(st.session_state["_inr_calc_error"])
            idx += 1

with st.container(border=True):
    st.markdown('<div class="card-label">🧪 Función renal (CrCl) — para ajuste de NACOs</div>', unsafe_allow_html=True)
    fc1, fc2 = st.columns([1, 1.4])
    with fc1:
        crcl_directo = st.number_input(
            "Aclaramiento de Creatinina (CrCl), mL/min", min_value=0, max_value=200, step=1, key="crcl_directo",
        )
    with fc2:
        with st.expander("Calcular CrCl (Cockcroft-Gault)"):
            cg1, cg2 = st.columns(2)
            with cg1:
                edad_cg = st.number_input("Edad", min_value=1, max_value=110, value=65, step=1, key="edad_cg")
                peso_cg = st.number_input("Peso (kg)", min_value=1, max_value=250, value=70, step=1, key="peso_cg")
            with cg2:
                creat_cg = st.number_input("Creatinina (mg/dL)", min_value=0.1, max_value=20.0, value=1.0, step=0.1, format="%.1f", key="creat_cg")
                sexo_cg = st.radio("Sexo", ["Femenino", "Masculino"], horizontal=True, key="sexo_cg")

            def _aplicar_crcl_calculado():
                crcl_calc = calcular_crcl_cockcroft_gault(
                    st.session_state.edad_cg,
                    st.session_state.peso_cg,
                    st.session_state.creat_cg,
                    st.session_state.sexo_cg,
                )
                if crcl_calc:
                    st.session_state["crcl_directo"] = round(crcl_calc)

            st.button("Calcular y usar este CrCl", width="stretch", on_click=_aplicar_crcl_calculado)

crcl = st.session_state["crcl_directo"]

# ---------------------------------------------------------------------------
# Motor de reglas: generar recomendaciones para cada fármaco seleccionado
# ---------------------------------------------------------------------------
recomendaciones = []

if "aspirina" in claves_elegidas:
    recomendaciones.append(evaluar_aspirina(riesgo))
if "clopidogrel" in claves_elegidas:
    recomendaciones.append(evaluar_p2y12(riesgo, "Clopidogrel"))
if "prasugrel" in claves_elegidas:
    recomendaciones.append(evaluar_p2y12(riesgo, "Prasugrel"))
if "ticagrelor" in claves_elegidas:
    recomendaciones.append(evaluar_p2y12(riesgo, "Ticagrelor"))
if "warfarina" in claves_elegidas:
    inr_val = detalles.get("inr_actual") or None
    recomendaciones.append(evaluar_avk(riesgo, "Warfarina", inr_val if inr_val else None))
if "acenocumarol" in claves_elegidas:
    inr_val = detalles.get("inr_actual") or None
    recomendaciones.append(evaluar_avk(riesgo, "Acenocumarol", inr_val if inr_val else None))
if "hbpm" in claves_elegidas:
    recomendaciones.append(evaluar_hbpm(detalles.get("hbpm_dosis", "Profiláctica"), riesgo))
if "hnf" in claves_elegidas:
    recomendaciones.append(evaluar_hnf())
if "rivaroxaban" in claves_elegidas:
    recomendaciones.append(evaluar_naco_xa("Rivaroxabán", riesgo, crcl))
if "apixaban" in claves_elegidas:
    recomendaciones.append(evaluar_naco_xa("Apixabán", riesgo, crcl))
if "edoxaban" in claves_elegidas:
    recomendaciones.append(evaluar_naco_xa("Edoxabán", riesgo, crcl))
if "dabigatran" in claves_elegidas:
    recomendaciones.append(evaluar_dabigatran(riesgo, crcl))

hay_alerta_roja = any(r.alerta_roja for r in recomendaciones)
hay_p2y12_y_otro = sum(1 for r in recomendaciones if "P2Y12" in r.categoria) > 0 and len(recomendaciones) > 1
fecha_dt = datetime.combine(fecha_procedimiento, datetime.min.time())

if naco_seleccionados:
    st.caption(f"ℹ️ Se usará el CrCl indicado arriba: **{crcl} mL/min**.")

# ---------------------------------------------------------------------------
# Timeline — el centro de la experiencia
# ---------------------------------------------------------------------------
def render_timeline(recos, fecha_procedimiento_dt):
    suspend_items, restart_items, chip_items = [], [], []

    for r in recos:
        if r.alerta_roja:
            chip_items.append(("alert", f"🚨 {esc(r.farmaco)} — ALERTA ROJA: requiere interconsulta con Hematología"))
            continue

        fecha_susp = r.fecha_suspension(fecha_procedimiento_dt)
        fecha_rein = r.fecha_reinicio(fecha_procedimiento_dt)

        if fecha_susp is not None:
            dias = (fecha_procedimiento_dt - fecha_susp).total_seconds() / 86400.0
            suspend_items.append((dias, r.farmaco, fecha_susp))
        else:
            chip_items.append(("ok", f"✅ {esc(r.farmaco)} — No suspender"))

        if fecha_rein is not None:
            dias_r = (fecha_rein - fecha_procedimiento_dt).total_seconds() / 86400.0
            restart_items.append((dias_r, r.farmaco, fecha_rein))

    if not suspend_items and not restart_items and not chip_items:
        return

    max_susp = max([d for d, _, _ in suspend_items] + [1.0])
    max_rein = max([d for d, _, _ in restart_items] + [1.0])
    suspend_items.sort(key=lambda x: -x[0])
    restart_items.sort(key=lambda x: x[0])

    gap_min = 18  # separación mínima (en % del ancho) respecto del nodo central Día 0

    nodos_html = []
    for i, (dias, farmaco, fecha) in enumerate(suspend_items):
        distancia = max(35 * (min(dias, max_susp) / max_susp) if max_susp > 0 else 0, gap_min)
        left_pct = 50 - distancia
        offset = 20 + (i % 3) * 76
        dia_label = f"Día -{dias:.0f}" if dias >= 1 else f"-{dias * 24:.0f} h"
        nodos_html.append(
            f'<div class="tl-node tl-suspend" style="left:{left_pct:.1f}%;">'
            f'<div class="tl-card tl-card-top" style="bottom:{offset}px;">'
            f'<div class="tl-day">{esc(dia_label)}</div>'
            f'<div class="tl-drug">{esc(farmaco)}</div>'
            f'<div class="tl-date">{fecha.strftime("%d/%m %H:%M")}</div>'
            f'</div><div class="tl-dot"></div></div>'
        )

    for i, (dias, farmaco, fecha) in enumerate(restart_items):
        distancia = max(35 * (min(dias, max_rein) / max_rein) if max_rein > 0 else 0, gap_min)
        left_pct = 50 + distancia
        offset = 20 + (i % 3) * 76
        dia_label = f"+{dias:.0f} d" if dias >= 1 else f"+{dias * 24:.0f} h"
        nodos_html.append(
            f'<div class="tl-node tl-restart" style="left:{left_pct:.1f}%;">'
            f'<div class="tl-dot"></div>'
            f'<div class="tl-card tl-card-bottom" style="top:{offset}px;">'
            f'<div class="tl-day">{esc(dia_label)}</div>'
            f'<div class="tl-drug">{esc(farmaco)}</div>'
            f'<div class="tl-date">{fecha.strftime("%d/%m %H:%M")}</div>'
            f'</div></div>'
        )

    day0_html = (
        '<div class="tl-node tl-day0" style="left:50%;">'
        '<div class="tl-card tl-card-main">'
        '<div class="tl-day">DÍA 0</div>'
        '<div class="tl-drug">Procedimiento</div>'
        f'<div class="tl-date">{fecha_procedimiento_dt.strftime("%d/%m/%Y")}</div>'
        '</div><div class="tl-dot tl-dot-main">📍</div></div>'
    )

    filas_extra = min(max(len(suspend_items), len(restart_items), 1), 3)
    extremo_maximo = 20 + (filas_extra - 1) * 76 + 76  # separación + filas + alto aprox. de tarjeta
    track_height = 2 * extremo_maximo + 24

    html_bloque = (
        '<div class="timeline-card">'
        '<div class="timeline-card-header"><span class="card-label">🕒 Línea de tiempo del procedimiento</span></div>'
        f'<div class="timeline-track" style="height:{track_height}px;">'
        '<div class="timeline-line"></div>'
        f"{day0_html}{''.join(nodos_html)}"
        "</div></div>"
    )
    st.markdown(html_bloque, unsafe_allow_html=True)

    if chip_items:
        chips_html = "".join(f'<span class="chip chip-{tipo}">{texto}</span>' for tipo, texto in chip_items)
        st.markdown(f'<div class="tl-extra-chips">{chips_html}</div>', unsafe_allow_html=True)


if not recomendaciones:
    st.caption("Seleccione al menos un fármaco arriba para generar el plan de manejo.")
else:
    if hay_alerta_roja:
        st.error(
            "🚨 **ALERTA ROJA** — se requiere interconsulta con Hematología antes de definir "
            "el manejo perioperatorio.",
            icon="🚨",
        )
    if hay_p2y12_y_otro:
        st.warning(
            "El paciente combina un inhibidor P2Y12 con otro antiagregante/anticoagulante "
            "(doble/triple terapia). Evalúe conjuntamente el riesgo de sangrado y el riesgo "
            "trombótico al suspender; considere interconsulta con Cardiología/Hematología.",
            icon="⚠️",
        )

    render_timeline(recomendaciones, fecha_dt)

    st.markdown('<div class="card-label" style="margin-top:.4rem;">📋 Detalle por fármaco</div>', unsafe_allow_html=True)
    tarjetas = []
    for r in recomendaciones:
        if r.alerta_roja:
            accent = "accent-alert"
        elif r.accion == "No suspender":
            accent = "accent-ok"
        else:
            accent = ""
        notas_html = "".join(f'<div class="detail-note">ℹ️ {esc(n)}</div>' for n in r.notas)
        reinicio_html = (
            f'<div class="detail-row"><span class="detail-k">Reinicio</span><span class="detail-v">{esc(r.detalle_reinicio)}</span></div>'
            if r.detalle_reinicio else ""
        )
        tarjetas.append(
            f'<div class="detail-card {accent}">'
            f'<div class="detail-head"><span class="detail-farmaco">{esc(r.farmaco)}</span>'
            f'<span class="detail-tag">{esc(r.categoria)}</span></div>'
            f'<div class="detail-accion">{esc(r.accion)}</div>'
            f'<div class="detail-row"><span class="detail-k">Suspensión</span><span class="detail-v">{esc(r.detalle_suspension)}</span></div>'
            f'{reinicio_html}{notas_html}</div>'
        )
    st.markdown(f'<div class="detail-grid">{"".join(tarjetas)}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Informe exportable
# ---------------------------------------------------------------------------
def generar_texto_informe():
    lineas = [
        "PLAN DE MANEJO PERIPROCEDIMIENTO — ANTICOAGULACIÓN EN RADIOLOGÍA INTERVENCIONISTA",
        "",
        f"Paciente: {nombre_paciente}",
        f"Médico responsable: {medico or '-'}",
        f"Fecha del procedimiento: {fecha_procedimiento.strftime('%d/%m/%Y')}",
        f"Procedimiento: {procedimiento}",
        f"Clasificación de riesgo de sangrado: {riesgo}",
        "",
    ]
    if naco_seleccionados:
        lineas.append(f"Aclaramiento de Creatinina (CrCl): {crcl} mL/min")
        lineas.append("")

    if hay_alerta_roja:
        lineas.append("*** ALERTA ROJA: SE REQUIERE INTERCONSULTA CON HEMATOLOGÍA ANTES DE PROCEDER ***")
        lineas.append("")

    lineas.append("FÁRMACOS EVALUADOS")
    lineas.append("-" * 60)
    for r in recomendaciones:
        lineas.append(f"\n• {r.farmaco} ({r.categoria})")
        lineas.append(f"  Acción: {r.accion}")
        lineas.append(f"  Suspensión: {r.detalle_suspension}")
        fecha_susp = r.fecha_suspension(fecha_dt)
        if fecha_susp:
            lineas.append(f"  Suspender desde: {fecha_susp.strftime('%d/%m/%Y %H:%M')}")
        if r.detalle_reinicio:
            lineas.append(f"  Reinicio: {r.detalle_reinicio}")
        fecha_rein = r.fecha_reinicio(fecha_dt)
        if fecha_rein:
            lineas.append(f"  Reiniciar desde: {fecha_rein.strftime('%d/%m/%Y %H:%M')}")
        for nota in r.notas:
            lineas.append(f"  Nota: {nota}")

    lineas.append("")
    lineas.append("-" * 60)
    lineas.append(f"Fuente: {FUENTE}")
    lineas.append(
        "Documento de apoyo a la decisión clínica. No sustituye el juicio clínico "
        "individualizado ni los protocolos institucionales vigentes."
    )
    return "\n".join(lineas)


def generar_pdf_informe(texto):
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    reemplazos = {
        "\u2265": ">=", "\u2264": "<=", "\u2014": "-", "\u2013": "-",
        "\u2192": "->", "\u2026": "...", "\u00d7": "x",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    }

    def limpiar(t):
        for o, n in reemplazos.items():
            t = t.replace(o, n)
        return t.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(0, 8, limpiar("Plan de Manejo Periprocedimiento — Anticoagulación en RI"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(3, 105, 161)
    pdf.set_line_width(0.6)
    y = pdf.get_y()
    pdf.line(14, y, 196, y)
    pdf.ln(6)
    pdf.set_text_color(0, 0, 0)

    for linea in texto.split("\n"):
        linea = linea.strip()
        pdf.set_x(pdf.l_margin)
        if not linea:
            pdf.ln(3)
            continue
        if linea.isupper() and len(linea) < 90:
            pdf.set_font("Helvetica", "B", 11)
        elif linea.startswith("***"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(220, 38, 38)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(pdf.epw, 5.5, limpiar(linea))

    return bytes(pdf.output())


if recomendaciones:
    with st.container(border=True):
        st.markdown('<div class="card-label">📄 Informe / exportar plan</div>', unsafe_allow_html=True)
        informe_texto = generar_texto_informe()
        with st.expander("Ver informe de texto"):
            st.text_area("Informe", value=informe_texto, height=280, label_visibility="collapsed")

        pdf_bytes = generar_pdf_informe(informe_texto)
        nombre_archivo = f"Plan_Anticoagulacion_{nombre_paciente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        st.download_button(
            label="⬇ Descargar plan en PDF",
            data=pdf_bytes,
            file_name=nombre_archivo,
            mime="application/pdf",
        )
