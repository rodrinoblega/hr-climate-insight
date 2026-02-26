"""
Section-based prompts for chunked report generation.
Each section is generated separately to ensure sufficient depth and length.
"""

# Base system prompt with consultant role and depth example
SYSTEM_PROMPT_BASE = """Eres un consultor senior de clima organizacional con 15 años de experiencia. Tu especialidad es transformar datos de encuestas en insights estratégicos profundos.

Tu enfoque es:
- PREVENTIVO: identificas riesgos antes de que escalen
- ÉTICO: proteges el anonimato (nunca análisis con n<5)
- CONSTRUCTIVO: presentas oportunidades, nunca señalas culpables
- PROFESIONAL PERO CÁLIDO: cercano sin perder rigor técnico

INSTRUCCIÓN CRÍTICA: Los clientes pagan por análisis PROFUNDOS. Cada sección debe incluir:
- Datos exactos desglosados (no solo promedios)
- Comparaciones entre sectores/segmentos
- Interpretación profunda de qué significan los números
- Implicaciones estratégicas

=== EJEMPLO DE PROFUNDIDAD ESPERADA ===

Este es el nivel de detalle que debes usar en CADA análisis:

"La disposición a recomendar Wassington como lugar de trabajo muestra resultados muy positivos: 38 colaboradores (84%) respondieron afirmativamente, 7 (16%) indicaron 'Tal vez', y ninguno respondió negativamente. Este indicador, conocido como eNPS interno, refleja un alto nivel de satisfacción y compromiso.

Al analizar por sector, Comercial lidera con 88% de recomendación, seguido por Administración (82%) y Producción (77%). Esta diferencia de 11 puntos porcentuales entre Comercial y Producción merece atención, aunque todos los sectores se mantienen en niveles saludables.

La alta disposición a recomendar correlaciona directamente con el orgullo de pertenencia (93% con puntajes 4-5) y la baja intención de rotación (solo 2% cambiaría de trabajo). Estos tres indicadores en conjunto evidencian una propuesta de valor empleador sólida que trasciende lo puramente económico.

Las implicaciones estratégicas son significativas: este nivel de advocacy interno puede aprovecharse para programas de referidos de talento, reduciendo costos de reclutamiento. Sin embargo, la brecha con Producción sugiere la necesidad de fortalecer la comunicación del propósito organizacional en el área operativa."

=== FIN DEL EJEMPLO ===

REGLAS:
- Genera SOLO la sección solicitada, no otras
- Usa formato Markdown
- Adapta el lenguaje según el país (vos/tú/você)
- Incluye marcadores [GRAFICO: palabra_clave] donde corresponda
"""

# Section definitions with specific prompts
SECTIONS = [
    {
        "id": "resumen_ejecutivo",
        "name": "Resumen Ejecutivo",
        "min_words": 500,
        "prompt": """Genera ÚNICAMENTE el Resumen Ejecutivo del informe de clima laboral.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- País: {pais}
- Ciudad: {ciudad}
- Fecha: {fecha}
- Total respuestas: {n_total}
{nota_anonimato}

DATOS CSV:
```
{datos_csv}
```

ESTRUCTURA REQUERIDA:

# Informe de Clima Laboral
# {empresa_nombre}

**Consultora:** [Consultora de Clima Organizacional]
**Destinatario:** Dirección General de {empresa_nombre}
**Fecha:** {fecha}

---

## Resumen Ejecutivo

[Escribe MÍNIMO 500 PALABRAS organizadas en 4-5 párrafos que incluyan:]

**Párrafo 1 - Contexto:**
- Propósito de la encuesta
- Metodología: cantidad de respuestas, sectores participantes
- Tasa de participación si se puede inferir

**Párrafo 2 - Hallazgos positivos:**
- Las 3-4 fortalezas principales CON DATOS ESPECÍFICOS
- Ejemplo: "El 93% de los colaboradores expresó alto orgullo de pertenencia (puntuaciones 4-5)"
- Comparaciones entre sectores si hay diferencias notables

**Párrafo 3 - Áreas de oportunidad:**
- Las 2-3 áreas que requieren atención CON DATOS ESPECÍFICOS
- Ejemplo: "Solo el 45% considera que la remuneración es equitativa respecto al mercado"
- Sin ser alarmista, presentar como oportunidades de mejora

**Párrafo 4 - Síntesis y próximos pasos:**
- Evaluación general del clima (saludable/atención/crítico)
- Mención de las dimensiones que se analizarán en detalle
- Nota sobre exclusiones de anonimato si las hubo

IMPORTANTE:
- NO incluyas otras secciones, SOLO el Resumen Ejecutivo
- Usa datos ESPECÍFICOS del CSV, no generalidades
- Mínimo 500 palabras
"""
    },
    {
        "id": "dimensiones_1_3",
        "name": "Dimensiones 1-3",
        "min_words": 1200,
        "prompt": """Genera ÚNICAMENTE las primeras 3 dimensiones del análisis.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- País: {pais}
- Ciudad: {ciudad}
- Fecha: {fecha}
- Total respuestas: {n_total}

GRÁFICOS DISPONIBLES:
{graficos_disponibles}

DATOS CSV:
```
{datos_csv}
```

INSTRUCCIONES:
1. Analiza las preguntas del CSV e identifica las dimensiones que cubre
2. Genera las PRIMERAS 3 dimensiones (típicamente: Compromiso/Pertenencia, Equidad/Trato, Compensación/Beneficios o similares según las preguntas)

ESTRUCTURA PARA CADA DIMENSIÓN (mínimo 400 palabras cada una):

---

## Dimensiones Analizadas

### 1. [Nombre de la Dimensión]

[Párrafo introductorio: qué mide esta dimensión, qué preguntas la componen, por qué es importante]

**Resultados detallados:**

**[Pregunta 1 resumida]:**
- Distribución exacta: X respondieron [opción A] (X%), Y respondieron [opción B] (Y%)
- Promedio: X.XX/5.0 (si aplica)
- Por sector: Administración (X%), Comercial (Y%), Producción (Z%)

**[Pregunta 2 resumida]:**
- [Mismo nivel de detalle]

[GRAFICO: palabra_clave] (si hay gráfico relevante disponible)

**Análisis interpretativo:**

[2-3 párrafos que incluyan:]
- Qué significan estos números para la organización
- Patrones o diferencias entre segmentos y posibles causas
- Implicaciones estratégicas
- Conexión con otras dimensiones si es relevante

**Nivel de riesgo:** 🟢 Saludable / 🟡 Atención / 🔴 Crítico - [Justificación basada en datos]

---

### 2. [Segunda Dimensión]
[Mismo formato detallado]

---

### 3. [Tercera Dimensión]
[Mismo formato detallado]

---

IMPORTANTE:
- NO incluyas el Resumen Ejecutivo ni otras secciones
- SOLO las dimensiones 1, 2 y 3
- Mínimo 1200 palabras en total (400+ por dimensión)
- Usa datos ESPECÍFICOS del CSV
- Incluye 1-2 marcadores [GRAFICO: x] si hay gráficos relevantes
"""
    },
    {
        "id": "dimensiones_4_6",
        "name": "Dimensiones 4-6",
        "min_words": 1200,
        "prompt": """Genera ÚNICAMENTE las dimensiones 4, 5 y 6 del análisis.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- País: {pais}
- Total respuestas: {n_total}

GRÁFICOS DISPONIBLES:
{graficos_disponibles}

CONTEXTO - Dimensiones ya analizadas:
{dimensiones_previas}

DATOS CSV:
```
{datos_csv}
```

INSTRUCCIONES:
1. Revisa qué dimensiones YA fueron analizadas (arriba)
2. Identifica las siguientes 3 dimensiones que NO han sido cubiertas
3. Típicamente serían: Herramientas/Recursos, Comunicación, Liderazgo, Trabajo en equipo, Desarrollo profesional, etc.

ESTRUCTURA PARA CADA DIMENSIÓN (mínimo 400 palabras cada una):

### 4. [Nombre de la Dimensión]

[Párrafo introductorio: qué mide, qué preguntas incluye, importancia]

**Resultados detallados:**

**[Pregunta resumida]:**
- Distribución: X respondieron [opción] (X%), Y respondieron [opción] (Y%)
- Por sector: [desglose]

[GRAFICO: palabra_clave] (si aplica)

**Análisis interpretativo:**
[2-3 párrafos profundos sobre significado, patrones, implicaciones]

**Nivel de riesgo:** [emoji] [nivel] - [justificación]

---

### 5. [Quinta Dimensión]
[Mismo formato]

---

### 6. [Sexta Dimensión]
[Mismo formato]

---

IMPORTANTE:
- NO repitas dimensiones ya analizadas
- NO incluyas otras secciones del informe
- SOLO dimensiones 4, 5 y 6
- Mínimo 1200 palabras (400+ por dimensión)
- Incluye 1-2 marcadores [GRAFICO: x] si hay gráficos relevantes
"""
    },
    {
        "id": "dimensiones_restantes_tabla",
        "name": "Dimensiones Restantes y Tabla Resumen",
        "min_words": 800,
        "prompt": """Genera las dimensiones restantes (si las hay) y la Tabla Resumen.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- Total respuestas: {n_total}

GRÁFICOS DISPONIBLES:
{graficos_disponibles}

CONTEXTO - Dimensiones ya analizadas:
{dimensiones_previas}

RESUMEN DE RESULTADOS POR DIMENSIÓN:
{resumen_dimensiones}

DATOS CSV:
```
{datos_csv}
```

INSTRUCCIONES:
1. Si hay preguntas del CSV que NO han sido cubiertas en las 6 dimensiones anteriores, crea dimensiones adicionales (7, 8, etc.)
2. Luego genera la Tabla Resumen con TODAS las dimensiones analizadas

ESTRUCTURA:

### 7. [Dimensión adicional si aplica]
[Análisis con mismo formato: resultados detallados, análisis interpretativo, nivel de riesgo]

### 8. [Otra dimensión si aplica]
[...]

---

## Tabla Resumen

CRÍTICO: Debes generar una tabla Markdown COMPLETA con una fila por cada dimensión analizada (mínimo 6-8 filas). Copia EXACTAMENTE este formato:

=== EJEMPLO DE TABLA (COPIA ESTE FORMATO EXACTO) ===

| Dimensión | Resultado Principal | Nivel |
|-----------|---------------------|-------|
| 🏢 Compromiso y Pertenencia | 93% expresó alto orgullo (puntuaciones 4-5), promedio 4.56/5.0 | 🟢 |
| ⚖️ Equidad y Trato | 78% percibe trato justo, sector Producción más bajo (71%) | 🟢 |
| 💰 Compensación y Beneficios | Solo 45% considera remuneración equitativa al mercado | 🔴 |
| 🛠️ Herramientas y Recursos | 82% tiene herramientas adecuadas, oportunidad en tecnología | 🟢 |
| 📢 Comunicación Interna | 67% satisfecho con comunicación, brecha entre sectores | 🟡 |
| 👔 Liderazgo y Supervisión | 85% confía en su líder directo, promedio 4.2/5.0 | 🟢 |
| 👥 Trabajo en Equipo | 88% valora colaboración con compañeros | 🟢 |
| 📚 Desarrollo Profesional | 52% ve oportunidades de crecimiento, área de mejora | 🟡 |

=== FIN DEL EJEMPLO ===

Genera tu tabla con los DATOS REALES de esta encuesta, siguiendo exactamente el formato anterior.

---

**Leyenda:** 🏢 Compromiso | ⚖️ Equidad | 💰 Compensación | 📚 Desarrollo | 🛠️ Herramientas | 👥 Equipo | 📢 Comunicación | 👔 Liderazgo | 🎯 Dirección

**Clasificación de niveles:**
- 🟢 Saludable: promedio ≥ 4.0 o satisfacción ≥ 75%
- 🟡 Atención: promedio 3.0-3.9 o satisfacción 50-74%
- 🔴 Crítico: promedio < 3.0 o satisfacción < 50%

---

IMPORTANTE:
- La tabla DEBE tener entre 6 y 10 filas (una por cada dimensión analizada)
- Cada fila DEBE incluir un dato numérico específico (porcentaje o promedio)
- NO dejes la tabla vacía ni uses placeholders como "[Dato específico]"
- La leyenda de emojis DEBE aparecer después de la tabla
- Mínimo 800 palabras en total para esta sección
"""
    },
    {
        "id": "evaluacion_global",
        "name": "Evaluación Global",
        "min_words": 500,
        "prompt": """Genera ÚNICAMENTE la sección de Evaluación Global del Clima.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- País: {pais}
- Total respuestas: {n_total}

RESUMEN DE TODAS LAS DIMENSIONES ANALIZADAS:
{resumen_dimensiones}

DATOS CSV (para referencia):
```
{datos_csv}
```

ESTRUCTURA REQUERIDA:

## Evaluación Global del Clima

[Escribe 2-3 párrafos de síntesis integradora - MÍNIMO 300 PALABRAS]

El párrafo debe:
- Conectar las dimensiones entre sí (cómo se relacionan los hallazgos)
- Dar una visión holística del clima organizacional
- Identificar patrones transversales
- Evaluar el estado general (sin ser ni alarmista ni complaciente)

**Fortalezas destacadas:**

1. **[Fortaleza 1]:** [Descripción con datos específicos. Ejemplo: "El 93% de los colaboradores expresó alto orgullo de pertenencia, con el sector Comercial liderando con 96%. Esta fortaleza cultural actúa como factor protector ante la competencia por talento."]

2. **[Fortaleza 2]:** [Descripción con datos específicos]

3. **[Fortaleza 3]:** [Descripción con datos específicos]

**Oportunidades de mejora prioritarias:**

1. **[Oportunidad 1]:** [Descripción con datos específicos. Ejemplo: "Solo el 45% considera que la remuneración es equitativa. Esta percepción es más marcada en Producción (38%) que en Administración (52%), sugiriendo la necesidad de revisar la comunicación sobre compensación total."]

2. **[Oportunidad 2]:** [Descripción con datos específicos]

3. **[Oportunidad 3]:** [Descripción con datos específicos]

---

IMPORTANTE:
- NO incluyas otras secciones
- SOLO Evaluación Global con Fortalezas y Oportunidades
- Mínimo 500 palabras
- Basa TODO en los datos reales del resumen de dimensiones
"""
    },
    {
        "id": "plan_accion",
        "name": "Plan de Acción",
        "min_words": 700,
        "prompt": """Genera ÚNICAMENTE la sección del Plan de Acción Recomendado.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- País: {pais}

RESUMEN DE DIMENSIONES Y HALLAZGOS:
{resumen_dimensiones}

ESTRUCTURA REQUERIDA:

## Plan de Acción Recomendado

[Párrafo introductorio conectando el plan con los hallazgos - 50 palabras]

### Acciones Inmediatas (Próximos 3 meses)

**Para el equipo de RRHH:**

1. **[Nombre de la acción - relacionada con hallazgo específico]**
   - **Contexto:** [Por qué esta acción, basado en qué dato del informe]
   - **Objetivo:** [Qué se busca lograr, métrica específica]
   - **Actividades sugeridas:**
     - [Actividad 1]
     - [Actividad 2]
     - [Actividad 3]
   - **Indicador de éxito:** [Cómo medir, meta numérica]
   - **Timeline:** [Cuándo iniciar, cuándo evaluar]

2. **[Segunda acción para RRHH]**
   - [Mismo nivel de detalle]

**Para los líderes de equipo:**

1. **[Acción para líderes]**
   - **Contexto:** [Relacionado con hallazgo de liderazgo/comunicación]
   - **Objetivo:** [Meta específica]
   - **Actividades sugeridas:**
     - [Actividad 1]
     - [Actividad 2]
   - **Indicador de éxito:** [Medición]

2. **[Segunda acción para líderes]**
   - [Mismo detalle]

### Acciones de Mediano Plazo (3-6 meses)

**Para RRHH:**
- **[Acción]:** [Descripción detallada con objetivo e indicador]
- **[Acción]:** [Descripción detallada]

**Para Líderes:**
- **[Acción]:** [Descripción detallada]
- **[Acción]:** [Descripción detallada]

### Seguimiento y Medición (6-12 meses)

- **Pulse survey:** Recomendado para [mes] enfocado en [dimensiones críticas identificadas]
- **Indicadores a monitorear mensualmente:**
  - [Indicador 1]
  - [Indicador 2]
  - [Indicador 3]
- **Nueva encuesta completa:** Sugerida para [fecha, típicamente 12 meses después]

---

IMPORTANTE:
- NO incluyas otras secciones
- SOLO el Plan de Acción completo
- Las acciones deben ser ESPECÍFICAS y basadas en los hallazgos reales
- Mínimo 700 palabras
- Cada acción debe tener contexto, objetivo, actividades, indicador y timeline
"""
    },
    {
        "id": "conclusiones",
        "name": "Conclusiones",
        "min_words": 400,
        "prompt": """Genera ÚNICAMENTE la sección de Conclusiones del informe.

DATOS DE LA ENCUESTA:
- Empresa: {empresa_nombre}
- País: {pais}
- Total respuestas: {n_total}

RESUMEN DE DIMENSIONES Y HALLAZGOS:
{resumen_dimensiones}

ESTRUCTURA REQUERIDA:

## Conclusiones

[Escribe 4-5 párrafos - MÍNIMO 400 PALABRAS]

**Párrafo 1 - Síntesis del estado actual:**
- Evaluación balanceada del clima (ni alarmista ni complaciente)
- Mención de las principales fortalezas y oportunidades
- Contexto de la organización

**Párrafo 2 - Reconocimiento:**
- Agradecimiento genuino a los colaboradores por participar
- Valor de la honestidad en las respuestas
- Reconocimiento del esfuerzo de la organización por escuchar

**Párrafo 3 - Perspectiva constructiva:**
- Los resultados como punto de partida, no sentencia
- Potencial de mejora identificado
- Mensaje motivacional sin ser ingenuo

**Párrafo 4 - Próximos pasos:**
- Comunicación de resultados a los colaboradores
- Inicio del plan de acción
- Importancia del seguimiento

**Párrafo 5 - Cierre:**
- Invitación a mantener el diálogo abierto
- Compromiso de la consultora (si aplica)
- Mensaje final de optimismo fundamentado

---

**Nota final:**

Este informe fue elaborado siguiendo las mejores prácticas de análisis de clima organizacional, respetando estrictamente el anonimato de los participantes. Los datos han sido procesados de manera agregada y ningún resultado permite identificar respuestas individuales.

---

IMPORTANTE:
- NO incluyas otras secciones
- SOLO las Conclusiones
- Mínimo 400 palabras
- Tono cálido pero profesional
- Adapta el lenguaje según el país (vos/tú/você para {pais})
"""
    }
]


def get_section_prompt(section_id: str) -> dict:
    """Get a specific section by ID."""
    for section in SECTIONS:
        if section["id"] == section_id:
            return section
    return None


def get_all_sections() -> list:
    """Get all section definitions."""
    return SECTIONS
