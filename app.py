import pandas as pd
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
# Sidebar — Datos del paciente y del procedimiento
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("💊 Anticoag-RI")
    st.caption("Manejo periprocedimiento de anticoagulantes en Radiología Intervencionista")

    st.subheader("Paciente", divider="gray")
    nombre_paciente = st.text_input("Paciente / ID", key="nombre_paciente")
    medico = st.text_input("Médico responsable", key="perfil_medico", placeholder="Dr. / Dra. ...")
    fecha_procedimiento = st.date_input("Fecha del procedimiento", key="fecha_procedimiento")

    st.subheader("Riesgo de sangrado", divider="gray")
    modo_riesgo = st.radio(
        "Definir riesgo por:",
        ["Elegir de una lista", "Definir manualmente"],
        key="modo_riesgo",
        label_visibility="collapsed",
    )

    if modo_riesgo == "Elegir de una lista":
        todos_los_procedimientos = PROCEDIMIENTOS[RIESGO_BAJO] + PROCEDIMIENTOS[RIESGO_ALTO]
        procedimiento = st.selectbox("Procedimiento planeado", todos_los_procedimientos, key="procedimiento_elegido")
        riesgo = procedimiento_a_riesgo(procedimiento)
    else:
        procedimiento = st.text_input("Nombre del procedimiento", key="procedimiento_manual", placeholder="Ej: Biopsia renal ecoguiada")
        riesgo = st.radio("Clasificación de riesgo", [RIESGO_BAJO, RIESGO_ALTO], key="riesgo_manual", horizontal=True)

    if riesgo == RIESGO_BAJO:
        st.success(f"Riesgo: {riesgo}", icon="🟢")
    else:
        st.error(f"Riesgo: {riesgo}", icon="🔴")

    with st.expander("Ver clasificación de referencia"):
        st.markdown("**Bajo riesgo**")
        for p in PROCEDIMIENTOS[RIESGO_BAJO]:
            st.caption(f"• {p}")
        st.markdown("**Alto riesgo**")
        for p in PROCEDIMIENTOS[RIESGO_ALTO]:
            st.caption(f"• {p}")

    st.subheader("Función renal (NACOs)", divider="gray")
    crcl_directo = st.number_input(
        "Aclaramiento de Creatinina (CrCl), mL/min", min_value=0, max_value=200, step=1, key="crcl_directo",
    )
    with st.expander("Calcular CrCl (Cockcroft-Gault)"):
        c1, c2 = st.columns(2)
        with c1:
            edad_cg = st.number_input("Edad", min_value=1, max_value=110, value=65, step=1, key="edad_cg")
            peso_cg = st.number_input("Peso (kg)", min_value=1, max_value=250, value=70, step=1, key="peso_cg")
        with c2:
            creat_cg = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, max_value=20.0, value=1.0, step=0.1, format="%.1f", key="creat_cg")
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

        st.button("Calcular y usar este CrCl", use_container_width=True, on_click=_aplicar_crcl_calculado)
    crcl = st.session_state["crcl_directo"]

# ---------------------------------------------------------------------------
# Cuerpo principal
# ---------------------------------------------------------------------------
st.title("Manejo periprocedimiento de anticoagulación")
st.caption(f"Radiología Intervencionista · {FUENTE}")

st.info(
    "Esta herramienta es un apoyo a la decisión clínica. No reemplaza el juicio clínico "
    "individualizado, los protocolos institucionales vigentes ni la interconsulta con "
    "Hematología/Cardiología cuando corresponda.",
    icon="⚕️",
)

st.subheader("Medicación actual del paciente", divider="gray")
etiquetas_elegidas = st.multiselect(
    "Antiagregantes / anticoagulantes que el paciente recibe actualmente:",
    options=list(LABEL_A_CLAVE.keys()),
    placeholder="Escriba o seleccione uno o más fármacos...",
)
claves_elegidas = {LABEL_A_CLAVE[etq] for etq in etiquetas_elegidas}

detalles = {}
col_extra1, col_extra2 = st.columns(2)
if "hbpm" in claves_elegidas:
    with col_extra1:
        detalles["hbpm_dosis"] = st.radio("Dosis de HBPM", ["Profiláctica", "Terapéutica"], key="hbpm_dosis", horizontal=True)
if "warfarina" in claves_elegidas or "acenocumarol" in claves_elegidas:
    with col_extra2:
        detalles["inr_actual"] = st.number_input("INR actual (si disponible)", min_value=0.0, max_value=10.0, step=0.1, format="%.1f", value=0.0, key="inr_actual_input")

naco_seleccionados = bool(claves_elegidas & {"rivaroxaban", "apixaban", "edoxaban", "dabigatran"})
if naco_seleccionados:
    st.caption(f"ℹ️ Se usará el CrCl del panel lateral: **{crcl} mL/min**.")

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

# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------
st.subheader("Plan de manejo sugerido", divider="gray")

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

    filas = []
    for r in recomendaciones:
        fecha_susp = r.fecha_suspension(fecha_dt)
        fecha_rein = r.fecha_reinicio(fecha_dt)
        filas.append({
            "Fármaco": r.farmaco,
            "Acción": ("🚨 " if r.alerta_roja else ("✅ " if r.accion == "No suspender" else "⏸️ ")) + r.accion,
            "Suspender desde": fecha_susp.strftime("%d/%m/%Y %H:%M") if fecha_susp else "—",
            "Reiniciar desde": fecha_rein.strftime("%d/%m/%Y %H:%M") if fecha_rein else "—",
        })
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    st.caption("Detalle por fármaco")
    for r in recomendaciones:
        with st.expander(f"{r.farmaco} — {r.accion}"):
            st.caption(r.categoria)
            st.markdown(f"**Suspensión:** {r.detalle_suspension}")
            if r.detalle_reinicio:
                st.markdown(f"**Reinicio:** {r.detalle_reinicio}")
            for nota in r.notas:
                st.markdown(f"ℹ️ {nota}")

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
    st.subheader("Informe / Exportar plan", divider="gray")
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
