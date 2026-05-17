"""
Parser de archivos Markdown para el Generador de Analisis Funcional.
Lee archivos .md y extrae metadatos, secciones, tablas y codigo.
"""

import re
from typing import Dict, Any, List, Tuple
from datetime import datetime


class MarkdownParser:
    """Parser de archivos Markdown para el generador de documentos."""
    
    @staticmethod
    def parse_file(file_content: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parsea el contenido de un archivo markdown.
        
        Returns:
            Tuple de (metadata, sections)
            - metadata: dict con metadatos del documento
            - sections: lista de secciones con contenido
        """
        lines = file_content.split('\n')
        
        # Extraer titulo del primer H1
        title_match = re.match(r'^#\s+(.+)$', lines[0].strip()) if lines else None
        full_title = title_match.group(1) if title_match else ""
        
        # Extraer numero de demanda del titulo
        dmnd_match = re.search(r'DMND\s*(\d+)', full_title, re.IGNORECASE)
        numero_demanda = dmnd_match.group(1) if dmnd_match else ""
        
        # Limpiar titulo (quitar DMND si esta al inicio)
        titulo = re.sub(r'^DMND\s*\d+\s*[-–—]\s*', '', full_title, flags=re.IGNORECASE).strip()
        
        # Buscar bloque de metadatos
        metadata = {
            'numero_demanda': numero_demanda,
            'titulo': titulo,
            'fecha': datetime.now().strftime('%d-%m-%Y'),
            'ciclo': '',
            'sistema': 'COMEX',
            'version': '1.0',
            'autor': ''
        }
        
        # Parsear metadatos del bloque ## Metadatos
        metadata, content_start = MarkdownParser._parse_metadata_block(lines, metadata)
        
        # Parsear secciones
        sections = MarkdownParser._parse_sections(lines, content_start)
        
        return metadata, sections
    
    @staticmethod
    def _parse_metadata_block(lines: List[str], default_metadata: Dict) -> Tuple[Dict, int]:
        """Busca y parsea el bloque de metadatos."""
        metadata = default_metadata.copy()
        content_start = 0
        
        for i, line in enumerate(lines):
            if line.strip().lower() == '## metadatos':
                # Leer lineas hasta el siguiente heading o separador
                j = i + 1
                while j < len(lines):
                    line_text = lines[j].strip()
                    
                    # Detenerse al encontrar siguiente heading o separador
                    if line_text.startswith('##') or line_text.startswith('---'):
                        content_start = j + 1 if line_text.startswith('---') else j
                        break
                    
                    # Parsear metadatos en formato "- clave: valor" o "clave: valor"
                    match = re.match(r'^[\s]*[-\*]?\s*(\w+):\s*(.+)$', line_text)
                    if match:
                        key = match.group(1).lower()
                        value = match.group(2).strip()
                        
                        # Mapear claves
                        key_mapping = {
                            'numero_demanda': 'numero_demanda',
                            'numero de demanda': 'numero_demanda',
                            'dmnd': 'numero_demanda',
                            'titulo': 'titulo',
                            'fecha': 'fecha',
                            'ciclo': 'ciclo',
                            'sistema': 'sistema',
                            'version': 'version',
                            'autor': 'autor'
                        }
                        
                        if key in key_mapping:
                            metadata[key_mapping[key]] = value
                    
                    j += 1
                break
        
        # Si no se encontro bloque de metadatos, buscar en el contenido
        if not metadata.get('numero_demanda') and metadata.get('titulo'):
            dmnd_match = re.search(r'DMND\s*(\d+)', metadata['titulo'], re.IGNORECASE)
            if dmnd_match:
                metadata['numero_demanda'] = dmnd_match.group(1)
        
        return metadata, content_start
    
    @staticmethod
    def _parse_sections(lines: List[str], start_idx: int) -> List[Dict[str, Any]]:
        """Parsea las secciones del documento."""
        sections = []
        current_section = None
        current_text = []
        
        i = start_idx
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Detectar nuevo heading de seccion (##)
            section_match = re.match(r'^##\s+(.+)$', stripped)
            if section_match:
                # Guardar seccion anterior
                if current_section:
                    sections.append({
                        'title': current_section,
                        'text': '\n'.join(current_text).strip(),
                        'table': None
                    })
                
                current_section = section_match.group(1).strip()
                current_text = []
                i += 1
                continue
            
            # Ignorar separadores
            if stripped == '---':
                i += 1
                continue
            
            # Acumular contenido
            if current_section:
                current_text.append(line)
            
            i += 1
        
        # Guardar ultima seccion
        if current_section:
            sections.append({
                'title': current_section,
                'text': '\n'.join(current_text).strip(),
                'table': None
            })
        
        # Extraer tablas markdown de cada seccion
        for section in sections:
            section['text'], section['table'] = MarkdownParser._extract_tables(section['text'])
        
        return sections
    
    @staticmethod
    def _extract_tables(text: str) -> Tuple[str, Dict]:
        """Extrae tablas markdown del texto y retorna texto limpio + datos de tabla."""
        lines = text.split('\n')
        clean_lines = []
        table_data = None
        in_table = False
        table_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar inicio de tabla
            if line.startswith('|') and not in_table:
                in_table = True
                table_lines = [line]
                i += 1
                continue
            
            # Acumular lineas de tabla
            if in_table and line.startswith('|'):
                table_lines.append(line)
                i += 1
                continue
            
            # Fin de tabla
            if in_table and not line.startswith('|'):
                in_table = False
                # Parsear tabla
                table_data = MarkdownParser._parse_table_lines(table_lines)
                # No agregar lineas de tabla al texto limpio
                table_lines = []
            
            clean_lines.append(lines[i])
            i += 1
        
        # Si termino en tabla
        if in_table and table_lines:
            table_data = MarkdownParser._parse_table_lines(table_lines)
        
        return '\n'.join(clean_lines).strip(), table_data
    
    @staticmethod
    def _parse_table_lines(table_lines: List[str]) -> Dict:
        """Parsea lineas de tabla markdown a estructura de datos."""
        if len(table_lines) < 2:
            return None
        
        # Header
        headers = [cell.strip() for cell in table_lines[0].split('|') if cell.strip()]
        num_cols = len(headers)
        
        # Skip separador (segunda linea)
        # Data rows
        rows = []
        for line in table_lines[2:]:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                # Asegurar que cada fila tenga el mismo numero de columnas que el header
                if len(cells) < num_cols:
                    cells.extend([''] * (num_cols - len(cells)))
                elif len(cells) > num_cols:
                    cells = cells[:num_cols]
                rows.append(cells)
        
        return {'headers': headers, 'rows': rows}
    
    @staticmethod
    def map_to_predefined_sections(parsed_sections: List[Dict]) -> Dict[str, Dict]:
        """
        Mapea secciones parseadas a las secciones predefinidas del formulario.
        
        Returns:
            Dict con {section_id: {text, table}}
        """
        # Mapeo de titulos a IDs
        section_mapping = {
            'informacion general': 'info_general',
            'información general': 'info_general',
            'historial de versiones': 'historial',
            'historial': 'historial',
            'necesidad': 'necesidad',
            'objetivos': 'objetivos',
            'objetivos y condiciones': 'objetivos',
            'descripcion': 'descripcion_actividades',
            'descripcion de las actividades': 'descripcion_actividades',
            'descripción de las actividades': 'descripcion_actividades',
            'reglas': 'reglas_desarrollo',
            'reglas para el desarrollo': 'reglas_desarrollo',
            'criterios': 'criterios_aceptacion',
            'criterios de aceptacion': 'criterios_aceptacion',
            'criterios de aceptación': 'criterios_aceptacion',
            'aprobaciones': 'aprobaciones'
        }
        
        result = {}
        
        for section in parsed_sections:
            title_lower = section['title'].lower()
            
            # Buscar match exacto o parcial
            matched_id = None
            for key, sec_id in section_mapping.items():
                if key in title_lower or title_lower in key:
                    matched_id = sec_id
                    break
            
            if matched_id:
                result[matched_id] = {
                    'text': section['text'],
                    'table': section['table'],
                    'include_table': section['table'] is not None
                }
        
        return result
