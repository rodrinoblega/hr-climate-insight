# HR Climate Insight - Contexto del Proyecto

## Qué es

Agente IA que analiza encuestas de clima laboral (Excel) y genera informes profesionales (DOCX) con gráficos. Enfoque LLM-first: el "criterio organizacional" está en el prompt, no en código complejo.

## Arquitectura

```
Excel → Filtro anonimato (n≥5) → Generar PNGs → LLM (GPT-4o-mini) → DOCX con gráficos
```

## Estructura de archivos

```
├── main.py                    # CLI principal, orquesta todo el flujo
├── config.py                  # Configuración, API keys, paths
├── prompts/
│   └── master_prompt.txt      # El "cerebro" - instrucciones al LLM
├── utils/
│   ├── excel_parser.py        # Leer Excel, detectar sector, preparar datos
│   ├── anonymity.py           # Filtro n≥5 (CRÍTICO - tolerancia cero)
│   ├── chart_generator.py     # Generar gráficos PNG con matplotlib
│   └── docx_generator.py      # Convertir Markdown + gráficos a DOCX
├── examples/
│   ├── test_survey.xlsx       # Encuesta de ejemplo (Wassington)
│   └── expected_output.docx   # Documento de referencia manual
├── output/                    # Archivos generados (en .gitignore)
└── data/input/                # Carpeta para encuestas de usuarios
```

## Flujo detallado

1. **Cargar Excel** (`excel_parser.py`): Lee con pandas
2. **Detectar sector** (`excel_parser.py`): Busca columna de área/departamento
3. **Filtro anonimato** (`anonymity.py`): Excluye segmentos con <5 respuestas
4. **Generar gráficos** (`chart_generator.py`): Crea PNGs para preguntas clave
5. **Construir prompt** (`main.py` + `master_prompt.txt`): Incluye datos CSV, lista de gráficos, instrucciones
6. **Llamar LLM** (`main.py`): GPT-4o-mini genera Markdown con marcadores [GRAFICO: N]
7. **Generar DOCX** (`docx_generator.py`): Parsea Markdown, inserta imágenes donde hay marcadores

## Cómo ejecutar

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# Generar informe
python main.py -i examples/test_survey.xlsx -e "Wassington" -p "Argentina" -c "Buenos Aires"

# Sin gráficos
python main.py -i survey.xlsx -e "Empresa" -p "País" -c "Ciudad" --no-charts
```

## Decisiones de diseño

1. **LLM-first**: El LLM detecta dimensiones dinámicamente desde las preguntas, no hay estructura fija de 7 dimensiones
2. **Anonimato hardcodeado**: Umbral n≥5 en código, no configurable (tolerancia cero)
3. **Gráficos con palabras clave**: El LLM escribe `[GRAFICO: palabra_clave]` (ej: orgullo, liderazgo) y el código hace búsqueda directa por keyword. Las keywords se generan una sola vez en `generate_all_charts()` y se usan tanto para el summary del LLM como para la inserción - no hay patrones duplicados.
4. **Adaptación cultural**: El prompt adapta "vos/tú/você" según el país
5. **Markdown intermedio**: LLM genera Markdown, luego se convierte a DOCX (más fácil de debuggear)

## Estado actual

- ✅ Carga de Excel y detección de sector
- ✅ Filtro de anonimato funcionando
- ✅ Generación de gráficos PNG con matplotlib
- ✅ Integración de gráficos en DOCX via marcadores
- ✅ Análisis dinámico de dimensiones
- ✅ CLI con argparse

## Configuración

Variables de entorno (`.env`):
- `OPENAI_API_KEY`: API key de OpenAI (requerido)
- `OPENAI_MODEL`: Modelo a usar (default: gpt-4o-mini)

## Documentación original

Ver `docs/CONTEXTO_COMPLETO_PARA_CLAUDE_CODE.txt` para el contexto inicial del proyecto y decisiones de arquitectura detalladas.
