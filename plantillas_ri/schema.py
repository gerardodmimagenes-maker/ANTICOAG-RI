"""Schema de datos para las plantillas de informes de Radiología Intervencionista.

Módulo 100% aislado: no importa nada de `app.py` ni de `reglas.py`, y nada
del resto de la aplicación importa de aquí salvo la página nueva
`pages/01_Plantillas_RI.py`.
"""

from dataclasses import dataclass, field
from enum import Enum
import re

_PLACEHOLDER_RE = re.compile(r"\[([^\]]+)\]")


class CategoriaRI(str, Enum):
    ONCOLOGICO = "Oncológico"
    NO_VASCULAR = "No vascular"
    VASCULAR_PERIFERICO = "Vascular periférico"


@dataclass
class PlantillaProcedimiento:
    """Plantilla de informe estructurado para un procedimiento de RI.

    Los campos de texto (indicacion, tecnica, etc.) pueden contener
    placeholders con la sintaxis [nombre del dato], que se detectan
    automáticamente para armar el formulario de completado rápido.
    """

    id: str
    nombre: str
    categoria: CategoriaRI
    guia_referencia: str

    indicacion: str
    consentimiento: str
    tecnica: str
    hallazgos: str
    resultado_tecnico: str
    complicaciones_inmediatas: str
    recomendaciones_post: str

    _campos_orden: tuple = field(
        default=(
            ("Indicación", "indicacion"),
            ("Consentimiento informado", "consentimiento"),
            ("Técnica / Procedimiento", "tecnica"),
            ("Hallazgos", "hallazgos"),
            ("Resultado técnico", "resultado_tecnico"),
            ("Complicaciones inmediatas", "complicaciones_inmediatas"),
            ("Recomendaciones post-procedimiento", "recomendaciones_post"),
        ),
        repr=False,
        compare=False,
    )

    def campos(self):
        """Devuelve [(titulo_seccion, texto_campo), ...] en el orden del informe."""
        return [(titulo, getattr(self, atributo)) for titulo, atributo in self._campos_orden]

    def placeholders(self) -> list:
        """Extrae los [placeholders] únicos de todos los campos, en orden de aparición."""
        vistos, orden = set(), []
        for _, texto in self.campos():
            for m in _PLACEHOLDER_RE.findall(texto):
                if m not in vistos:
                    vistos.add(m)
                    orden.append(m)
        return orden

    def texto_completo(self, valores: dict | None = None) -> str:
        """Renderiza el informe completo, reemplazando placeholders si se dan `valores`."""
        valores = valores or {}
        partes = [f"{self.nombre.upper()}", f"(Ref.: {self.guia_referencia})", ""]
        for titulo, texto in self.campos():
            partes.append(titulo.upper())
            partes.append(_reemplazar_placeholders(texto, valores))
            partes.append("")
        return "\n".join(partes).strip() + "\n"


def _reemplazar_placeholders(texto: str, valores: dict) -> str:
    def _sub(match):
        clave = match.group(1)
        valor = valores.get(clave)
        return valor if valor else match.group(0)

    return _PLACEHOLDER_RE.sub(_sub, texto)
