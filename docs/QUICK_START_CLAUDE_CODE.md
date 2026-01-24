# QUICK START PARA CLAUDE CODE

## Objetivo
Implementar Pre-MVP de agente IA para análisis de clima laboral.

## Contexto en 3 Puntos

1. **Qué hace**: Lee Excel de encuesta → Genera informe DOCX profesional (~20 páginas)
2. **Cómo**: LLM (GPT-4o-mini) hace el análisis, Python maneja I/O y anonimato
3. **Por qué simple**: Validar viabilidad rápido (2 días vs 4 semanas)

## Archivos de Referencia Disponibles

```
/mnt/project/
├── Encuesta_de_clima_laboral_2025_Wassington.xlsx  ← Test case
├── Ana_lisis_de_resultados...docx                   ← Output esperado
├── Specification                                     ← Spec completa
└── 3_3-Plantilla-encuesta-clima-laboral.pdf        ← Referencia
```

## Estructura a Crear

```
proyecto/
├── main.py                 # CLI principal
├── config.py              # Config (API keys)
├── requirements.txt       # pandas, openai, python-docx, openpyxl
├── prompts/
│   └── master_prompt.txt  # El corazón del sistema
├── utils/
│   ├── excel_parser.py    # Lee Excel
│   ├── anonymity.py       # Filtra n≥5 (CRÍTICO)
│   └── docx_generator.py  # Markdown → DOCX
├── data/input/            # Aquí van los Excels
└── output/                # Aquí salen los DOCXs
```

## Código Total Estimado
~250 líneas de Python + prompt (~500 líneas)

## Flujo de Ejecución

```bash
python main.py --input data/input/wassington.xlsx \
               --empresa "Wassington" \
               --pais "Argentina" \
               --ciudad "Buenos Aires"
```

→ Genera `output/informe_wassington_2025.docx` en ~30 segundos

## Reglas Críticas (Tolerancia CERO)

1. **Anonimato**: Filtro hardcoded n≥5 ANTES de LLM
2. **No punitivo**: Lenguaje constructivo siempre
3. **Revisión humana**: Output es para revisar, no auto-enviar

## Test Case de Validación

**Input**: Encuesta_de_clima_laboral_2025_Wassington.xlsx
- 45 respuestas, 4 sectores
- Problema conocido: "Áreas varias" tiene n=4 → debe excluirse

**Output esperado**: Similar a Ana_lisis_de_resultados...docx
- ~10,000 palabras
- 8 secciones temáticas
- Tabla resumen
- Plan de acción

## Costos
- Por informe: $0.002 (GPT-4o-mini)
- Por mes (50 informes): $0.12

## Criterio de Éxito Pre-MVP

✅ Genera informe comparable al manual
✅ Respeta anonimato
✅ Toma <1 minuto
✅ Output editable en Word
✅ README claro para usar

## Siguiente Acción
Leer CONTEXTO_COMPLETO_PARA_CLAUDE_CODE.txt para detalles técnicos completos.
