# Arquitectura de Generación de Informes por Secciones

## Resumen Ejecutivo

Para garantizar informes de alta calidad con **8,000+ palabras** de análisis profundo, implementamos una arquitectura de **generación por secciones** que divide el informe en 7 llamadas independientes a la API de OpenAI.

---

## ¿Por qué este enfoque?

| Enfoque | Palabras generadas | Profundidad | Costo |
|---------|-------------------|-------------|-------|
| Una sola llamada | ~2,000 | Superficial | Bajo |
| **7 llamadas (implementado)** | **~8,000+** | **Profundo** | Medio |

Los modelos de lenguaje tienden a "resumir" cuando se les pide generar documentos muy largos en una sola llamada. Al dividir en secciones, cada llamada se enfoca en una parte específica con instrucciones detalladas.

---

## Estructura de las 7 Llamadas

```
┌─────────────────────────────────────────────────────────────────┐
│                    GENERACIÓN DEL INFORME                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Llamada 1: Resumen Ejecutivo (500+ palabras)                  │
│      ↓                                                          │
│  Llamada 2: Dimensiones 1-3 (1,200+ palabras)                  │
│      ↓ [pasa contexto de dimensiones previas]                  │
│  Llamada 3: Dimensiones 4-6 (1,200+ palabras)                  │
│      ↓ [pasa contexto de dimensiones previas]                  │
│  Llamada 4: Dimensiones Restantes + Tabla (800+ palabras)      │
│      ↓ [pasa resumen de todas las dimensiones]                 │
│  Llamada 5: Evaluación Global (500+ palabras)                  │
│      ↓                                                          │
│  Llamada 6: Plan de Acción (700+ palabras)                     │
│      ↓                                                          │
│  Llamada 7: Conclusiones (400+ palabras)                       │
│                                                                 │
│  ═══════════════════════════════════════════                   │
│  TOTAL MÍNIMO: ~5,300 palabras                                 │
│  TOTAL ESPERADO: ~8,000-10,000 palabras                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura JSON de los Prompts

Cada sección se define con la siguiente estructura:

```json
{
  "sections": [
    {
      "id": "resumen_ejecutivo",
      "name": "Resumen Ejecutivo",
      "min_words": 500,
      "max_tokens": 4000,
      "requires_context": false,
      "prompt": "Genera ÚNICAMENTE el Resumen Ejecutivo..."
    },
    {
      "id": "dimensiones_1_3",
      "name": "Dimensiones 1-3",
      "min_words": 1200,
      "max_tokens": 4000,
      "requires_context": false,
      "prompt": "Genera ÚNICAMENTE las primeras 3 dimensiones..."
    },
    {
      "id": "dimensiones_4_6",
      "name": "Dimensiones 4-6",
      "min_words": 1200,
      "max_tokens": 4000,
      "requires_context": true,
      "context_from": ["dimensiones_1_3"],
      "prompt": "Genera ÚNICAMENTE las dimensiones 4, 5 y 6...\n\nDimensiones ya analizadas:\n{dimensiones_previas}"
    },
    {
      "id": "dimensiones_restantes_tabla",
      "name": "Dimensiones Restantes y Tabla",
      "min_words": 800,
      "max_tokens": 4000,
      "requires_context": true,
      "context_from": ["dimensiones_1_3", "dimensiones_4_6"],
      "prompt": "Genera las dimensiones restantes y la tabla resumen..."
    },
    {
      "id": "evaluacion_global",
      "name": "Evaluación Global",
      "min_words": 500,
      "max_tokens": 4000,
      "requires_context": true,
      "context_from": ["resumen_dimensiones"],
      "prompt": "Genera ÚNICAMENTE la Evaluación Global..."
    },
    {
      "id": "plan_accion",
      "name": "Plan de Acción",
      "min_words": 700,
      "max_tokens": 4000,
      "requires_context": true,
      "context_from": ["resumen_dimensiones"],
      "prompt": "Genera ÚNICAMENTE el Plan de Acción..."
    },
    {
      "id": "conclusiones",
      "name": "Conclusiones",
      "min_words": 400,
      "max_tokens": 4000,
      "requires_context": true,
      "context_from": ["resumen_dimensiones"],
      "prompt": "Genera ÚNICAMENTE las Conclusiones..."
    }
  ]
}
```

---

## Variables Disponibles en Cada Prompt

Cada prompt tiene acceso a las siguientes variables:

```json
{
  "variables_base": {
    "empresa_nombre": "Nombre de la empresa",
    "pais": "País",
    "ciudad": "Ciudad",
    "fecha": "Febrero 2026",
    "n_total": 45,
    "nota_anonimato": "Información sobre exclusiones por anonimato",
    "graficos_disponibles": "Lista de gráficos generados",
    "datos_csv": "Datos de la encuesta en formato CSV"
  },
  "variables_contextuales": {
    "dimensiones_previas": "Contenido completo de dimensiones ya generadas",
    "resumen_dimensiones": "Resumen de hallazgos por dimensión"
  }
}
```

---

## Flujo de Ejecución

```
┌──────────────────┐
│   Usuario sube   │
│   archivo Excel  │
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Parseo de datos │
│  + Anonimización │
└────────┬─────────┘
         ▼
┌──────────────────┐
│   Generación de  │
│     gráficos     │
└────────┬─────────┘
         ▼
┌──────────────────────────────────────────┐
│         LOOP DE GENERACIÓN               │
│  ┌────────────────────────────────────┐  │
│  │  Para cada sección (1 a 7):       │  │
│  │                                    │  │
│  │  1. Formatear prompt con datos    │  │
│  │  2. Llamar API (max_tokens=4000)  │  │
│  │  3. Guardar contenido             │  │
│  │  4. Actualizar contexto           │  │
│  │  5. Log de progreso               │  │
│  └────────────────────────────────────┘  │
└────────┬─────────────────────────────────┘
         ▼
┌──────────────────┐
│  Concatenar las  │
│   7 secciones    │
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Generar DOCX    │
│  con gráficos    │
└────────┬─────────┘
         ▼
┌──────────────────┐
│    Descargar     │
│     informe      │
└──────────────────┘
```

---

## Ejemplo de Llamada a la API

Cada llamada se estructura así:

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "Eres un consultor senior de clima organizacional con 15 años de experiencia..."
    },
    {
      "role": "user",
      "content": "Genera ÚNICAMENTE el Resumen Ejecutivo del informe...\n\nDATOS DE LA ENCUESTA:\n- Empresa: Henear\n- País: Argentina\n...\n\nDATOS CSV:\n```\npregunta,opcion,cantidad,porcentaje\n...\n```"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 4000
}
```

---

## Estimación de Costos

Con el modelo `gpt-4o-mini`:

| Concepto | Estimación |
|----------|------------|
| Tokens de entrada (promedio por llamada) | ~2,000 |
| Tokens de salida (promedio por llamada) | ~1,500 |
| **Total por llamada** | ~3,500 tokens |
| **Total por informe (7 llamadas)** | ~24,500 tokens |
| **Costo aproximado por informe** | ~$0.01 - $0.02 USD |

*Nota: Los costos pueden variar según el tamaño de la encuesta y el modelo utilizado.*

---

## Manejo de Errores (Próxima Mejora)

Se planea implementar:

- **Reintentos automáticos**: 3 intentos por sección con espera exponencial
- **Progreso parcial**: Guardar secciones completadas antes de un fallo
- **Fallback**: Mensaje indicativo si una sección no pudo generarse

---

## Resumen

| Aspecto | Detalle |
|---------|---------|
| Cantidad de llamadas | 7 secuenciales |
| Palabras mínimas | ~5,300 |
| Palabras esperadas | ~8,000-10,000 |
| Tiempo estimado | 30-60 segundos |
| Costo por informe | ~$0.01-0.02 USD |
| Modelo recomendado | gpt-4o-mini |

---

*Documento técnico - HR Climate Insight by Henear*
