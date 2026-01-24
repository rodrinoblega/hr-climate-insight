"""
Excel parser for climate survey data.
Reads Excel files from Google Forms and extracts survey responses.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def load_survey(filepath: str | Path) -> pd.DataFrame:
    """
    Load an Excel survey file and return a DataFrame.

    Args:
        filepath: Path to the Excel file

    Returns:
        DataFrame with survey responses

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is empty or invalid
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Survey file not found: {filepath}")

    if not filepath.suffix.lower() in ['.xlsx', '.xls']:
        raise ValueError(f"Invalid file type. Expected Excel file, got: {filepath.suffix}")

    df = pd.read_excel(filepath)

    if df.empty:
        raise ValueError("Survey file is empty")

    if len(df) < 1:
        raise ValueError("Survey file has no data rows")

    return df


def detect_sector_column(df: pd.DataFrame) -> Optional[str]:
    """
    Automatically detect the column containing sector/area information.

    Args:
        df: Survey DataFrame

    Returns:
        Column name if found, None otherwise
    """
    # Expanded keywords for Spanish and English surveys
    sector_keywords = [
        # Spanish
        'sector', 'área', 'area', 'departamento', 'equipo',
        'división', 'division', 'unidad', 'sucursal', 'oficina',
        'planta', 'sede', 'gerencia', 'dirección', 'direccion',
        'región', 'region', 'localidad', 'ubicación', 'ubicacion',
        # English
        'department', 'team', 'unit', 'branch', 'office',
        'location', 'site', 'facility', 'group', 'function',
        # Common patterns
        'trabajas', 'work', 'belong', 'perteneces',
    ]

    for col in df.columns:
        col_lower = col.lower()
        for keyword in sector_keywords:
            if keyword in col_lower:
                # Verify it's a categorical column with reasonable number of unique values
                if df[col].nunique() <= 20:  # Avoid matching free-text columns
                    return col

    return None


def get_survey_stats(df: pd.DataFrame, sector_column: Optional[str] = None) -> dict:
    """
    Get basic statistics about the survey.

    Args:
        df: Survey DataFrame
        sector_column: Name of the sector column (auto-detected if None)

    Returns:
        Dictionary with survey statistics
    """
    if sector_column is None:
        sector_column = detect_sector_column(df)

    stats = {
        'total_responses': len(df),
        'total_questions': len(df.columns),
        'sector_column': sector_column,
        'sectors': {}
    }

    if sector_column and sector_column in df.columns:
        sector_counts = df[sector_column].value_counts().to_dict()
        stats['sectors'] = sector_counts

    return stats


def prepare_data_for_llm(df: pd.DataFrame, sector_column: Optional[str] = None) -> str:
    """
    Convert DataFrame to a format suitable for LLM analysis.

    Args:
        df: Survey DataFrame
        sector_column: Name of the sector column

    Returns:
        CSV string representation of the data
    """
    return df.to_csv(index=False)


def get_column_metadata(df: pd.DataFrame) -> list[dict]:
    """
    Extract metadata about each column (question).

    Args:
        df: Survey DataFrame

    Returns:
        List of dictionaries with column info
    """
    metadata = []

    for i, col in enumerate(df.columns):
        col_data = df[col]
        dtype = str(col_data.dtype)

        # Determine column type
        if col_data.dtype in ['int64', 'float64']:
            col_type = 'numeric'
            unique_values = sorted(col_data.dropna().unique().tolist())
            if len(unique_values) <= 10:
                value_info = unique_values
            else:
                value_info = f"range: {col_data.min()} - {col_data.max()}"
        else:
            col_type = 'categorical'
            value_counts = col_data.value_counts()
            value_info = value_counts.to_dict()

        metadata.append({
            'index': i + 1,
            'name': col,
            'type': col_type,
            'dtype': dtype,
            'null_count': int(col_data.isnull().sum()),
            'values': value_info
        })

    return metadata


def get_survey_summary(df: pd.DataFrame, sector_column: Optional[str] = None) -> str:
    """
    Generate a human-readable summary of the survey structure.
    Useful for helping the LLM understand what dimensions the survey covers.

    Args:
        df: Survey DataFrame
        sector_column: Name of the sector column (optional)

    Returns:
        String summary of the survey structure
    """
    lines = [
        f"RESUMEN DE LA ENCUESTA:",
        f"- Total de respuestas: {len(df)}",
        f"- Total de preguntas: {len(df.columns)}",
    ]

    if sector_column and sector_column in df.columns:
        sector_counts = df[sector_column].value_counts()
        lines.append(f"- Segmentos detectados ({len(sector_counts)}):")
        for sector, count in sector_counts.items():
            lines.append(f"  - {sector}: {count} respuestas")

    lines.append(f"\nESTRUCTURA DE PREGUNTAS:")

    for i, col in enumerate(df.columns):
        col_data = df[col]
        # Truncate long column names for readability
        col_display = col[:100] + "..." if len(col) > 100 else col

        if col_data.dtype in ['int64', 'float64']:
            unique = col_data.dropna().unique()
            if len(unique) <= 10:
                lines.append(f"{i+1}. [Escala numérica] {col_display}")
                lines.append(f"   Valores: {sorted(unique.tolist())}, Promedio: {col_data.mean():.2f}")
            else:
                lines.append(f"{i+1}. [Numérica] {col_display}")
                lines.append(f"   Rango: {col_data.min():.1f} - {col_data.max():.1f}, Promedio: {col_data.mean():.2f}")
        else:
            value_counts = col_data.value_counts()
            if len(value_counts) <= 6:
                lines.append(f"{i+1}. [Categórica] {col_display}")
                values_str = ", ".join([f"{k}: {v}" for k, v in value_counts.head(6).items()])
                lines.append(f"   Respuestas: {values_str}")
            else:
                lines.append(f"{i+1}. [Texto/Múltiple] {col_display}")
                lines.append(f"   {len(value_counts)} valores únicos")

    return "\n".join(lines)
