"""
Motor de reglas clínicas para el manejo perioperatorio de antiagregantes y
anticoagulantes en pacientes sometidos a procedimientos de Radiología
Intervencionista.

Fuente base: Society of Interventional Radiology (SIR) Consensus Guidelines
(2019) — Patel S. et al., J Vasc Interv Radiol.

Este módulo es puramente declarativo/funcional (sin dependencias de UI) para
poder testearse y mantenerse de forma aislada del código de Streamlit.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

FUENTE = "Society of Interventional Radiology (SIR) Consensus Guidelines (2019)"

RIESGO_BAJO = "Bajo riesgo"
RIESGO_ALTO = "Alto riesgo"

PROCEDIMIENTOS = {
    RIESGO_BAJO: [
        "Accesos venosos (CVC, PICC, Port-a-Cath)",
        "Drenaje de colecciones superficiales o abscesos",
        "Biopsias superficiales (Tiroides, ganglios linfáticos, mama)",
        "Toracentesis",
        "Paracentesis",
        "Inyecciones articulares",
    ],
    RIESGO_ALTO: [
        "Biopsia de órgano sólido (Hígado, Riñón, Bazo, Pulmón)",
        "Intervención biliar (DPT, colecistostomía)",
        "Nefrostomía percutánea",
        "Ablación tumoral (Radiofrecuencia, Microondas, Crioablación)",
        "TIPS (Derivación portosistémica intrahepática transyugular)",
        "Drenaje intraabdominal complejo",
    ],
}


def procedimiento_a_riesgo(nombre_procedimiento):
    for riesgo, lista in PROCEDIMIENTOS.items():
        if nombre_procedimiento in lista:
            return riesgo
    return None


@dataclass
class Recomendacion:
    farmaco: str
    categoria: str
    accion: str  # "No suspender" | "Suspender" | "ALERTA ROJA"
    detalle_suspension: str
    horas_suspension_max: Optional[float] = None  # para cálculo de fecha (límite más conservador)
    detalle_reinicio: str = ""
    horas_reinicio: Optional[float] = None
    notas: list = field(default_factory=list)
    alerta_roja: bool = False

    def fecha_suspension(self, fecha_procedimiento: datetime):
        if self.horas_suspension_max is None:
            return None
        return fecha_procedimiento - timedelta(hours=self.horas_suspension_max)

    def fecha_reinicio(self, fecha_procedimiento: datetime):
        if self.horas_reinicio is None:
            return None
        return fecha_procedimiento + timedelta(hours=self.horas_reinicio)


def _reinicio_general(riesgo):
    if riesgo == RIESGO_BAJO:
        return "Reiniciar a las 24 horas si hay hemostasia adecuada.", 24.0
    return "Reiniciar a las 48 a 72 horas (según evaluación clínica y hemostasia).", 72.0


def evaluar_aspirina(riesgo):
    reinicio_txt, reinicio_h = _reinicio_general(riesgo)
    if riesgo == RIESGO_BAJO:
        return Recomendacion(
            farmaco="Aspirina (AAS)",
            categoria="Antiagregante plaquetario",
            accion="No suspender",
            detalle_suspension="No requiere suspensión en procedimientos de bajo riesgo de sangrado.",
            horas_suspension_max=None,
            detalle_reinicio=reinicio_txt,
            horas_reinicio=reinicio_h,
        )
    return Recomendacion(
        farmaco="Aspirina (AAS)",
        categoria="Antiagregante plaquetario",
        accion="Suspender",
        detalle_suspension="Suspender 5 días antes del procedimiento.",
        horas_suspension_max=5 * 24,
        detalle_reinicio=reinicio_txt,
        horas_reinicio=reinicio_h,
    )


def evaluar_p2y12(riesgo, farmaco="Clopidogrel"):
    reinicio_txt, reinicio_h = _reinicio_general(riesgo)
    return Recomendacion(
        farmaco=farmaco,
        categoria="Antiagregante plaquetario (inhibidor P2Y12)",
        accion="Suspender",
        detalle_suspension="Suspender 5 días antes del procedimiento (Riesgo Bajo y Alto).",
        horas_suspension_max=5 * 24,
        detalle_reinicio=reinicio_txt,
        horas_reinicio=reinicio_h,
        notas=[
            "Si el paciente tiene un stent coronario reciente (doble antiagregación), "
            "considerar interconsulta con Cardiología antes de suspender."
        ],
    )


def evaluar_avk(riesgo, farmaco="Warfarina", inr_actual=None):
    reinicio_txt, reinicio_h = _reinicio_general(riesgo)
    if riesgo == RIESGO_BAJO:
        detalle = "Suspender 3 a 5 días antes. Objetivo de INR: < 2.0."
        objetivo_txt = "< 2.0"
        objetivo_val = 2.0
        horas_max = 5 * 24
    else:
        detalle = "Suspender 5 días antes. Objetivo de INR: ≤ 1.5."
        objetivo_txt = "≤ 1.5"
        objetivo_val = 1.5
        horas_max = 5 * 24

    notas = ["Siempre requiere control de INR previo al procedimiento."]
    if inr_actual is not None:
        cumple = inr_actual <= objetivo_val
        notas.append(
            f"INR informado: {inr_actual:.1f} (objetivo {objetivo_txt}) — "
            + ("cumple objetivo." if cumple else "NO cumple objetivo; considerar posponer o revertir.")
        )

    return Recomendacion(
        farmaco=farmaco,
        categoria="Anticoagulante oral Anti-Vitamina K",
        accion="Suspender",
        detalle_suspension=detalle,
        horas_suspension_max=horas_max,
        detalle_reinicio=reinicio_txt,
        horas_reinicio=reinicio_h,
        notas=notas,
    )


def evaluar_hbpm(dosis, riesgo):
    """dosis: 'Profiláctica' | 'Terapéutica' (igual para Riesgo Bajo y Alto)."""
    reinicio_txt, reinicio_h = _reinicio_general(riesgo)
    notas = []
    if dosis == "Profiláctica":
        horas = 12.0
        detalle = "Suspender 12 horas antes (dosis profiláctica; aplica a Riesgo Bajo y Alto)."
        if riesgo == RIESGO_ALTO:
            notas.append(
                "Puede reiniciarse dosis profiláctica a las 12-24 h tras el procedimiento de "
                "alto riesgo si el paciente está inmovilizado (profilaxis de TVP)."
            )
    else:
        horas = 24.0
        detalle = "Suspender 24 horas antes (dosis terapéutica; aplica a Riesgo Bajo y Alto)."

    return Recomendacion(
        farmaco=f"Heparina de Bajo Peso Molecular ({dosis})",
        categoria="Heparina",
        accion="Suspender",
        detalle_suspension=detalle,
        horas_suspension_max=horas,
        detalle_reinicio=reinicio_txt,
        horas_reinicio=reinicio_h,
        notas=notas,
    )


def evaluar_hnf():
    return Recomendacion(
        farmaco="Heparina No Fraccionada (IV)",
        categoria="Heparina",
        accion="Suspender",
        detalle_suspension="Suspender 2 a 4 horas antes. Verificar aPTT normal antes del procedimiento.",
        horas_suspension_max=4.0,
        detalle_reinicio="Reiniciar según evaluación clínica y hemostasia (ver regla general por riesgo).",
        horas_reinicio=None,
        notas=["Requiere verificación de aPTT normal previo al procedimiento."],
    )


def evaluar_naco_xa(farmaco, riesgo, crcl):
    """Rivaroxaban / Apixaban / Edoxaban."""
    reinicio_txt, reinicio_h = _reinicio_general(riesgo)
    crcl_alterado = crcl < 30
    if not crcl_alterado:
        if riesgo == RIESGO_BAJO:
            horas, texto_omitir = 24.0, "omitir 1 dosis diaria o 2 dosis cada 12h"
        else:
            horas, texto_omitir = 48.0, None
        detalle = f"CrCl > 30 mL/min. Suspender {int(horas)} horas antes"
        detalle += f" ({texto_omitir})." if texto_omitir else "."
    else:
        horas = 48.0 if riesgo == RIESGO_BAJO else 72.0
        detalle = f"CrCl < 30 mL/min (alterado). Suspender {int(horas)} horas antes."

    return Recomendacion(
        farmaco=farmaco,
        categoria="Nuevo Anticoagulante Oral (NACO / DOAC) — inhibidor del Factor Xa",
        accion="Suspender",
        detalle_suspension=detalle,
        horas_suspension_max=horas,
        detalle_reinicio=reinicio_txt,
        horas_reinicio=reinicio_h,
        notas=[f"Función renal: CrCl = {crcl:.0f} mL/min."],
    )


def evaluar_dabigatran(riesgo, crcl):
    reinicio_txt, reinicio_h = _reinicio_general(riesgo)
    if crcl < 30:
        return Recomendacion(
            farmaco="Dabigatrán",
            categoria="Nuevo Anticoagulante Oral (NACO / DOAC) — inhibidor directo de trombina",
            accion="ALERTA ROJA",
            detalle_suspension=(
                "CrCl < 30 mL/min: uso contraindicado o requiere consulta hematológica "
                "antes de definir manejo perioperatorio."
            ),
            horas_suspension_max=None,
            detalle_reinicio="Definir con Hematología según evaluación individual.",
            horas_reinicio=None,
            notas=["Se requiere interconsulta con Hematología antes de continuar."],
            alerta_roja=True,
        )
    if crcl > 50:
        if riesgo == RIESGO_BAJO:
            horas_min, horas_max = 24.0, 48.0
        else:
            horas_min, horas_max = 48.0, 72.0
    else:  # 30-50
        if riesgo == RIESGO_BAJO:
            horas_min, horas_max = 48.0, 72.0
        else:
            horas_min, horas_max = 72.0, 96.0

    banda_crcl = "> 50 mL/min" if crcl > 50 else "30 - 50 mL/min"
    detalle = f"CrCl {banda_crcl}. Suspender {int(horas_min)} a {int(horas_max)} horas antes."

    return Recomendacion(
        farmaco="Dabigatrán",
        categoria="Nuevo Anticoagulante Oral (NACO / DOAC) — inhibidor directo de trombina",
        accion="Suspender",
        detalle_suspension=detalle,
        horas_suspension_max=horas_max,
        detalle_reinicio=reinicio_txt,
        horas_reinicio=reinicio_h,
        notas=[f"Función renal: CrCl = {crcl:.0f} mL/min."],
    )


CATALOGO_FARMACOS = {
    "aspirina": {"label": "Aspirina (AAS)", "requiere_crcl": False},
    "clopidogrel": {"label": "Clopidogrel", "requiere_crcl": False},
    "prasugrel": {"label": "Prasugrel", "requiere_crcl": False},
    "ticagrelor": {"label": "Ticagrelor", "requiere_crcl": False},
    "warfarina": {"label": "Warfarina", "requiere_crcl": False},
    "acenocumarol": {"label": "Acenocumarol", "requiere_crcl": False},
    "hbpm": {"label": "Heparina de Bajo Peso Molecular (ej. Enoxaparina)", "requiere_crcl": False},
    "hnf": {"label": "Heparina No Fraccionada (IV)", "requiere_crcl": False},
    "rivaroxaban": {"label": "Rivaroxabán", "requiere_crcl": True},
    "apixaban": {"label": "Apixabán", "requiere_crcl": True},
    "edoxaban": {"label": "Edoxabán", "requiere_crcl": True},
    "dabigatran": {"label": "Dabigatrán", "requiere_crcl": True},
}


def calcular_crcl_cockcroft_gault(edad, peso_kg, creatinina_mg_dl, sexo):
    if creatinina_mg_dl <= 0 or edad <= 0 or peso_kg <= 0:
        return None
    factor = 0.85 if sexo == "Femenino" else 1.0
    return ((140 - edad) * peso_kg * factor) / (72 * creatinina_mg_dl)
