#!/usr/bin/env python3
"""
HR Climate Insight - Pre-MVP
Generates professional climate survey reports using LLM analysis.

Usage:
    python main.py --input survey.xlsx --empresa "Company Name" --pais "Country" --ciudad "City"
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

import config
from utils.excel_parser import (
    load_survey,
    detect_sector_column,
    get_survey_stats,
    prepare_data_for_llm,
    get_survey_summary,
)
from utils.anonymity import (
    apply_anonymity_filter,
    get_anonymity_summary,
)
from utils.docx_generator import markdown_to_docx, save_markdown
from utils.chart_generator import (
    generate_all_charts,
    get_chartable_questions_summary,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_report(
    input_file: str,
    empresa: str,
    pais: str,
    ciudad: str,
    output_dir: str | None = None,
    include_charts: bool = True,
) -> Path:
    """
    Generate a climate survey report from an Excel file.

    Args:
        input_file: Path to the Excel survey file
        empresa: Company name
        pais: Country
        ciudad: City
        output_dir: Output directory (default: ./output)
        include_charts: Whether to generate and include charts (default: True)

    Returns:
        Path to the generated DOCX file
    """
    # Validate configuration
    errors = config.validate_config()
    if errors:
        for error in errors:
            logger.error(error)
        raise ValueError("Configuration errors found. Please fix and retry.")

    output_dir = Path(output_dir) if output_dir else config.OUTPUT_DIR

    # Step 1: Load survey data
    logger.info(f"Loading survey from: {input_file}")
    df = load_survey(input_file)
    logger.info(f"Loaded {len(df)} responses with {len(df.columns)} questions")

    # Step 2: Detect sector column
    sector_column = detect_sector_column(df)
    if sector_column:
        logger.info(f"Detected sector column: {sector_column[:50]}...")
    else:
        logger.warning("No sector column detected. Skipping segment analysis.")

    # Step 3: Apply anonymity filter (CRITICAL)
    if sector_column:
        logger.info("Applying anonymity filter (n >= 5)...")
        filtered_df, exclusion_report = apply_anonymity_filter(df, sector_column)
        logger.info(get_anonymity_summary(exclusion_report))

        if len(filtered_df) == 0:
            raise ValueError("No data remaining after anonymity filter. Cannot generate report.")

        # Prepare anonymity note for prompt
        if exclusion_report['excluded_segments']:
            nota_anonimato = (
                f"NOTA SOBRE ANONIMATO:\n{exclusion_report['warning']}\n"
                f"Respuestas incluidas en el análisis: {exclusion_report['filtered_count']} de {exclusion_report['original_count']}"
            )
        else:
            nota_anonimato = "Todas las respuestas fueron incluidas (todos los segmentos cumplen n >= 5)."
    else:
        filtered_df = df
        nota_anonimato = "Análisis realizado sin segmentación por sector."

    # Step 4: Generate charts (if enabled)
    charts = {}
    charts_summary = ""
    max_charts = 15  # Limit number of charts

    if include_charts:
        logger.info("Generating charts for survey questions...")
        charts_dir = output_dir / "charts"
        charts = generate_all_charts(filtered_df, charts_dir, max_charts=max_charts)
        logger.info(f"Generated {len(charts)} charts")

        # Get summary for prompt using the SAME charts dict (ensures keyword consistency)
        charts_summary = get_chartable_questions_summary(charts)

    # Step 5: Prepare data for LLM
    logger.info("Preparing data for LLM analysis...")
    datos_csv = prepare_data_for_llm(filtered_df)

    # Step 6: Load and format prompt
    logger.info("Loading master prompt...")
    prompt_template = config.get_master_prompt()

    fecha = datetime.now().strftime("%B %Y")

    prompt = prompt_template.format(
        empresa_nombre=empresa,
        pais=pais,
        ciudad=ciudad,
        fecha=fecha,
        n_total=len(filtered_df),
        nota_anonimato=nota_anonimato,
        datos_csv=datos_csv,
    )

    # Add charts instructions if charts are enabled - BEFORE the main content
    if include_charts and charts_summary:
        charts_instruction = f"""

=== GRÁFICOS DISPONIBLES (USO OBLIGATORIO) ===

{charts_summary}

INSTRUCCIONES CRÍTICAS PARA GRÁFICOS:
1. DEBES usar entre 4 y 6 marcadores [GRAFICO: palabra_clave] en tu respuesta
2. Usa la palabra_clave EXACTA de la lista anterior (ej: orgullo, recomendar, liderazgo)
3. Coloca el marcador en una línea sola, seguido de un párrafo que analice ESE gráfico específico
4. IMPORTANTE: El texto después del gráfico debe hablar sobre LA MISMA pregunta del gráfico

Ejemplo CORRECTO:

[GRAFICO: orgullo]

Como se observa en el gráfico anterior, el nivel de orgullo de los colaboradores es alto, con un promedio de 4.6...

Ejemplo INCORRECTO (NO hacer esto):

[GRAFICO: orgullo]

Como se observa en el gráfico anterior, el 85% recomendaría la empresa...  ← ERROR: habla de recomendar, no de orgullo

=== FIN INSTRUCCIONES DE GRÁFICOS ===

"""
        # Insert charts instruction near the beginning of the prompt, after the header
        prompt = prompt.replace("REGLAS CRÍTICAS (NO NEGOCIABLES):",
                               charts_instruction + "REGLAS CRÍTICAS (NO NEGOCIABLES):")

    # Step 7: Call LLM
    logger.info(f"Calling OpenAI API ({config.OPENAI_MODEL})...")
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=16000,
    )

    markdown_content = response.choices[0].message.content
    logger.info(f"Received response: {len(markdown_content)} characters")

    # Log token usage
    usage = response.usage
    logger.info(f"Token usage - Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}, Total: {usage.total_tokens}")

    # Step 8: Generate outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    empresa_slug = empresa.lower().replace(" ", "_")

    # Save markdown (for debugging)
    md_path = output_dir / f"informe_{empresa_slug}_{timestamp}.md"
    save_markdown(markdown_content, md_path)
    logger.info(f"Saved Markdown: {md_path}")

    # Generate DOCX with charts
    docx_path = output_dir / f"informe_{empresa_slug}_{timestamp}.docx"
    markdown_to_docx(markdown_content, docx_path, charts=charts if include_charts else None)
    logger.info(f"Generated DOCX: {docx_path}")

    return docx_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate climate survey reports from Excel data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --input survey.xlsx --empresa "Wassington" --pais "Argentina" --ciudad "Buenos Aires"
    python main.py -i data/input/encuesta.xlsx -e "Mi Empresa" -p "México" -c "CDMX"
    python main.py -i survey.xlsx -e "Company" -p "USA" -c "NYC" --no-charts
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the Excel survey file'
    )
    parser.add_argument(
        '-e', '--empresa',
        required=True,
        help='Company name'
    )
    parser.add_argument(
        '-p', '--pais',
        required=True,
        help='Country'
    )
    parser.add_argument(
        '-c', '--ciudad',
        required=True,
        help='City'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='Disable chart generation'
    )

    args = parser.parse_args()

    try:
        output_path = generate_report(
            input_file=args.input,
            empresa=args.empresa,
            pais=args.pais,
            ciudad=args.ciudad,
            output_dir=args.output,
            include_charts=not args.no_charts,
        )
        print(f"\n✅ Report generated successfully: {output_path}")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    sys.exit(main())
