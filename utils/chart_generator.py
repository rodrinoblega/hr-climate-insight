"""
Chart generator for climate survey data.
Creates bar charts for survey questions using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use

import pandas as pd
from pathlib import Path
from typing import Optional
import tempfile
import hashlib


# Color palettes for different chart types
COLORS_NUMERIC = ['#a8d5e5', '#6bb8d4', '#3a9fc2', '#1a7fa3', '#0d5f7a']
COLORS_CATEGORICAL_POSITIVE = ['#66c2a5', '#a6d96a', '#d9ef8b']  # Green tones for Si/positive
COLORS_CATEGORICAL_NEUTRAL = ['#fee08b', '#fdae61', '#f46d43']  # Yellow/orange for mixed
COLORS_CATEGORICAL_NEGATIVE = ['#d73027', '#a50026']  # Red for negative


def get_chart_data(df: pd.DataFrame) -> dict:
    """
    Analyze the dataframe and extract chartable questions.

    Args:
        df: Survey DataFrame

    Returns:
        Dictionary with question names as keys and chart info as values
    """
    chart_data = {}

    for col in df.columns:
        col_data = df[col].dropna()

        if len(col_data) == 0:
            continue

        # Check if it's a numeric scale (1-5, 1-10, etc.)
        if col_data.dtype in ['int64', 'float64']:
            unique_values = sorted(col_data.unique())
            if 2 <= len(unique_values) <= 10:
                value_counts = col_data.value_counts().sort_index()
                chart_data[col] = {
                    'type': 'numeric_scale',
                    'values': value_counts.index.tolist(),
                    'counts': value_counts.values.tolist(),
                    'labels': [str(int(v)) for v in value_counts.index],
                    'mean': col_data.mean(),
                }
        else:
            # Categorical data
            value_counts = col_data.value_counts()
            if 2 <= len(value_counts) <= 6:
                chart_data[col] = {
                    'type': 'categorical',
                    'values': value_counts.index.tolist(),
                    'counts': value_counts.values.tolist(),
                    'labels': value_counts.index.tolist(),
                }

    return chart_data


def generate_chart(
    question: str,
    chart_info: dict,
    output_dir: Path,
    width: float = 6,
    height: float = 4,
) -> Optional[Path]:
    """
    Generate a bar chart for a survey question.

    Args:
        question: The question text (used for title)
        chart_info: Dictionary with chart data from get_chart_data()
        output_dir: Directory to save the chart image
        width: Figure width in inches
        height: Figure height in inches

    Returns:
        Path to the generated PNG file, or None if generation failed
    """
    try:
        fig, ax = plt.subplots(figsize=(width, height))

        labels = chart_info['labels']
        counts = chart_info['counts']

        # Select colors based on chart type
        if chart_info['type'] == 'numeric_scale':
            # Gradient from light to dark blue
            n_bars = len(labels)
            colors = COLORS_NUMERIC[:n_bars] if n_bars <= len(COLORS_NUMERIC) else COLORS_NUMERIC
        else:
            # For categorical, try to assign colors based on content
            colors = _get_categorical_colors(labels)

        # Create bars
        bars = ax.bar(range(len(labels)), counts, color=colors[:len(labels)])

        # Customize chart
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylabel('Cantidad de respuestas', fontsize=10)
        ax.set_xlabel('')

        # Title - truncate if too long
        title = _format_title(question)
        ax.set_title(title, fontsize=11, pad=10)

        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.annotate(f'{count}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        # Generate filename from question hash
        question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        output_path = output_dir / f"chart_{question_hash}.png"

        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)

        return output_path

    except Exception as e:
        print(f"Error generating chart for '{question[:50]}...': {e}")
        plt.close('all')
        return None


def _format_title(question: str, max_length: int = 60) -> str:
    """Format question text for use as chart title."""
    # Remove common prefixes like "1. 1)." etc.
    import re
    cleaned = re.sub(r'^[\d\.\)\s]+', '', question)

    # Truncate if needed
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + '...'

    # Ensure it starts with ¿ if it's a question
    if not cleaned.startswith('¿') and '?' in cleaned:
        cleaned = '¿' + cleaned

    return cleaned


def _get_categorical_colors(labels: list) -> list:
    """Assign colors to categorical labels based on their meaning."""
    colors = []

    positive_keywords = ['sí', 'si', 'yes', 'siempre', 'always', 'frecuentemente',
                        'excelente', 'muy bueno', 'bueno']
    neutral_keywords = ['tal vez', 'maybe', 'a veces', 'sometimes', 'regular',
                       'más o menos', 'no sé', 'neutro']
    negative_keywords = ['no', 'nunca', 'never', 'rara vez', 'rarely', 'malo',
                        'muy malo', 'pésimo']

    for label in labels:
        label_lower = str(label).lower().strip()

        if any(kw in label_lower for kw in positive_keywords):
            colors.append('#66c2a5')  # Green
        elif any(kw in label_lower for kw in neutral_keywords):
            colors.append('#fdae61')  # Orange
        elif any(kw in label_lower for kw in negative_keywords):
            colors.append('#d73027')  # Red
        else:
            colors.append('#8da0cb')  # Default blue-gray

    return colors


def generate_all_charts(
    df: pd.DataFrame,
    output_dir: Path,
    max_charts: int = 10,
) -> dict:
    """
    Generate charts for all chartable questions in the survey.

    Args:
        df: Survey DataFrame
        output_dir: Directory to save chart images
        max_charts: Maximum number of charts to generate

    Returns:
        Dictionary mapping question text to chart file path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_data = get_chart_data(df)
    generated_charts = {}

    for i, (question, info) in enumerate(chart_data.items()):
        if i >= max_charts:
            break

        chart_path = generate_chart(question, info, output_dir)
        if chart_path:
            generated_charts[question] = {
                'path': chart_path,
                'info': info,
            }

    return generated_charts


def _extract_keyword(question: str) -> str:
    """
    Extract a simple keyword from a question for use in chart markers.

    Args:
        question: The full question text

    Returns:
        A short keyword (2-4 words) that identifies the question
    """
    import re

    # Remove common prefixes like "1. 1)." etc.
    cleaned = re.sub(r'^[\d\.\)\s]+', '', question)

    # Remove question marks and common filler words
    cleaned = cleaned.replace('¿', '').replace('?', '')

    # Common keyword mappings for typical survey questions
    keyword_patterns = [
        (r'orgulloso|orgullo', 'orgullo'),
        (r'recomendar|recomendarías', 'recomendar'),
        (r'cambiar.*trabajo|cambiarías', 'cambiar_trabajo'),
        (r'tratados.*igual|favoritismo|equidad', 'trato_igualitario'),
        (r'objetivos.*empresa|conoces.*objetivos', 'objetivos_empresa'),
        (r'objetivos.*puesto|descripción.*puesto', 'objetivos_puesto'),
        (r'remuneración|salario|sueldo', 'remuneracion'),
        (r'herramientas|software|elementos', 'herramientas'),
        (r'procesos.*desactualizados|mejorar.*procesos', 'procesos'),
        (r'propusiste.*mejora|comentaste.*mejora', 'propuestas_mejora'),
        (r'beneficios', 'beneficios'),
        (r'capacitaci[oó]n|formación', 'capacitacion'),
        (r'equipo.*trabajo|gusto.*equipo', 'equipo_trabajo'),
        (r'clima.*laboral|ambiente.*trabajo', 'clima_laboral'),
        (r'colaboración.*área|colaboración.*equipo', 'colaboracion'),
        (r'feedback|devolución|retroalimentación', 'feedback'),
        (r'reconoce.*esfuerzo|reconocimiento', 'reconocimiento'),
        (r'escucha.*opiniones|tiene.*cuenta', 'escucha'),
        (r'liderazgo|líder|superior', 'liderazgo'),
        (r'apoyo|contención', 'apoyo'),
        (r'dependencia.*jerárquica|esquema.*dependencia', 'jerarquia'),
        (r'comunicación.*área|comunicación.*interna', 'comunicacion'),
        (r'direcci[oó]n|gerencia', 'direccion'),
        (r'encuesta.*importante|importancia.*encuesta', 'importancia_encuesta'),
        (r'eficiente|eficiencia', 'eficiencia'),
        (r'confianza|confí[ao]', 'confianza'),
        (r'error|mencionar.*error', 'errores'),
        (r'problemas.*culpables|resolver.*problemas', 'resolver_problemas'),
        (r'sector|área.*trabajas', 'sector'),
    ]

    cleaned_lower = cleaned.lower()
    for pattern, keyword in keyword_patterns:
        if re.search(pattern, cleaned_lower):
            return keyword

    # Fallback: take first 3 significant words
    words = re.findall(r'\b[a-záéíóúñü]{4,}\b', cleaned_lower)
    if words:
        return '_'.join(words[:2])

    return cleaned[:20].lower().replace(' ', '_')


def get_chartable_questions_summary(df: pd.DataFrame, max_charts: int = 15) -> str:
    """
    Generate a summary of chartable questions for the LLM prompt.
    Uses keywords instead of numbers for more reliable matching.
    Only includes questions up to max_charts to match what's actually generated.

    Args:
        df: Survey DataFrame
        max_charts: Maximum number of charts (should match generate_all_charts)

    Returns:
        String summary for inclusion in the prompt
    """
    chart_data = get_chart_data(df)

    if not chart_data:
        return "No se detectaron preguntas graficables en esta encuesta."

    lines = [
        "PREGUNTAS GRAFICABLES DISPONIBLES:",
        "Usa el marcador [GRAFICO: palabra_clave] para insertar gráficos.",
        "Las palabras clave disponibles son:",
        ""
    ]

    # Only show questions up to max_charts (same limit as generate_all_charts)
    for i, (question, info) in enumerate(chart_data.items()):
        if i >= max_charts:
            break

        keyword = _extract_keyword(question)
        # Truncate question for display
        q_display = question[:70] + "..." if len(question) > 70 else question

        if info['type'] == 'numeric_scale':
            lines.append(f"• [GRAFICO: {keyword}] → {q_display}")
            lines.append(f"  Promedio: {info['mean']:.2f}")
        else:
            lines.append(f"• [GRAFICO: {keyword}] → {q_display}")
            # Show distribution
            dist = ", ".join([f"{l}: {c}" for l, c in zip(info['labels'][:3], info['counts'][:3])])
            lines.append(f"  Distribución: {dist}")
        lines.append("")

    return "\n".join(lines)
