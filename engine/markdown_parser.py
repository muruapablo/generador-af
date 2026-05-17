"""
Parser de contenido Markdown para estructurar los datos del análisis funcional.
Convierte texto del formulario a una estructura de datos que pueden consumir
los generadores DOCX y HTML.
"""

import re
from typing import List, Dict, Any


def parse_markdown_sections(text: str) -> List[Dict[str, Any]]:
    """
    Parsea texto markdown en secciones basadas en headings (# ## ###).
    Retorna una lista de diccionarios con 'level', 'title', 'content'.
    """
    sections = []
    current_section = None
    lines = text.split('\n')

    for line in lines:
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if heading_match:
            if current_section:
                sections.append(current_section)
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            current_section = {
                "level": level,
                "title": title,
                "content": []
            }
        elif current_section is not None:
            current_section["content"].append(line)
        else:
            # Texto antes del primer heading
            if not sections:
                sections.append({
                    "level": 0,
                    "title": "",
                    "content": [line]
                })
            else:
                sections[-1]["content"].append(line)

    if current_section:
        sections.append(current_section)

    # Join content lines
    for sec in sections:
        sec["content"] = '\n'.join(sec["content"]).strip()

    return sections


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extrae bloques de código markdown (``` ... ```) del texto.
    Retorna lista de dicts con 'language' y 'code'.
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    blocks = []
    for lang, code in matches:
        blocks.append({
            "language": lang or "text",
            "code": code.strip()
        })
    return blocks


def split_content_and_code(text: str) -> List[Dict[str, Any]]:
    """
    Divide el texto en partes alternadas: texto normal y bloques de código.
    Útil para renderizar progresivamente.
    """
    parts = []
    pattern = r'(```(?:\w+)?\n.*?```)'
    segments = re.split(pattern, text, flags=re.DOTALL)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        if segment.startswith('```'):
            # Es código
            lines = segment.split('\n')
            lang = lines[0].replace('```', '').strip()
            code = '\n'.join(lines[1:-1]).strip()
            parts.append({"type": "code", "language": lang, "content": code})
        else:
            parts.append({"type": "text", "content": segment})

    return parts


def markdown_table_to_data(table_md: str) -> Dict[str, Any]:
    """
    Convierte una tabla markdown a lista de diccionarios.
    """
    lines = [line.strip() for line in table_md.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return {"headers": [], "rows": []}

    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    rows = []
    for line in lines[2:]:  # Skip header and separator
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells:
            rows.append(cells)

    return {"headers": headers, "rows": rows}


def structure_analysis_document(metadata: Dict[str, Any], sections_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estructura todo el documento de análisis funcional.
    """
    document = {
        "metadata": metadata,
        "sections": []
    }

    for section_id, content in sections_data.items():
        if isinstance(content, dict):
            # Tiene texto + tabla
            document["sections"].append({
                "id": section_id,
                "text": content.get("text", ""),
                "table": content.get("table", None),
                "has_table": content.get("table") is not None
            })
        else:
            # Solo texto
            document["sections"].append({
                "id": section_id,
                "text": content,
                "table": None,
                "has_table": False
            })

    return document
