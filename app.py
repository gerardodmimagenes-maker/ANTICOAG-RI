import streamlit as st
from datetime import datetime, date, timedelta

from reglas import (
    FUENTE,
    RIESGO_BAJO,
    RIESGO_ALTO,
    PROCEDIMIENTOS,
    CATALOGO_FARMACOS,
    procedimiento_a_riesgo,
    calcular_crcl_cockcroft_gault,
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
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estilos — identidad azul/teal clínica (distinta de la app de BI-RADS mama)
# ---------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #f0f9ff; }
    .block-container { color: #0c1e2e; }
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #e0f2fe !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0c1e2e !important;
    }
    .main-title-blue { color: #0369a1 !important; letter-spacing: 0.3px; }
    .accent-subtitle { color: #0369a1 !important; }

    .stButton > button:not([kind="secondary"]),
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(3, 105, 161, 0.22) !important;
    }
    .stButton > button:not([kind="secondary"]):hover,
    .stDownloadButton > button:hover { filter: brightness(1.06); }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #bae6fd !important;
        border-radius: 10px !important;
        background-color: #ffffff !important;
        box-shadow: 0 1px 4px rgba(3, 105, 161, 0.07) !important;
    }

    .tarjeta-farmaco {
        border-left: 5px solid #0369a1;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(3, 105, 161, 0.08);
    }
    .tarjeta-farmaco.no-suspender { border-left-color: #059669; }
    .tarjeta-farmaco.alerta { border-left-color: #dc2626; background-color: #fef2f2; }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .badge-suspender { background-color: #fef3c7; color: #92400e; }
    .badge-no-suspender { background-color: #d1fae5; color: #065f46; }
    .badge-alerta { background-color: #fee2e2; color: #991b1b; }

    .alerta-roja-banner {
        background-color: #140000;
        border: 2px solid #ff073a;
        box-shadow: 0 0 10px #ff073a, 0 0 22px rgba(255, 7, 58, 0.55);
        color: #ff073a;
        padding: 14px 18px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 15px;
        text-align: center;
        margin-bottom: 15px;
        letter-spacing: 0.4px;
    }
    </style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "nombre_paciente": "Paciente_Anónimo",
    "fecha_procedimiento": date.today() + timedelta(days=7),
    "modo_riesgo": "Elegir de una lista",
    "riesgo_manual": RIESGO_ALTO,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------------------
# Sidebar — Datos del paciente y del procedimiento
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<h2 style='text-align:center;color:#0c1e2e;font-weight:900;letter-spacing:1px;margin-bottom:0;'>💊 ANTICOAG-RI</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='accent-subtitle' style='text-align:center;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1px;margin-top:3px;'>Copiloto de Manejo Periprocedimiento</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size:16px;'>📝 Datos del Paciente</h3>", unsafe_allow_html=True)
    nombre_paciente = st.text_input("Paciente / ID:", key="nombre_paciente")
    medico = st.text_input("Médico responsable:", key="perfil_medico", placeholder="Dr. / Dra. ...")
    fecha_procedimiento = st.date_input("Fecha programada del procedimiento:", key="fecha_procedimiento")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:16px;'>🩸 Riesgo de Sangrado del Procedimiento</h3>", unsafe_allow_html=True)
    modo_riesgo = st.radio(
        "¿Cómo desea definir el riesgo?",
        ["Elegir de una lista", "Definir manualmente"],
        key="modo_riesgo",
    )

    if modo_riesgo == "Elegir de una lista":
        todos_los_procedimientos = PROCEDIMIENTOS[RIESGO_BAJO] + PROCEDIMIENTOS[RIESGO_ALTO]
        procedimiento = st.selectbox("Procedimiento planeado:", todos_los_procedimientos, key="procedimiento_elegido")
        riesgo = procedimiento_a_riesgo(procedimiento)
    else:
        procedimiento = st.text_input("Nombre del procedimiento:", key="procedimiento_manual", placeholder="Ej: Biopsia renal ecoguiada")
        riesgo = st.radio("Clasificación de riesgo:", [RIESGO_BAJO, RIESGO_ALTO], key="riesgo_manual", horizontal=True)

    color_riesgo = "#059669" if riesgo == RIESGO_BAJO else "#dc2626"
    st.markdown(
        f"<div style='text-align:center;background-color:{color_riesgo};color:white;padding:8px;border-radius:8px;font-weight:800;margin-top:6px;'>{riesgo.upper()}</div>",
        unsafe_allow_html=True,
    )

    with st.expander("📋 Ver clasificación de referencia"):
        st.markdown("**Bajo riesgo:**")
        for p in PROCEDIMIENTOS[RIESGO_BAJO]:
            st.caption(f"• {p}")
        st.markdown("**Alto riesgo:**")
        for p in PROCEDIMIENTOS[RIESGO_ALTO]:
            st.caption(f"• {p}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:16px;'>🧪 Función Renal (para NACOs)</h3>", unsafe_allow_html=True)
    if "crcl_directo" not in st.session_state:
        st.session_state["crcl_directo"] = 90.0
    crcl_directo = st.number_input("Aclaramiento de Creatinina (CrCl) mL/min:", min_value=0.0, max_value=200.0, step=1.0, key="crcl_directo")
    with st.expander("Calcular CrCl (Cockcroft-Gault)"):
        c1, c2 = st.columns(2)
        with c1:
            edad_cg = st.number_input("Edad:", min_value=1, max_value=110, value=65, key="edad_cg")
            peso_cg = st.number_input("Peso (kg):", min_value=1.0, max_value=250.0, value=70.0, key="peso_cg")
        with c2:
            creat_cg = st.number_input("Creatinina sérica (mg/dL):", min_value=0.1, max_value=20.0, value=1.0, step=0.1, key="creat_cg")
            sexo_cg = st.radio("Sexo:", ["Femenino", "Masculino"], horizontal=True, key="sexo_cg")

        def _aplicar_crcl_calculado():
            crcl_calc = calcular_crcl_cockcroft_gault(
                st.session_state.edad_cg,
                st.session_state.peso_cg,
                st.session_state.creat_cg,
                st.session_state.sexo_cg,
            )
            if crcl_calc:
                st.session_state["crcl_directo"] = round(crcl_calc, 1)

        st.button("Calcular y usar este CrCl", use_container_width=True, on_click=_aplicar_crcl_calculado)
    crcl = st.session_state["crcl_directo"]

# ---------------------------------------------------------------------------
# Cuerpo principal
# ---------------------------------------------------------------------------
st.markdown("<h1 class='main-title-blue' style='font-size:28px;font-weight:800;margin-bottom:0;'>MANEJO PERIPROCEDIMIENTO DE ANTICOAGULACIÓN</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='accent-subtitle' style='font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-top:2px;'>Radiología Intervencionista • {FUENTE}</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.info(
    "⚕️ Esta herramienta es un **apoyo a la decisión clínica** basado en las guías de consenso SIR (2019). "
    "No reemplaza el juicio clínico individualizado, los protocolos institucionales vigentes ni la "
    "interconsulta con Hematología/Cardiología cuando corresponda.",
    icon="⚕️",
)

col_farmacos, col_resultados = st.columns([1, 1.3])

with col_farmacos:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;font-size:18px;'>💊 Medicación Actual del Paciente</h3>", unsafe_allow_html=True)
        st.caption("Seleccione todos los antiagregantes / anticoagulantes que el paciente esté recibiendo actualmente.")

        seleccion = {}
        for clave, meta in CATALOGO_FARMACOS.items():
            seleccion[clave] = st.checkbox(meta["label"], key=f"chk_{clave}")

        detalles = {}
        if seleccion.get("hbpm"):
            detalles["hbpm_dosis"] = st.radio("Dosis de HBPM:", ["Profiláctica", "Terapéutica"], key="hbpm_dosis", horizontal=True)
        if seleccion.get("warfarina") or seleccion.get("acenocumarol"):
            detalles["inr_actual"] = st.number_input("INR actual (si disponible):", min_value=0.0, max_value=10.0, step=0.1, value=0.0, key="inr_actual_input")

        naco_seleccionados = any(seleccion.get(f) for f in ("rivaroxaban", "apixaban", "edoxaban", "dabigatran"))
        if naco_seleccionados:
            st.caption(f"ℹ️ Se usará el CrCl ingresado en el panel lateral: **{crcl:.0f} mL/min**.")

# ---------------------------------------------------------------------------
# Motor de reglas: generar recomendaciones para cada fármaco seleccionado
# ---------------------------------------------------------------------------
recomendaciones = []

if seleccion.get("aspirina"):
    recomendaciones.append(evaluar_aspirina(riesgo))
if seleccion.get("clopidogrel"):
    recomendaciones.append(evaluar_p2y12(riesgo, "Clopidogrel"))
if seleccion.get("prasugrel"):
    recomendaciones.append(evaluar_p2y12(riesgo, "Prasugrel"))
if seleccion.get("ticagrelor"):
    recomendaciones.append(evaluar_p2y12(riesgo, "Ticagrelor"))
if seleccion.get("warfarina"):
    inr_val = detalles.get("inr_actual") or None
    recomendaciones.append(evaluar_avk(riesgo, "Warfarina", inr_val if inr_val else None))
if seleccion.get("acenocumarol"):
    inr_val = detalles.get("inr_actual") or None
    recomendaciones.append(evaluar_avk(riesgo, "Acenocumarol", inr_val if inr_val else None))
if seleccion.get("hbpm"):
    recomendaciones.append(evaluar_hbpm(detalles.get("hbpm_dosis", "Profiláctica"), riesgo))
if seleccion.get("hnf"):
    recomendaciones.append(evaluar_hnf())
if seleccion.get("rivaroxaban"):
    recomendaciones.append(evaluar_naco_xa("Rivaroxabán", riesgo, crcl))
if seleccion.get("apixaban"):
    recomendaciones.append(evaluar_naco_xa("Apixabán", riesgo, crcl))
if seleccion.get("edoxaban"):
    recomendaciones.append(evaluar_naco_xa("Edoxabán", riesgo, crcl))
if seleccion.get("dabigatran"):
    recomendaciones.append(evaluar_dabigatran(riesgo, crcl))

hay_alerta_roja = any(r.alerta_roja for r in recomendaciones)
hay_p2y12_y_otro = sum(1 for r in recomendaciones if "P2Y12" in r.categoria) > 0 and len(recomendaciones) > 1

fecha_dt = datetime.combine(fecha_procedimiento, datetime.min.time())

with col_resultados:
    if hay_alerta_roja:
        st.markdown(
            '<div class="alerta-roja-banner">🚨 ALERTA ROJA: se requiere interconsulta con Hematología antes de definir el manejo perioperatorio</div>',
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown("<h3 class='accent-subtitle' style='margin-top:0;font-size:18px;'>🤖 Plan de Manejo Sugerido</h3>", unsafe_allow_html=True)

        if not recomendaciones:
            st.caption("Seleccione al menos un fármaco en el panel izquierdo para generar el plan de manejo.")
        else:
            for r in recomendaciones:
                clase = "alerta" if r.alerta_roja else ("no-suspender" if r.accion == "No suspender" else "")
                badge_clase = "badge-alerta" if r.alerta_roja else ("badge-no-suspender" if r.accion == "No suspender" else "badge-suspender")

                fecha_susp = r.fecha_suspension(fecha_dt)
                fecha_rein = r.fecha_reinicio(fecha_dt)

                html = f"""
                <div class="tarjeta-farmaco {clase}">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong style="font-size:15px;">{r.farmaco}</strong>
                        <span class="badge {badge_clase}">{r.accion}</span>
                    </div>
                    <p style="font-size:12px;color:#64748b;margin:2px 0 6px 0;">{r.categoria}</p>
                    <p style="margin:4px 0;"><b>Suspensión:</b> {r.detalle_suspension}</p>
                """
                if fecha_susp:
                    html += f"<p style='margin:4px 0;font-size:13px;color:#0369a1;'><b>🗓️ Suspender desde:</b> {fecha_susp.strftime('%d/%m/%Y %H:%M')}</p>"
                if r.detalle_reinicio:
                    html += f"<p style='margin:4px 0;'><b>Reinicio:</b> {r.detalle_reinicio}</p>"
                if fecha_rein:
                    html += f"<p style='margin:4px 0;font-size:13px;color:#0369a1;'><b>🗓️ Reiniciar desde:</b> {fecha_rein.strftime('%d/%m/%Y %H:%M')}</p>"
                for nota in r.notas:
                    html += f"<p style='margin:4px 0;font-size:12.5px;color:#475569;'>ℹ️ {nota}</p>"
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)

            if hay_p2y12_y_otro:
                st.warning(
                    "⚠️ El paciente combina un inhibidor P2Y12 con otro antiagregante/anticoagulante "
                    "(doble/triple terapia). El riesgo de sangrado y el riesgo trombótico al suspender "
                    "deben evaluarse conjuntamente; considere interconsulta con Cardiología/Hematología.",
                    icon="⚠️",
                )

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
        lineas.append(f"Aclaramiento de Creatinina (CrCl): {crcl:.0f} mL/min")
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
    import io
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


with col_resultados:
    if recomendaciones:
        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0;font-size:16px;'>📄 Informe / Exportar Plan</h3>", unsafe_allow_html=True)
            informe_texto = generar_texto_informe()
            st.text_area("Informe", value=informe_texto, height=280, label_visibility="collapsed")

            pdf_bytes = generar_pdf_informe(informe_texto)
            nombre_archivo = f"Plan_Anticoagulacion_{nombre_paciente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            st.download_button(
                label="⬇ Descargar Plan en PDF",
                data=pdf_bytes,
                file_name=nombre_archivo,
                mime="application/pdf",
                use_container_width=True,
            )
