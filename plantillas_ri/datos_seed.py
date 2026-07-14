"""Datos semilla (mock data) del Módulo de Plantillas de Radiología Intervencionista.

3 plantillas iniciales de procedimientos clásicos de RI general/corporal,
redactadas en formato de informe estructurado según lineamientos SIR / CIRSE.
"""

from .schema import CategoriaRI, PlantillaProcedimiento


PLANTILLAS: list[PlantillaProcedimiento] = [
    PlantillaProcedimiento(
        id="colecistostomia_percutanea",
        nombre="Colecistostomía Percutánea",
        categoria=CategoriaRI.NO_VASCULAR,
        guia_referencia="SIR Standards of Practice — Percutaneous Cholecystostomy (2010, rev.)",
        indicacion=(
            "Colecistitis aguda en paciente de alto riesgo quirúrgico / no candidato a "
            "colecistectomía [urgente/de entrada], con diagnóstico clínico-radiológico "
            "compatible ([hallazgos ecográficos/TC]). Falla de tratamiento médico conservador "
            "durante [número] horas."
        ),
        consentimiento=(
            "Se explicó al paciente/familiar/representante legal la indicación, técnica, "
            "beneficios esperados y riesgos del procedimiento (dolor, sangrado, infección, "
            "lesión de víscera adyacente, desplazamiento o migración del catéter, "
            "peritonitis biliar, necesidad de procedimiento adicional o quirúrgico). "
            "Se obtuvo consentimiento informado por escrito."
        ),
        tecnica=(
            "Bajo guía de [ecografía/TC] y técnica estéril habitual, con el paciente en "
            "posición [decúbito supino/oblicuo], se identifica la vesícula biliar distendida. "
            "Se administra anestesia local con lidocaína al [1%/2%] en piel y trayecto. "
            "Se realiza punción transhepática/transperitoneal de la vesícula biliar con aguja "
            "[calibre de aguja, ej. 18-19G] mediante técnica de [Seldinger/trócar], "
            "confirmando posición intraluminal con aspiración de bilis. "
            "Se coloca catéter de drenaje tipo pigtail autorretentivo [calibre de catéter, "
            "ej. 8-10 Fr], que se fija a piel y se conecta a bolsa colectora estéril."
        ),
        hallazgos=(
            "Vesícula biliar distendida, de paredes [engrosadas/edematosas], con contenido "
            "[bilis/lodo biliar/pus] en su interior. [Presencia/ausencia] de litiasis vesicular. "
            "No se identifica colección perivesicular libre en el trayecto abordado."
        ),
        resultado_tecnico=(
            "Colecistostomía percutánea realizada con éxito técnico. Se obtiene [volumen] mL de "
            "material [biliar/purulento] que se envía a cultivo. Catéter con adecuada posición "
            "intraluminal confirmada por [inyección de contraste/aspiración], funcionando con "
            "libre débito hacia el exterior."
        ),
        complicaciones_inmediatas=(
            "Procedimiento sin complicaciones inmediatas. Paciente hemodinámicamente estable "
            "durante y posterior al procedimiento. [Sin/con] evidencia de sangrado activo, "
            "bilioperitoneo o neumoperitoneo en control post-procedimiento."
        ),
        recomendaciones_post=(
            "Control clínico y de laboratorio (hemograma, función renal) en las próximas "
            "[horas]. Mantener catéter a bolsa colectora en drenaje libre, con registro de "
            "débito diario. Colangiografía de control a través del catéter en [número de "
            "semanas] semanas para evaluar permeabilidad de la vía biliar antes de retirar el "
            "catéter. Considerar colecistectomía diferida según evolución clínica y riesgo "
            "quirúrgico del paciente."
        ),
    ),
    PlantillaProcedimiento(
        id="tace",
        nombre="Quimioembolización Transarterial (TACE)",
        categoria=CategoriaRI.ONCOLOGICO,
        guia_referencia="CIRSE Standards of Practice on TACE (2021) / SIR",
        indicacion=(
            "Hepatocarcinoma [BCLC A/B] no candidato a tratamiento curativo (resección/"
            "trasplante/ablación), con lesión(es) hepática(s) de [tamaño] cm en segmento(s) "
            "[segmento hepático], función hepática [Child-Pugh A/B], discutido en comité "
            "multidisciplinario de tumores hepáticos."
        ),
        consentimiento=(
            "Se informó al paciente sobre finalidad paliativa/de control local del "
            "procedimiento, técnica, alternativas terapéuticas y riesgos (dolor, náuseas y "
            "fiebre —síndrome post-embolización—, lesión hepática/biliar, absceso hepático, "
            "embolización no deseada a órganos adyacentes, insuficiencia hepática, reacción al "
            "medio de contraste, sangrado en sitio de punción). Se obtuvo consentimiento "
            "informado por escrito."
        ),
        tecnica=(
            "Bajo anestesia [local con sedación/general] y técnica estéril, se realiza punción "
            "de arteria femoral/radial [derecha/izquierda] con técnica de Seldinger, "
            "colocando introductor [calibre de introductor, ej. 5 Fr]. Se realiza arteriografía "
            "diagnóstica del tronco celíaco y arteria mesentérica superior con catéter "
            "[tipo de catéter]. Se cateteriza selectivamente/superselectivamente la(s) "
            "arteria(s) nutricia(s) del tumor con microcatéter [calibre de microcatéter, ej. "
            "2.4-2.8 Fr] guiado por roadmap. Se administra emulsión de quimioembolización "
            "([lipiodol + doxorrubicina/microesferas cargadas con fármaco, dosis]) bajo "
            "control fluoroscópico hasta [estasis/reducción del flujo] arterial tumoral."
        ),
        hallazgos=(
            "Arteriografía hepática que evidencia lesión(es) hipervascular(es) en "
            "[localización hepática] de [tamaño] cm, con [patrón de neovascularización/"
            "tinción tumoral] característico de hepatocarcinoma. [Presencia/ausencia] de "
            "shunt arteriovenoso o arterioportal significativo."
        ),
        resultado_tecnico=(
            "Quimioembolización transarterial realizada con éxito técnico, logrando "
            "devascularización [completa/parcial] del/los tumor(es) tratado(s) con "
            "estasis de flujo en la(s) arteria(s) nutricia(s). Sin evidencia de reflujo de "
            "material embolizante a territorio no deseado en el control angiográfico final."
        ),
        complicaciones_inmediatas=(
            "Procedimiento sin complicaciones inmediatas. Hemostasia adecuada en sitio de "
            "punción [manual/con dispositivo de cierre vascular]. Paciente estable "
            "hemodinámicamente al finalizar el procedimiento."
        ),
        recomendaciones_post=(
            "Reposo e inmovilización del miembro de punción según protocolo institucional "
            "([horas]). Control de laboratorio (hemograma, función hepática y renal) a las "
            "24-48 horas. Manejo del síndrome post-embolización (analgesia, antieméticos, "
            "hidratación). Tomografía/resonancia de control con contraste a las [4-6 semanas] "
            "para evaluar respuesta tumoral (criterios mRECIST). Reevaluación en comité "
            "multidisciplinario de tumores hepáticos según respuesta."
        ),
    ),
    PlantillaProcedimiento(
        id="nefrostomia_percutanea",
        nombre="Nefrostomía Percutánea",
        categoria=CategoriaRI.NO_VASCULAR,
        guia_referencia="SIR / CIRSE Standards of Practice — Percutaneous Nephrostomy",
        indicacion=(
            "Hidronefrosis [grado] secundaria a [causa: litiasis obstructiva/estenosis "
            "ureteral/compresión extrínseca tumoral] del riñón [derecho/izquierdo], con "
            "[deterioro de función renal/pionefrosis/urosepsis/dolor refractario] que motiva "
            "derivación urinaria percutánea."
        ),
        consentimiento=(
            "Se explicó al paciente/familiar/representante legal la indicación, técnica y "
            "riesgos del procedimiento (dolor, sangrado/hematuria, infección, lesión de "
            "estructuras adyacentes, fístula arteriovenosa, desplazamiento o migración del "
            "catéter, necesidad de recambio periódico). Se obtuvo consentimiento informado "
            "por escrito."
        ),
        tecnica=(
            "Bajo guía de [ecografía/fluoroscopia] combinada y técnica estéril, con el "
            "paciente en posición [prono/prono oblicuo], se identifica el sistema colector "
            "dilatado del riñón [derecho/izquierdo]. Se infiltra anestesia local con "
            "lidocaína al [1%/2%] en piel y trayecto. Se realiza punción de un cáliz "
            "[posterior/inferior] con aguja [calibre de aguja, ej. 18G] mediante técnica de "
            "[Seldinger/trócar], confirmando posición intracalicial con salida de orina "
            "y/o inyección de contraste diluido (pielografía anterógrada). Se dilata el "
            "trayecto de forma progresiva y se coloca catéter de nefrostomía tipo pigtail "
            "autorretentivo [calibre de catéter, ej. 8 Fr], fijado a piel y conectado a "
            "bolsa colectora estéril."
        ),
        hallazgos=(
            "Sistema colector renal [derecho/izquierdo] dilatado (hidronefrosis grado "
            "[I-IV]), con [presencia/ausencia] de imágenes de litiasis y/o defectos de "
            "relleno intraluminales en la pielografía anterógrada. Punto de obstrucción "
            "aparente a nivel de [ubicación: unión ureteropiélica/uréter proximal/medio/"
            "distal]."
        ),
        resultado_tecnico=(
            "Nefrostomía percutánea realizada con éxito técnico. Catéter con adecuada "
            "posición intracalicial confirmada por pielografía anterógrada, con drenaje "
            "inmediato de orina [clara/turbia/hemática] de [volumen] mL hacia bolsa colectora."
        ),
        complicaciones_inmediatas=(
            "Procedimiento sin complicaciones inmediatas. [Sin/con] hematuria macroscópica "
            "transitoria autolimitada. Paciente hemodinámicamente estable durante y posterior "
            "al procedimiento, sin signos de sangrado retroperitoneal en el control."
        ),
        recomendaciones_post=(
            "Control clínico y de laboratorio (hemograma, función renal, electrolitos) en las "
            "próximas [horas]. Mantener catéter a bolsa colectora en drenaje libre, con "
            "registro de débito horario/diario. Control de imagen (ecografía) para evaluar "
            "respuesta de la dilatación del sistema colector. Recambio programado del catéter "
            "cada [8-12 semanas] o antes si presenta disfunción. Evaluar tratamiento definitivo "
            "de la causa obstructiva por Urología según corresponda."
        ),
    ),
]


def obtener_por_id(plantilla_id: str) -> PlantillaProcedimiento | None:
    for plantilla in PLANTILLAS:
        if plantilla.id == plantilla_id:
            return plantilla
    return None


def por_categoria() -> dict:
    agrupadas: dict = {}
    for plantilla in PLANTILLAS:
        agrupadas.setdefault(plantilla.categoria, []).append(plantilla)
    return agrupadas
