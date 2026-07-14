# Anticoagulación en Radiología Intervencionista (ANTICOAG-RI)

Aplicación web (Streamlit) de apoyo a la decisión clínica para el manejo
perioperatorio de antiagregantes y anticoagulantes en pacientes programados
para procedimientos de Radiología Intervencionista.

**Fuente base:** Society of Interventional Radiology (SIR) Consensus
Guidelines (2019).

Este proyecto es independiente de la app "BI-RADS MAMA" (no la modifica ni
depende de ella).

## Funcionalidad

- Clasificación del procedimiento por riesgo de sangrado (lista predefinida
  o definición manual).
- Selección de la medicación actual del paciente: antiagregantes (AAS,
  Clopidogrel, Prasugrel, Ticagrelor), anti-vitamina K (Warfarina,
  Acenocumarol), heparinas (HBPM profiláctica/terapéutica, HNF) y NACOs/DOACs
  (Rivaroxabán, Apixabán, Edoxabán, Dabigatrán).
- Cálculo de aclaramiento de creatinina (Cockcroft-Gault) para ajustar la
  recomendación de los NACOs según función renal.
- Cálculo de INR a partir de datos de laboratorio (PT del paciente, PT
  control del laboratorio e ISI del reactivo) para pacientes con Warfarina
  o Acenocumarol.
- Generación automática de fechas sugeridas de suspensión y reinicio en
  base a la fecha programada del procedimiento.
- Alerta roja automática (Dabigatrán con CrCl < 30 mL/min → requiere
  interconsulta con Hematología).
- Exportación del plan de manejo como texto y como PDF descargable.
- Interfaz inmersiva tipo "glass" (fondo azul profundo, tarjetas
  translúcidas con blur), sin barra lateral: los selectores de paciente,
  procedimiento y fármacos viven en tarjetas flotantes superiores, y el
  plan de manejo se visualiza como una línea de tiempo horizontal con el
  Día 0 (procedimiento) como nodo central.

## Instalación

Se recomienda usar un entorno virtual (en Windows, si su carpeta de usuario
tiene una ruta muy larga, cree el entorno virtual en una ruta corta, por
ejemplo `C:\pyenvs\anticoag-ri`, para evitar el límite de longitud de ruta
de Windows con algunas dependencias).

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

Luego abra el navegador en `http://localhost:8501`.

## Estructura del proyecto

- `app.py` — Interfaz de usuario (Streamlit) y orquestación de la UI.
- `reglas.py` — Motor de reglas clínicas (puro Python, sin dependencias de
  UI), basado en las tablas de la guía SIR 2019. Contiene la lógica de
  clasificación de riesgo, evaluación por fármaco y cálculo de CrCl.
- `.streamlit/config.toml` — Tema visual de la aplicación.

## Aviso clínico

Esta herramienta es un apoyo a la decisión clínica. **No reemplaza el
juicio clínico individualizado**, los protocolos institucionales vigentes,
ni la interconsulta con Hematología/Cardiología cuando corresponda.
