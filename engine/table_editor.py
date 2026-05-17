"""
Componente de editor de tablas visual.
Proporciona funciones para crear, editar y convertir tablas
entre formato de datos (listas/diccionarios) y Markdown.
"""

import pandas as pd
from typing import List, Dict, Any, Optional


def create_empty_table(columns: List[str], num_rows: int = 3) -> pd.DataFrame:
    """Crea un DataFrame vacío con las columnas especificadas."""
    data = {col: [""] * num_rows for col in columns}
    return pd.DataFrame(data)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Convierte un DataFrame a tabla Markdown."""
    if df.empty:
        return ""

    lines = []
    # Header
    headers = df.columns.tolist()
    lines.append("| " + " | ".join(headers) + " |")
    # Separator
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    # Rows
    for _, row in df.iterrows():
        cells = [str(val) if val is not None else "" for val in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def markdown_to_dataframe(table_md: str) -> Optional[pd.DataFrame]:
    """Convierte una tabla Markdown a DataFrame."""
    if not table_md or not table_md.strip():
        return None

    lines = [line.strip() for line in table_md.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return None

    # Parse header
    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]

    # Parse data rows (skip header and separator)
    rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|')]
        # Filter empty cells at start/end due to split
        cells = [c for c in cells if c]
        if cells:
            rows.append(cells)

    if not rows:
        return pd.DataFrame(columns=headers)

    # Ensure all rows have same number of columns
    max_cols = max(len(row) for row in rows)
    for row in rows:
        while len(row) < max_cols:
            row.append("")

    df = pd.DataFrame(rows, columns=headers[:max_cols])
    return df


def validate_table_data(df: pd.DataFrame) -> bool:
    """Valida que el DataFrame tenga al menos un header y no esté vacío."""
    return not df.empty and len(df.columns) > 0


def add_empty_row(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega una fila vacía al DataFrame."""
    new_row = pd.DataFrame([[""] * len(df.columns)], columns=df.columns)
    return pd.concat([df, new_row], ignore_index=True)


def remove_last_row(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina la última fila del DataFrame."""
    if len(df) > 0:
        return df.iloc[:-1].reset_index(drop=True)
    return df


def get_table_editor_config() -> Dict[str, Any]:
    """Configuración por defecto para el editor de tablas en Streamlit."""
    return {
        "height": 300,
        "width": "stretch",
        "hide_index": True,
        "column_config": {
            "editable": True,
            "disabled": False
        }
    }
