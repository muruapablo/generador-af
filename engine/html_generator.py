"""
Generador de documentos HTML optimizado para Microsoft Loop.
Crea archivos HTML con:
- Acordeones colapsables por defecto (<details>/<summary>)
- Bloques de código con fondo oscuro
- Tablas con estilos limpios
- Botones "Copiar sección" para facilitar pegado en Loop
- Logo centrado
"""

import os
import base64
from jinja2 import Template
from typing import Dict, Any, List, Optional
from markdown import markdown


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.titulo }}</title>
    <style>
    {{ css_content }}
    </style>
</head>
<body>
    <div class="logo-container">
        {% if logo_b64 %}
        <img src="data:image/png;base64,{{ logo_b64 }}" alt="Logo">
        {% endif %}
    </div>

    <div class="metadata-header">
        <h1>{{ metadata.numero_demanda }} - {{ metadata.titulo }}</h1>
        <div class="metadata-row">
            <span><span class="metadata-label">Número de llamado:</span> {{ metadata.numero_demanda }}</span>
            <span><span class="metadata-label">Fecha:</span> {{ metadata.fecha }}</span>
            <span><span class="metadata-label">Ciclo:</span> {{ metadata.ciclo }}</span>
        </div>
        <div class="metadata-row">
            <span><span class="metadata-label">Sistema/Módulo:</span> {{ metadata.sistema }}</span>
            <span><span class="metadata-label">Versión:</span> {{ metadata.version }}</span>
            <span><span class="metadata-label">Autor:</span> {{ metadata.autor }}</span>
        </div>
    </div>

    {% for section in sections %}
    <section class="section-block" id="sec-{{ section.id }}">
        <details {% if not section.open %}open{% endif %}>
            <summary>{{ section.title }}</summary>
            <div class="details-content">
                <button class="copy-btn" onclick="copySection('sec-{{ section.id }}')">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path>
                    </svg>
                    Copiar sección
                </button>
                <div class="section-body">
                    {{ section.html_content | safe }}
                </div>
            </div>
        </details>
    </section>
    {% endfor %}

    <script>
        function copySection(sectionId) {
            const section = document.getElementById(sectionId);
            const content = section.querySelector('.section-body');
            const range = document.createRange();
            range.selectNode(content);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            document.execCommand('copy');
            window.getSelection().removeAllRanges();
            
            const btn = section.querySelector('.copy-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '✓ Copiado';
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 2000);
        }
    </script>
</body>
</html>
"""

HTML_FULL_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.titulo }} - Completo</title>
    <style>
    {{ css_content }}
    /* Estilos adicionales para vista completa */
    .full-section {
        margin-bottom: 32px;
        padding-bottom: 24px;
        border-bottom: 2px solid var(--color-table-border);
    }
    .full-section-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--color-text);
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 3px solid var(--color-primary);
    }
    .full-content {
        padding: 8px 0;
    }
    </style>
</head>
<body>
    <div class="logo-container">
        {% if logo_b64 %}
        <img src="data:image/png;base64,{{ logo_b64 }}" alt="Logo">
        {% endif %}
    </div>

    <div class="metadata-header">
        <h1>{{ metadata.numero_demanda }} - {{ metadata.titulo }}</h1>
        <div class="metadata-row">
            <span><span class="metadata-label">Número de llamado:</span> {{ metadata.numero_demanda }}</span>
            <span><span class="metadata-label">Fecha:</span> {{ metadata.fecha }}</span>
            <span><span class="metadata-label">Ciclo:</span> {{ metadata.ciclo }}</span>
        </div>
        <div class="metadata-row">
            <span><span class="metadata-label">Sistema/Módulo:</span> {{ metadata.sistema }}</span>
            <span><span class="metadata-label">Versión:</span> {{ metadata.version }}</span>
            <span><span class="metadata-label">Autor:</span> {{ metadata.autor }}</span>
        </div>
    </div>

    {% for section in sections %}
    <section class="full-section" id="sec-{{ section.id }}">
        <div class="full-section-title">{{ section.title }}</div>
        <div class="full-content">
            {{ section.html_content | safe }}
        </div>
    </section>
    {% endfor %}

</body>
</html>
"""


class HTMLGenerator:
    def __init__(self, css_path: str = None):
        self.css_path = css_path or os.path.join(os.path.dirname(__file__), '..', 'assets', 'loop.css')
        self.template = Template(HTML_TEMPLATE)

    def _load_css(self) -> str:
        """Carga el contenido del archivo CSS."""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _encode_logo(self, logo_path: Optional[str]) -> Optional[str]:
        """Codifica el logo a base64 para embeberlo en HTML."""
        if not logo_path or not os.path.exists(logo_path):
            return None
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _markdown_to_html(self, text: str) -> str:
        """Convierte texto markdown a HTML."""
        if not text:
            return ""
        # Usar markdown library con extensiones para tablas y código
        extensions = ['tables', 'fenced_code']
        return markdown(text, extensions=extensions)

    def _prepare_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepara las secciones para el template HTML."""
        prepared = []
        for section in sections:
            sec_id = section.get('id', '')
            if sec_id == 'portada':
                continue  # La portada se muestra arriba como metadata header

            title = section.get('title', '')
            text = section.get('text', '')

            # Convertir markdown a HTML
            html_content = self._markdown_to_html(text)

            # Agregar tabla si existe (convertir markdown table)
            table = section.get('table')
            if table and table.get('headers'):
                table_md = self._table_to_markdown(table)
                html_content += self._markdown_to_html(table_md)

            prepared.append({
                'id': sec_id,
                'title': title,
                'html_content': html_content,
                'open': True  # Colapsados por defecto (open=False en details)
            })

        return prepared

    def _table_to_markdown(self, table_data: Dict[str, Any]) -> str:
        """Convierte datos de tabla a markdown."""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        if not headers:
            return ""

        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        return "\n".join(lines)

    def generate(self, metadata: Dict[str, Any], sections: List[Dict[str, Any]], 
                 output_path: str, logo_path: Optional[str] = None,
                 use_accordion: bool = True) -> str:
        """
        Genera el archivo HTML completo.
        
        Args:
            metadata: Diccionario con metadatos del documento
            sections: Lista de secciones con contenido
            output_path: Ruta donde guardar el HTML
            logo_path: Ruta al logo PNG (opcional)
            use_accordion: Si True, usa acordeones colapsables. 
                          Si False, genera HTML plano con todo visible.
        
        Returns:
            Ruta al archivo generado
        """
        # Cargar CSS
        css_content = self._load_css()

        # Codificar logo
        logo_b64 = self._encode_logo(logo_path)

        # Preparar secciones
        prepared_sections = self._prepare_sections(sections)

        # Seleccionar template según modo
        if use_accordion:
            template = Template(HTML_TEMPLATE)
        else:
            template = Template(HTML_FULL_TEMPLATE)

        # Renderizar template
        html_output = template.render(
            metadata=metadata,
            sections=prepared_sections,
            css_content=css_content,
            logo_b64=logo_b64
        )

        # Guardar
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        return output_path
