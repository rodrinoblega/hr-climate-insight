# HR Climate Insight - Contexto del Proyecto

## Qué es

Aplicación web que analiza encuestas de clima laboral (Excel) y genera informes profesionales (DOCX) con gráficos. Enfoque LLM-first: el "criterio organizacional" está en el prompt, no en código complejo.

## Arquitectura

```
Excel → Filtro anonimato (n≥5) → Generar PNGs → LLM (7 llamadas) → DOCX con gráficos
```

### Generación por Secciones (Chunked Generation)

Para garantizar informes de **8,000+ palabras**, el sistema divide la generación en **7 llamadas secuenciales**:

| # | Sección | Palabras mín. |
|---|---------|---------------|
| 1 | Resumen Ejecutivo | 500 |
| 2 | Dimensiones 1-3 | 1,200 |
| 3 | Dimensiones 4-6 | 1,200 |
| 4 | Dimensiones restantes + Tabla | 800 |
| 5 | Evaluación Global | 500 |
| 6 | Plan de Acción | 700 |
| 7 | Conclusiones | 400 |

Cada sección pasa contexto a las siguientes (dimensiones ya analizadas, resumen de hallazgos).

## Estructura de archivos

```
├── app.py                     # Interfaz web (Streamlit) con branding Henear
├── main.py                    # CLI + orquestación de generación por secciones
├── config.py                  # Configuración, API keys, paths
├── prompts/
│   ├── system_prompt.txt      # Rol del consultor + ejemplo de profundidad
│   ├── user_template.txt      # Template del mensaje de usuario (legacy)
│   └── section_prompts.py     # 7 prompts para generación por secciones
├── utils/
│   ├── excel_parser.py        # Leer Excel, detectar sector, preparar datos
│   ├── anonymity.py           # Filtro n≥5 (CRÍTICO - tolerancia cero)
│   ├── chart_generator.py     # Generar gráficos PNG con matplotlib
│   └── docx_generator.py      # Convertir Markdown + gráficos a DOCX
├── assets/
│   └── logo.png               # Logo de Henear
├── .streamlit/
│   ├── config.toml            # Configuración de tema
│   └── secrets.toml           # Contraseña de acceso (en .gitignore)
├── docs/
│   ├── arquitectura_generacion_informes.md  # Documentación técnica
│   └── QUICK_START_CLAUDE_CODE.md
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
5. **Preparar fecha localizada** (`main.py`): Traduce mes según país (Febrero/February/Fevereiro)
6. **Generar por secciones** (`main.py` + `section_prompts.py`): 7 llamadas a la API
7. **Concatenar secciones**: Une todo el markdown generado
8. **Generar DOCX** (`docx_generator.py`): Parsea Markdown, inserta imágenes donde hay marcadores

## Cómo ejecutar

### Opción 1: Interfaz Web (Recomendado)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# Iniciar la aplicación web
./venv/bin/python -m streamlit run app.py

# Abrir http://localhost:8501
# Password: configurar en Streamlit Cloud Secrets
```

### Opción 2: CLI

```bash
# Generar informe
./venv/bin/python main.py -i examples/test_survey.xlsx -e "Wassington" -p "Argentina" -c "Buenos Aires"

# Sin gráficos
./venv/bin/python main.py -i survey.xlsx -e "Empresa" -p "País" -c "Ciudad" --no-charts
```

### Comandos útiles

```bash
# Cerrar la app
pkill -f "streamlit run"

# Levantar la app
./venv/bin/python -m streamlit run app.py
```

## Características de la Interfaz Web

### Branding Henear
- Logo de Henear en el header
- Colores corporativos (teal/cyan)

### Tema Oscuro/Claro
- Toggle con iconos 🌙/☀️
- Estilos CSS adaptativos
- Logo invertido en modo oscuro

### Idiomas
- Español (ES 🇪🇸) - por defecto
- Inglés (EN 🇬🇧)
- Traducciones completas de la interfaz

### Fecha Localizada
El sistema detecta el país y traduce la fecha:
- Argentina, México, España → **Febrero 2026**
- Brasil → **Fevereiro 2026**
- USA, UK → **February 2026**

## Estructura de Prompts

### `section_prompts.py`

Define las 7 secciones con:
- `id`: Identificador único
- `name`: Nombre descriptivo
- `min_words`: Palabras mínimas
- `prompt`: Instrucciones específicas con placeholders

Placeholders disponibles:
- `{empresa_nombre}`, `{pais}`, `{ciudad}`, `{fecha}`
- `{n_total}`, `{nota_anonimato}`
- `{graficos_disponibles}`, `{datos_csv}`
- `{dimensiones_previas}`, `{resumen_dimensiones}` (contexto entre secciones)

### Sistema de contexto entre secciones

```python
# Las secciones de dimensiones acumulan contexto
if section["id"].startswith("dimensiones"):
    dimensiones_previas += section_content
    # Extrae títulos y niveles de riesgo para resumen
```

## Decisiones de diseño

1. **Generación por secciones**: 7 llamadas en vez de 1 para garantizar profundidad
2. **LLM-first**: El LLM detecta dimensiones dinámicamente desde las preguntas
3. **Anonimato hardcodeado**: Umbral n≥5 en código, no configurable (tolerancia cero)
4. **Gráficos con palabras clave**: El LLM escribe `[GRAFICO: palabra_clave]`
5. **Adaptación cultural**: Adapta "vos/tú/você" según el país
6. **Fecha localizada**: Mes traducido automáticamente según país
7. **Markdown intermedio**: LLM genera Markdown, luego se convierte a DOCX

## Estado del proyecto

### Fase 1: Core Backend ✅ COMPLETADO
- ✅ Carga de Excel y detección de sector
- ✅ Filtro de anonimato funcionando
- ✅ Generación de gráficos PNG con matplotlib
- ✅ Integración de gráficos en DOCX via marcadores
- ✅ Análisis dinámico de dimensiones
- ✅ CLI con argparse

### Fase 2: Interfaz Web ✅ COMPLETADO
- ✅ Aplicación Streamlit (`app.py`)
- ✅ Formulario: upload Excel + campos (empresa, país, ciudad)
- ✅ Integración con backend existente
- ✅ Descarga de informe generado (.docx)
- ✅ Sistema de autenticación (contraseña simple)
- ✅ Manejo de errores y feedback al usuario
- ✅ Branding Henear (logo, colores)
- ✅ Tema oscuro/claro
- ✅ Soporte multilenguaje (ES/EN)

### Fase 2.5: Mejoras de Generación ✅ COMPLETADO
- ✅ Generación por secciones (7 llamadas API)
- ✅ Prompts especializados por sección
- ✅ Contexto entre secciones
- ✅ Fecha localizada por país
- ✅ Tabla resumen con datos reales

### Fase 3: Editor de Prompt 🔲 PENDIENTE
- 🔲 Pantalla para visualizar prompt actual
- 🔲 Editor de texto para modificar prompt
- 🔲 Guardar cambios del prompt
- 🔲 Botón "Restaurar prompt original"

### Fase 4: Testing y Entrega 🔲 PENDIENTE
- 🔲 Testing con múltiples encuestas
- 🔲 Ajustes y bugfixes
- 🔲 Documentación de uso
- 🔲 Deploy en servidor
- 🔲 Capacitación inicial

## Configuración

### Variables de entorno (`.env`):
- `OPENAI_API_KEY`: API key de OpenAI (requerido)
- `OPENAI_MODEL`: Modelo a usar (default: gpt-4o-mini)

### Streamlit secrets (`.streamlit/secrets.toml`):
- `password`: Contraseña de acceso a la web (configurar en Streamlit Secrets)

## Costos

- **API OpenAI por informe**: ~$0.01-0.02 USD (7 llamadas con gpt-4o-mini)
- **Tokens por informe**: ~24,500 tokens totales
- **Hosting**: Gratuito (Streamlit Cloud u otra plataforma)

## Notas para el cliente

- El cliente provee su propia API key de OpenAI
- El prompt puede ser personalizado (Fase 3 pendiente)
- El informe generado es un .docx totalmente editable
- Los informes tienen ~8,000-10,000 palabras de análisis profundo

## Documentación adicional

- `docs/arquitectura_generacion_informes.md`: Explicación técnica del chunking
- `docs/QUICK_START_CLAUDE_CODE.md`: Guía rápida

## Archivos auxiliares

- `generate_budget_pdf.py`: Script para generar el presupuesto en PDF
- `presupuesto_hr_climate_insight.pdf`: Presupuesto aprobado por el cliente
