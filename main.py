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
from prompts.section_prompts import SYSTEM_PROMPT_BASE, SECTIONS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Month translations by language
MONTH_TRANSLATIONS = {
    "es": {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    },
    "pt": {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    },
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
}

# Country to language mapping
COUNTRY_LANGUAGE = {
    "argentina": "es", "méxico": "es", "mexico": "es", "españa": "es", "spain": "es",
    "colombia": "es", "chile": "es", "perú": "es", "peru": "es", "uruguay": "es",
    "paraguay": "es", "venezuela": "es", "ecuador": "es", "bolivia": "es",
    "brasil": "pt", "brazil": "pt",
    "usa": "en", "united states": "en", "uk": "en", "united kingdom": "en",
    "canada": "en", "australia": "en"
}


def get_localized_date(pais: str) -> str:
    """Get current date formatted in the language of the country."""
    now = datetime.now()
    country_lower = pais.lower().strip()
    lang = COUNTRY_LANGUAGE.get(country_lower, "es")  # Default to Spanish
    month_name = MONTH_TRANSLATIONS[lang][now.month]
    return f"{month_name} {now.year}"


def generate_report_by_sections(
    client: OpenAI,
    datos_csv: str,
    empresa: str,
    pais: str,
    ciudad: str,
    fecha: str,
    n_total: int,
    nota_anonimato: str,
    graficos_disponibles: str,
) -> str:
    """
    Generate report in sections to ensure sufficient content length.

    Makes separate API calls for each section, passing context between them.
    This approach produces ~8,000+ words instead of ~2,000 from a single call.

    Args:
        client: OpenAI client instance
        datos_csv: CSV data prepared for LLM
        empresa: Company name
        pais: Country
        ciudad: City
        fecha: Report date
        n_total: Total valid responses
        nota_anonimato: Anonymity note
        graficos_disponibles: Available charts summary

    Returns:
        Complete markdown report
    """
    all_sections_content = []
    dimensiones_previas = ""
    resumen_dimensiones = ""
    total_tokens = {"input": 0, "output": 0}

    for i, section in enumerate(SECTIONS):
        logger.info(f"Generating section {i+1}/{len(SECTIONS)}: {section['name']} (min {section['min_words']} words)")

        # Format the section prompt with available data
        section_prompt = section["prompt"].format(
            empresa_nombre=empresa,
            pais=pais,
            ciudad=ciudad,
            fecha=fecha,
            n_total=n_total,
            nota_anonimato=nota_anonimato,
            graficos_disponibles=graficos_disponibles,
            datos_csv=datos_csv,
            dimensiones_previas=dimensiones_previas,
            resumen_dimensiones=resumen_dimensiones,
        )

        # Make API call for this section
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_BASE},
                {"role": "user", "content": section_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
        )

        section_content = response.choices[0].message.content
        all_sections_content.append(section_content)

        # Track token usage
        usage = response.usage
        total_tokens["input"] += usage.prompt_tokens
        total_tokens["output"] += usage.completion_tokens

        logger.info(f"  Section {section['name']}: {len(section_content)} chars, {usage.completion_tokens} tokens")

        # Update context for subsequent sections
        if section["id"].startswith("dimensiones"):
            dimensiones_previas += f"\n\n{section_content}"

            # Create a brief summary for later sections
            # Extract just the dimension titles and key findings
            lines = section_content.split("\n")
            for line in lines:
                if line.startswith("### ") or line.startswith("**Nivel de riesgo"):
                    resumen_dimensiones += line + "\n"

    # Log total token usage
    total = total_tokens["input"] + total_tokens["output"]
    logger.info(f"Total token usage - Input: {total_tokens['input']}, Output: {total_tokens['output']}, Total: {total}")

    # Combine all sections
    full_report = "\n\n".join(all_sections_content)

    # Count approximate words
    word_count = len(full_report.split())
    logger.info(f"Total report length: {len(full_report)} chars, ~{word_count} words")

    return full_report


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

    # Step 6: Prepare variables for report generation
    fecha = get_localized_date(pais)

    # Format charts section
    if include_charts and charts_summary:
        graficos_disponibles = charts_summary
    else:
        graficos_disponibles = "No hay gráficos disponibles para esta encuesta."

    # Step 7: Generate report by sections (7 API calls for deeper content)
    logger.info(f"Generating report by sections using {config.OPENAI_MODEL}...")
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    markdown_content = generate_report_by_sections(
        client=client,
        datos_csv=datos_csv,
        empresa=empresa,
        pais=pais,
        ciudad=ciudad,
        fecha=fecha,
        n_total=len(filtered_df),
        nota_anonimato=nota_anonimato,
        graficos_disponibles=graficos_disponibles,
    )

    logger.info(f"Report generation complete: {len(markdown_content)} characters")

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
