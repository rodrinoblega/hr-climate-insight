"""
Anonymity filter for survey data.
Ensures data is filtered to protect respondent identity (n >= 5 threshold).

CRITICAL: This is a zero-tolerance requirement. All data sent to LLM
must pass through this filter first.
"""

import pandas as pd
import logging
from typing import Optional

# Hardcoded anonymity threshold - DO NOT CHANGE without authorization
ANONYMITY_THRESHOLD = 5

logger = logging.getLogger(__name__)


def apply_anonymity_filter(
    df: pd.DataFrame,
    sector_column: str,
    threshold: int = ANONYMITY_THRESHOLD
) -> tuple[pd.DataFrame, dict]:
    """
    Filter data to ensure anonymity by removing segments with n < threshold.

    Args:
        df: Survey DataFrame
        sector_column: Column name containing sector/segment information
        threshold: Minimum responses required (default: 5)

    Returns:
        Tuple of (filtered_df, exclusion_report)

    Raises:
        ValueError: If sector_column not in DataFrame
    """
    if sector_column not in df.columns:
        raise ValueError(f"Sector column '{sector_column}' not found in data")

    # Count responses per segment
    sector_counts = df[sector_column].value_counts()

    # Identify segments below threshold
    excluded_segments = sector_counts[sector_counts < threshold].to_dict()
    included_segments = sector_counts[sector_counts >= threshold].to_dict()

    # Filter out excluded segments
    mask = df[sector_column].isin(included_segments.keys())
    filtered_df = df[mask].copy()

    # Build exclusion report
    exclusion_report = {
        'threshold': threshold,
        'original_count': len(df),
        'filtered_count': len(filtered_df),
        'excluded_count': len(df) - len(filtered_df),
        'excluded_segments': excluded_segments,
        'included_segments': included_segments,
        'warning': None
    }

    if excluded_segments:
        excluded_names = list(excluded_segments.keys())
        logger.warning(
            f"Anonymity filter excluded {len(excluded_segments)} segment(s): {excluded_names}"
        )
        exclusion_report['warning'] = (
            f"Se excluyeron del análisis los siguientes segmentos por tener menos de "
            f"{threshold} respuestas (protección de anonimato): {', '.join(excluded_names)}"
        )

    return filtered_df, exclusion_report


def validate_anonymity(df: pd.DataFrame, sector_column: str) -> bool:
    """
    Validate that all segments in the data meet the anonymity threshold.

    Args:
        df: Survey DataFrame (should be already filtered)
        sector_column: Column name containing sector/segment information

    Returns:
        True if all segments meet threshold, False otherwise
    """
    if sector_column not in df.columns:
        return True  # No sector column, no segment-level anonymity concern

    sector_counts = df[sector_column].value_counts()
    return all(count >= ANONYMITY_THRESHOLD for count in sector_counts)


def get_anonymity_summary(exclusion_report: dict) -> str:
    """
    Generate a human-readable summary of the anonymity filtering.

    Args:
        exclusion_report: Report from apply_anonymity_filter

    Returns:
        Summary string for inclusion in reports
    """
    lines = [
        f"Total de respuestas originales: {exclusion_report['original_count']}",
        f"Respuestas incluidas en el análisis: {exclusion_report['filtered_count']}",
    ]

    if exclusion_report['excluded_segments']:
        lines.append(f"\nSegmentos excluidos por anonimato (n < {exclusion_report['threshold']}):")
        for segment, count in exclusion_report['excluded_segments'].items():
            lines.append(f"  - {segment}: {count} respuestas")

    lines.append(f"\nSegmentos incluidos:")
    for segment, count in exclusion_report['included_segments'].items():
        lines.append(f"  - {segment}: {count} respuestas")

    return "\n".join(lines)
