import streamlit as st
import os
import sys
import zipfile
import shutil
from datetime import datetime
from typing import Dict, Any, List

# Librerías UI extras
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from stqdm import stqdm

# Añadir engine al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engine'))

from forms.sections_config import SECTIONS, DEFAULT_METADATA
from engine.markdown_parser import structure_analysis_document
from engine.table_editor import (
    create_empty_table, dataframe_to_markdown, 
    markdown_to_dataframe, add_empty_row, remove_last_row
)
from engine.docx_generator import DOCXGenerator
from engine.html_generator import HTMLGenerator
from engine.md_parser import MarkdownParser

# Configuración de página
st.set_page_config(
    page_title="Generador de Análisis Funcional",
    page_icon=":page_facing_up:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Cargar CSS custom
def load_custom_css():
    css_path = os.path.join(ASSETS_DIR, "streamlit_custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Cargar Bootstrap Icons para iconos profesionales
    st.markdown(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">',
        unsafe_allow_html=True
    )


def calculate_progress():
    """Calcula el progreso de completado de las secciones."""
    if not st.session_state.sections_data:
        return 0
    
    total_sections = len(SECTIONS) - 1  # Excluir portada
    completed = 0
    
    for sec in SECTIONS:
        sec_id = sec['id']
        if sec_id == 'portada':
            continue
        if sec_id in st.session_state.sections_data:
            text = st.session_state.sections_data[sec_id].get('text', '')
            if text and len(text.strip()) > 20:
                completed += 1
    
    return int((completed / total_sections) * 100) if total_sections > 0 else 0


def init_session_state():
    """Inicializa el estado de sesión."""
    if 'metadata' not in st.session_state:
        st.session_state.metadata = DEFAULT_METADATA.copy()
        st.session_state.metadata['fecha'] = datetime.now().strftime('%d-%m-%Y')
    
    if 'sections_data' not in st.session_state:
        st.session_state.sections_data = {}
    
    if 'uploaded_logo' not in st.session_state:
        st.session_state.uploaded_logo = None
    
    if 'logo_temp_path' not in st.session_state:
        st.session_state.logo_temp_path = None
    
    if 'custom_filename' not in st.session_state:
        st.session_state.custom_filename = ""
    
    if 'md_parsed' not in st.session_state:
        st.session_state.md_parsed = False
    
    if 'md_sections_count' not in st.session_state:
        st.session_state.md_sections_count = 0
    
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = None
    
    if 'modo_seleccionado' not in st.session_state:
        st.session_state.modo_seleccionado = None


def render_welcome_screen():
    """Muestra la pantalla de bienvenida para seleccionar modo de trabajo."""
    colored_header(
        label="Generador de Análisis Funcional",
        description="Seleccioná cómo querés empezar",
        color_name="orange-70"
    )
    
    st.markdown("### ¿Cómo querés empezar?")
    st.caption("Elegí una opción para continuar. Podés cambiar de modo más tarde desde el sidebar.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown('### <i class="bi bi-file-text"></i> Formulario Web', unsafe_allow_html=True)
            st.markdown("""
            **Ideal para:**
            - Crear documentos desde cero
            - Editar sección por sección
            - Usar el editor visual de tablas
            - Agregar código SQL y estructuras
            """)
            if st.button("Comenzar con Formulario", type="primary", key="btn_formulario", use_container_width=True):
                st.session_state.modo_seleccionado = "Formulario Web"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown('### <i class="bi bi-cloud-upload"></i> Subir Archivos', unsafe_allow_html=True)
            st.markdown("""
            **Ideal para:**
            - Importar desde archivos Markdown
            - Parsear documentos existentes
            - Generar automáticamente
            - Reutilizar contenido previo
            """)
            if st.button("Comenzar con Archivos", type="primary", key="btn_archivos", use_container_width=True):
                st.session_state.modo_seleccionado = "Subir Archivos (.md)"
                st.rerun()
    
    st.divider()
    st.info('<i class="bi bi-lightbulb"></i> **Recomendado:** Formulario Web para documentos nuevos.', unsafe_allow_html=True)


def save_uploaded_logo(uploaded_file) -> str:
    """Guarda el logo subido temporalmente."""
    if uploaded_file is not None:
        temp_path = os.path.join(GENERATED_DIR, "temp_logo.png")
        os.makedirs(GENERATED_DIR, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return temp_path
    return None


def get_filename() -> str:
    """Genera el nombre del archivo basado en metadatos o personalizado."""
    if st.session_state.custom_filename:
        return st.session_state.custom_filename
    
    dmnd = st.session_state.metadata.get('numero_demanda', '')
    if dmnd:
        return f"DMND{dmnd}"
    return "AnalisisFuncional"


def generate_documents(use_accordion=True):
    """Genera los documentos DOCX y HTML con barra de progreso."""
    filename = get_filename()
    output_dir = os.path.join(GENERATED_DIR, filename)
    os.makedirs(output_dir, exist_ok=True)

    # Preparar secciones
    sections_list = []
    for sec in SECTIONS:
        sec_id = sec['id']
        if sec_id in st.session_state.sections_data:
            data = st.session_state.sections_data[sec_id]
            sections_list.append({
                'id': sec_id,
                'title': sec['titulo'],
                'text': data.get('text', ''),
                'table': data.get('table', None),
                'include_table': data.get('include_table', True)
            })

    # Determinar pasos totales
    total_steps = 3 if use_accordion else 2
    current_step = 0
    
    # Generar DOCX
    docx_path = os.path.join(output_dir, f"{filename}.docx")
    for _ in stqdm(range(1), desc="Generando DOCX", total=total_steps, position=0):
        docx_gen = DOCXGenerator(logo_path=st.session_state.logo_temp_path)
        docx_gen.generate(
            metadata=st.session_state.metadata,
            sections=sections_list,
            output_path=docx_path
        )
        current_step += 1

    # Generar HTML
    html_path = os.path.join(output_dir, f"{filename}.html")
    for _ in stqdm(range(1), desc="Generando HTML", total=total_steps, position=0):
        html_gen = HTMLGenerator()
        html_gen.generate(
            metadata=st.session_state.metadata,
            sections=sections_list,
            output_path=html_path,
            logo_path=st.session_state.logo_temp_path,
            use_accordion=use_accordion
        )
        current_step += 1
    
    # Generar HTML completo adicional (si se usan acordeones)
    html_full_path = None
    if use_accordion:
        html_full_path = os.path.join(output_dir, f"{filename}_completo.html")
        for _ in stqdm(range(1), desc="Generando HTML completo", total=total_steps, position=0):
            html_gen.generate(
                metadata=st.session_state.metadata,
                sections=sections_list,
                output_path=html_full_path,
                logo_path=st.session_state.logo_temp_path,
                use_accordion=False
            )
            current_step += 1
    
    # Crear ZIP
    zip_path = os.path.join(output_dir, f"{filename}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(docx_path, os.path.basename(docx_path))
        zipf.write(html_path, os.path.basename(html_path))
        if html_full_path and os.path.exists(html_full_path):
            zipf.write(html_full_path, os.path.basename(html_full_path))
    
    return docx_path, html_path, html_full_path, zip_path, output_dir


def render_sidebar():
    """Renderiza la barra lateral con componentes mejorados."""
    st.sidebar.markdown("### Generador")
    st.sidebar.caption("Análisis Funcional")
    st.sidebar.divider()
    
    # Indicador de progreso con metric card
    if st.session_state.sections_data:
        progress = calculate_progress()
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric(
                label="Progreso",
                value=f"{progress}%",
                delta=f"{int(progress * (len(SECTIONS)-1) / 100)} secciones"
            )
        with col2:
            st.metric(
                label="Total",
                value=f"{len(SECTIONS)-1}",
                delta="secciones"
            )
        style_metric_cards(border_left_color="#ED7D31")
        st.sidebar.divider()
    
    st.sidebar.divider()
    
    # Nombre de archivo personalizado
    st.session_state.custom_filename = st.sidebar.text_input(
        "Nombre de archivo (opcional)",
        value=st.session_state.custom_filename,
        placeholder="DMND...",
        key="custom_name"
    )
    
    st.sidebar.divider()
    
    # Opciones de generacion con toggle switch
    st.sidebar.markdown("**Opciones de Salida**")
    use_accordion = st.sidebar.toggle(
        "HTML con acordeones (Loop)",
        value=True,
        key="opt_accordion",
    )
    
    if not use_accordion:
        st.sidebar.info("Se generara HTML completo sin acordeones.")
    
    st.sidebar.divider()
    
    # Logo
    st.sidebar.markdown("**Logo Corporativo**")
    uploaded_logo = st.sidebar.file_uploader(
        "Subir logo (.png)",
        type=['png'],
        key="logo_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_logo is not None:
        st.session_state.uploaded_logo = uploaded_logo
        st.session_state.logo_temp_path = save_uploaded_logo(uploaded_logo)
        st.sidebar.image(uploaded_logo, width=150, caption="Logo cargado")
    
    st.sidebar.divider()
    
    # Botón para cambiar modo (solo si ya se seleccionó uno)
    if st.session_state.modo_seleccionado is not None:
        st.sidebar.divider()
        if st.sidebar.button("Cambiar modo", key="btn_cambiar_modo", use_container_width=True):
            st.session_state.modo_seleccionado = None
            st.rerun()
    
    st.sidebar.divider()
    
    # Info del proyecto
    st.sidebar.markdown("**Generador v1.2**")
    st.sidebar.caption("Herramienta de documentación")
    
    # Determinar modo actual
    modo = st.session_state.modo_seleccionado if st.session_state.modo_seleccionado else "Formulario Web"
    
    return modo, use_accordion


def render_formulario():
    """Renderiza el formulario web con secciones predefinidas."""
    colored_header(
        label="Generador de Análisis Funcional",
        description="Completa las secciones del documento. El formato corporativo se aplicará automáticamente.",
        color_name="orange-70"
    )
    
    # Tabs por sección
    section_titles = [sec['titulo'] for sec in SECTIONS]
    tabs = st.tabs(section_titles)
    
    for idx, (tab, sec_config) in enumerate(zip(tabs, SECTIONS)):
        with tab:
            sec_id = sec_config['id']
            
            # Inicializar datos de sección si no existen
            if sec_id not in st.session_state.sections_data:
                st.session_state.sections_data[sec_id] = {
                    'text': '',
                    'table': None
                }
            
            # Badge de estado
            text_content_check = st.session_state.sections_data[sec_id].get('text', '')
            has_content = len(text_content_check.strip()) > 20 if text_content_check else False
            
            if sec_id != 'portada':
                status_icon = '<i class="bi bi-check-circle-fill" style="color: #22C55E;"></i>' if has_content else '<i class="bi bi-pencil-square" style="color: #ED7D31;"></i>'
                st.caption(f'{status_icon} Sección {"completada" if has_content else "en progreso"}', unsafe_allow_html=True)
            
            # SECCIÓN ESPECIAL: Portada (metadatos)
            if sec_id == 'portada':
                st.info("Completa los datos de la portada del documento.")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.metadata['numero_demanda'] = st.text_input(
                        "Numero de demanda",
                        value=st.session_state.metadata.get('numero_demanda', ''),
                        key="portada_dmnd"
                    )
                with col2:
                    st.session_state.metadata['titulo'] = st.text_input(
                        "Titulo del documento",
                        value=st.session_state.metadata.get('titulo', ''),
                        key="portada_titulo"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.metadata['fecha'] = st.text_input(
                        "Fecha",
                        value=st.session_state.metadata.get('fecha', datetime.now().strftime('%d-%m-%Y')),
                        key="portada_fecha"
                    )
                with col2:
                    st.session_state.metadata['ciclo'] = st.text_input(
                        "Ciclo",
                        value=st.session_state.metadata.get('ciclo', ''),
                        key="portada_ciclo"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.metadata['sistema'] = st.text_input(
                        "Sistema/Modulo",
                        value=st.session_state.metadata.get('sistema', 'COMEX'),
                        key="portada_sistema"
                    )
                with col2:
                    st.session_state.metadata['version'] = st.text_input(
                        "Version",
                        value=st.session_state.metadata.get('version', '1.0'),
                        key="portada_version"
                    )
                
                st.session_state.metadata['autor'] = st.text_input(
                    "Autor",
                    value=st.session_state.metadata.get('autor', ''),
                    key="portada_autor"
                )
                
                # Vista previa del titulo
                dmnd = st.session_state.metadata.get('numero_demanda', '')
                titulo = st.session_state.metadata.get('titulo', '')
                if dmnd and titulo:
                    preview = titulo if dmnd in titulo else f"DMND{dmnd} - {titulo}"
                    st.success(f"Titulo de portada: {preview}")
                
                continue
            
            # Descripción
            st.info(sec_config['descripcion'])
            
            # Editor de texto
            text_key = f"ta_{sec_id}"
            
            # Inicializar el widget key en session_state si no existe
            if text_key not in st.session_state:
                st.session_state[text_key] = st.session_state.sections_data[sec_id].get('text', '')
            
            # Herramientas de formato rápido
            with st.container():
                st.caption("Herramientas rapidas:")
                h_col1, h_col2, h_col3, h_col4 = st.columns(4)
                
                with h_col1:
                    if st.button("Insertar SQL", key=f"btn_sql_{sec_id}"):
                        current = st.session_state[text_key]
                        template = "\n\n```sql\n-- Escribe tu consulta SQL aqui\nSELECT * FROM tabla\nWHERE condicion = 'valor'\n```\n\n"
                        st.session_state[text_key] = current + template
                        st.session_state.sections_data[sec_id]['text'] = st.session_state[text_key]
                        st.rerun()
                
                with h_col2:
                    if st.button("Insertar codigo", key=f"btn_code_{sec_id}"):
                        current = st.session_state[text_key]
                        template = "\n\n```\n// Escribe tu codigo aqui\nfunction ejemplo() {\n    return 'Hola';\n}\n```\n\n"
                        st.session_state[text_key] = current + template
                        st.session_state.sections_data[sec_id]['text'] = st.session_state[text_key]
                        st.rerun()
                
                with h_col3:
                    if st.button("Insertar tabla", key=f"btn_table_md_{sec_id}"):
                        # Mostrar diálogo para configurar tabla
                        st.session_state[f"show_table_dialog_{sec_id}"] = True
                        st.rerun()
                
                with h_col4:
                    if st.button("Limpiar", key=f"btn_clear_{sec_id}"):
                        st.session_state[text_key] = ""
                        st.session_state.sections_data[sec_id]['text'] = ""
                        st.rerun()
            
            # Diálogo de configuración de tabla
            if st.session_state.get(f"show_table_dialog_{sec_id}", False):
                with st.container(border=True):
                    st.subheader("Configurar tabla")
                    cols = st.number_input("Columnas", min_value=1, max_value=10, value=3, key=f"table_cols_{sec_id}")
                    rows = st.number_input("Filas", min_value=1, max_value=20, value=2, key=f"table_rows_{sec_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Insertar", key=f"table_insert_{sec_id}"):
                            # Generar tabla markdown
                            headers = [f"Col{i+1}" for i in range(cols)]
                            header_line = "| " + " | ".join(headers) + " |"
                            separator = "|" + "|".join(["---"] * cols) + "|"
                            
                            data_lines = []
                            for r in range(rows):
                                cells = [f"dato{r+1}-{c+1}" for c in range(cols)]
                                data_lines.append("| " + " | ".join(cells) + " |")
                            
                            template = "\n\n" + header_line + "\n" + separator + "\n" + "\n".join(data_lines) + "\n\n"
                            
                            current = st.session_state[text_key]
                            st.session_state[text_key] = current + template
                            st.session_state.sections_data[sec_id]['text'] = st.session_state[text_key]
                            st.session_state[f"show_table_dialog_{sec_id}"] = False
                            st.rerun()
                    
                    with col2:
                        if st.button("Cancelar", key=f"table_cancel_{sec_id}"):
                            st.session_state[f"show_table_dialog_{sec_id}"] = False
                            st.rerun()
            
            # Editor de texto (sin value=, usa key directamente)
            text_content = st.text_area(
                f"Contenido de {sec_config['titulo']}",
                height=300,
                key=text_key,
                placeholder="Escribe el contenido aqui. Puedes usar markdown:\n\n# Titulo\n## Subtitulo\n**negrita**\n`codigo inline`\n\n```sql\n-- bloque de codigo\nSELECT * FROM tabla\n```\n\n| Col1 | Col2 |\n|------|------|\n| A | B |"
            )
            
            # Guardar en el dict principal
            st.session_state.sections_data[sec_id]['text'] = text_content
            
            # Editor de tabla si corresponde
            if sec_config.get('requiere_tabla', False):
                st.divider()
                
                # Checkbox para incluir/excluir tabla
                # Para Reglas, deshabilitado por defecto (no es un dato recurrente)
                default_include = False if sec_id == 'reglas_desarrollo' else True
                include_table = st.checkbox(
                    "Incluir tabla de estructura",
                    value=st.session_state.sections_data[sec_id].get('include_table', default_include),
                    key=f"include_table_{sec_id}"
                )
                st.session_state.sections_data[sec_id]['include_table'] = include_table
                
                if include_table:
                    st.subheader("Tabla de datos")
                    
                    columns = sec_config.get('columnas_tabla', [])
                    
                    # Obtener tabla actual o crear nueva
                    table_data = st.session_state.sections_data[sec_id].get('table')
                    
                    # HISTORIAL DE VERSIONES - Editor especial
                    if sec_id == 'historial':
                        import pandas as pd
                        
                        if table_data is None or not table_data.get('rows'):
                            # Crear con una sola fila y autocompletar desde metadatos
                            df = pd.DataFrame({col: [''] for col in columns})
                            
                            # Autocompletar Versión desde metadatos
                            version = st.session_state.metadata.get('version', '1.0')
                            if 'Versión' in columns:
                                df.loc[0, 'Versión'] = version
                            if 'Version' in columns:
                                df.loc[0, 'Version'] = version
                            
                            # Autocompletar Autor desde metadatos
                            autor = st.session_state.metadata.get('autor', '')
                            if 'Autor' in columns:
                                df.loc[0, 'Autor'] = autor
                            
                            # Autocompletar Fecha con fecha actual
                            fecha = st.session_state.metadata.get('fecha', '')
                            if 'Fecha' in columns and fecha:
                                df.loc[0, 'Fecha'] = fecha
                            
                            # Autocompletar Número de llamado
                            dmnd = st.session_state.metadata.get('numero_demanda', '')
                            if 'Número de llamado' in columns and dmnd:
                                df.loc[0, 'Número de llamado'] = f"DMND{dmnd}"
                        else:
                            df = pd.DataFrame(
                                table_data.get('rows', []),
                                columns=table_data.get('headers', columns)
                            )
                        
                        # Mostrar tabla
                        st.dataframe(df, width='stretch', hide_index=True)
                        
                        # Botones para agregar/quitar filas
                        col_add, col_remove = st.columns(2)
                        with col_add:
                            if st.button("+ Agregar fila", key=f"add_row_{sec_id}"):
                                new_row = {}
                                for col in columns:
                                    if col == 'Versión' or col == 'Version':
                                        new_row[col] = st.session_state.metadata.get('version', '')
                                    elif col == 'Autor':
                                        new_row[col] = st.session_state.metadata.get('autor', '')
                                    elif col == 'Fecha':
                                        new_row[col] = st.session_state.metadata.get('fecha', '')
                                    elif col == 'Número de llamado':
                                        dmnd = st.session_state.metadata.get('numero_demanda', '')
                                        new_row[col] = f"DMND{dmnd}" if dmnd else ''
                                    else:
                                        new_row[col] = ''
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                                st.session_state.sections_data[sec_id]['table'] = {
                                    'headers': df.columns.tolist(),
                                    'rows': df.values.tolist()
                                }
                                st.rerun()
                        
                        with col_remove:
                            if len(df) > 1:
                                if st.button("- Quitar ultima fila", key=f"remove_row_{sec_id}"):
                                    df = df.iloc[:-1].reset_index(drop=True)
                                    st.session_state.sections_data[sec_id]['table'] = {
                                        'headers': df.columns.tolist(),
                                        'rows': df.values.tolist()
                                    }
                                    st.rerun()
                            else:
                                st.button("- Quitar ultima fila", key=f"remove_row_{sec_id}", disabled=True)
                        
                        # Editor inline de celdas
                        st.markdown("**Editar valores:**")
                        edited_rows = []
                        for idx, row in df.iterrows():
                            cols_ui = st.columns(len(columns))
                            new_row = []
                            for i, col in enumerate(columns):
                                with cols_ui[i]:
                                    if col == 'Fecha':
                                        # Date picker para fechas
                                        val = st.date_input(
                                            col,
                                            value=None,
                                            key=f"hist_date_{sec_id}_{idx}_{i}"
                                        )
                                        new_row.append(str(val) if val else row.get(col, ''))
                                    else:
                                        val = st.text_input(
                                            col,
                                            value=str(row.get(col, '')),
                                            key=f"hist_{sec_id}_{idx}_{i}"
                                        )
                                        new_row.append(val)
                            edited_rows.append(new_row)
                        
                        # Actualizar datos
                        df = pd.DataFrame(edited_rows, columns=columns)
                        st.session_state.sections_data[sec_id]['table'] = {
                            'headers': df.columns.tolist(),
                            'rows': df.values.tolist()
                        }
                    
                    else:
                        # Editor estandar para otras secciones
                        import pandas as pd
                        if table_data is None:
                            df = pd.DataFrame({col: [''] * 3 for col in columns})
                        else:
                            # Usar los headers de la tabla guardada (pueden venir del .md)
                            saved_headers = table_data.get('headers', columns)
                            saved_rows = table_data.get('rows', [])
                            
                            # Si los datos vienen del .md, pueden tener diferentes headers
                            if saved_rows and len(saved_headers) != len(columns):
                                # Crear DataFrame con los headers del archivo .md
                                df = pd.DataFrame(saved_rows, columns=saved_headers)
                            else:
                                df = pd.DataFrame(saved_rows, columns=columns)
                                # Rellenar con filas vacias si es necesario
                                while len(df) < 3:
                                    df = pd.concat([df, pd.DataFrame([{col: '' for col in columns}])], ignore_index=True)
                        
                        edited_df = st.data_editor(
                            df,
                            num_rows="dynamic",
                            key=f"table_{sec_id}"
                        )
                        
                        # Guardar tabla
                        if not edited_df.empty:
                            st.session_state.sections_data[sec_id]['table'] = {
                                'headers': edited_df.columns.tolist(),
                                'rows': edited_df.values.tolist()
                            }
                    
                    # Ayuda para markdown de tabla
                    with st.expander("Ver tabla en Markdown"):
                        from engine.table_editor import dataframe_to_markdown
                        current_df = pd.DataFrame(
                            st.session_state.sections_data[sec_id]['table']['rows'],
                            columns=st.session_state.sections_data[sec_id]['table']['headers']
                        )
                        st.code(dataframe_to_markdown(current_df), language="markdown")
    
    # Botón de generación
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        use_accordion_opt = st.session_state.get('opt_accordion', True)
        if st.button("Generar Documentos", type="primary"):
            if not st.session_state.metadata.get('numero_demanda'):
                st.error("[ATENCION] Debes ingresar el número de demanda")
                return
            
            with st.spinner("Generando documentos..."):
                try:
                    docx_path, html_path, html_full_path, zip_path, output_dir = generate_documents(
                        use_accordion=use_accordion_opt
                    )
                    
                    st.success("[OK] Documentos generados correctamente!")
                    
                    # Mostrar descargas
                    cols_download = st.columns(4 if html_full_path else 3)
                    
                    with cols_download[0]:
                        with open(docx_path, "rb") as f:
                            st.download_button(
                                label="Descargar DOCX",
                                data=f.read(),
                                file_name=os.path.basename(docx_path),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    
                    with cols_download[1]:
                        with open(html_path, "rb") as f:
                            label_html = "HTML Acordeones" if html_full_path else "Descargar HTML"
                            st.download_button(
                                label=label_html,
                                data=f.read(),
                                file_name=os.path.basename(html_path),
                                mime="text/html"
                            )
                    
                    if html_full_path:
                        with cols_download[2]:
                            with open(html_full_path, "rb") as f:
                                st.download_button(
                                    label="HTML Completo",
                                    data=f.read(),
                                    file_name=os.path.basename(html_full_path),
                                    mime="text/html"
                                )
                    
                    with cols_download[-1]:
                        with open(zip_path, "rb") as f:
                            st.download_button(
                                label="Descargar ZIP",
                                data=f.read(),
                                file_name=os.path.basename(zip_path),
                                mime="application/zip"
                            )
                    
                    # Vista previa HTML (usar el acordeón por defecto o completo según preferencia)
                    st.divider()
                    preview_path = html_path if use_accordion_opt else (html_full_path or html_path)
                    st.subheader("Vista Previa")
                    with open(preview_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Mostrar en iframe
                    st.components.v1.html(html_content, height=600, scrolling=True)
                    
                except Exception as e:
                    st.error(f"[ERROR] Error al generar documentos: {str(e)}")
                    raise


def render_upload_mode():
    """Renderiza el modo de subir archivos markdown."""
    st.title("Subir Archivos Markdown")
    st.caption("Sube tu archivo .md para generar el documento automaticamente.")
    
    uploaded_files = st.file_uploader(
        "Subir archivo Markdown",
        type=['md'],
        accept_multiple_files=False,
        key="md_files"
    )
    
    if uploaded_files:
        content = uploaded_files.getvalue().decode('utf-8')
        
        with st.expander("Vista previa del contenido"):
            st.code(content[:500] + "..." if len(content) > 500 else content, language="markdown")
        
        # Boton para parsear archivo
        if st.button("Parsear Archivo", type="primary", key="parse_md_btn"):
            try:
                with st.spinner("Parseando archivo..."):
                    # Parsear archivo
                    metadata, parsed_sections = MarkdownParser.parse_file(content)
                    
                    # Actualizar metadata en session
                    st.session_state.metadata.update(metadata)
                    
                    # Mapear secciones a formato del formulario
                    mapped_sections = MarkdownParser.map_to_predefined_sections(parsed_sections)
                    
                    # Guardar en session_state
                    for sec_id, data in mapped_sections.items():
                        if sec_id not in st.session_state.sections_data:
                            st.session_state.sections_data[sec_id] = {}
                        st.session_state.sections_data[sec_id]['text'] = data['text']
                        st.session_state.sections_data[sec_id]['table'] = data['table']
                        st.session_state.sections_data[sec_id]['include_table'] = data['include_table']
                        
                        # Sincronizar text_area widgets
                        text_key = f"ta_{sec_id}"
                        st.session_state[text_key] = data['text']
                    
                    # Marcar como parseado
                    st.session_state.md_parsed = True
                    st.session_state.md_sections_count = len(parsed_sections)
                    st.rerun()
            
            except Exception as e:
                st.error(f"[ERROR] Error al parsear archivo: {str(e)}")
                st.session_state.md_parsed = False
        
        # Si ya fue parseado, mostrar resumen y boton de generar
        if st.session_state.get('md_parsed', False):
            st.success("[OK] Archivo parseado exitosamente!")
            st.info(f"Secciones encontradas: {st.session_state.md_sections_count}")
            
            # Mostrar resumen
            st.subheader("Resumen del documento")
            meta = st.session_state.metadata
            st.json({
                "Titulo": meta.get('titulo'),
                "DMND": meta.get('numero_demanda'),
                "Autor": meta.get('autor')
            })
            
            # Boton separado para generar documentos
            st.divider()
            if st.button("Generar DOCX y HTML", type="primary", key="gen_from_md_btn"):
                try:
                    with st.spinner("Generando documentos..."):
                        docx_path, html_path, html_full_path, zip_path, output_dir = generate_documents(
                            use_accordion=st.session_state.get('opt_accordion', True)
                        )
                        
                        st.session_state.generated_files = {
                            'docx': docx_path,
                            'html': html_path,
                            'zip': zip_path
                        }
                        st.success("[OK] Documentos generados!")
                        st.rerun()
                except Exception as e:
                    st.error(f"[ERROR] Error al generar: {str(e)}")
            
            # Mostrar descargas si existen archivos generados
            if st.session_state.get('generated_files'):
                files = st.session_state.generated_files
                st.divider()
                st.subheader("Descargas")
                
                col_d1, col_d2, col_d3 = st.columns(3)
                
                with col_d1:
                    with open(files['docx'], "rb") as f:
                        st.download_button(
                            label="Descargar DOCX",
                            data=f.read(),
                            file_name=os.path.basename(files['docx']),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                
                with col_d2:
                    with open(files['html'], "rb") as f:
                        st.download_button(
                            label="Descargar HTML",
                            data=f.read(),
                            file_name=os.path.basename(files['html']),
                            mime="text/html"
                        )
                
                with col_d3:
                    with open(files['zip'], "rb") as f:
                        st.download_button(
                            label="Descargar ZIP",
                            data=f.read(),
                            file_name=os.path.basename(files['zip']),
                            mime="application/zip"
                        )


def render_skeleton():
    """Muestra skeleton loaders mientras la app inicializa."""
    skeleton_html = """
    <style>
    .skeleton-container {
        padding: 1rem 0;
    }
    .skeleton-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .skeleton-col {
        flex: 1;
    }
    .skeleton-block {
        background: linear-gradient(90deg, var(--skeleton-bg) 25%, var(--skeleton-highlight) 50%, var(--skeleton-bg) 75%);
        background-size: 200% 100%;
        animation: skeleton-shimmer 1.5s infinite;
        border-radius: 8px;
        width: 100%;
    }
    .skeleton-title {
        height: 32px;
        width: 60%;
        margin-bottom: 1.5rem;
    }
    .skeleton-tab-row {
        display: flex;
        gap: 4px;
        margin-bottom: 1rem;
        background: rgba(128,128,128,0.08);
        padding: 6px;
        border-radius: 12px;
    }
    .skeleton-tab {
        height: 40px;
        flex: 1;
        border-radius: 8px;
    }
    .skeleton-input {
        height: 48px;
    }
    .skeleton-textarea {
        height: 120px;
    }
    .skeleton-button {
        height: 48px;
        width: 200px;
        margin-top: 1rem;
    }
    </style>
    <div class="skeleton-container">
        <div class="skeleton-block skeleton-title"></div>
        <div class="skeleton-tab-row">
            <div class="skeleton-block skeleton-tab"></div>
            <div class="skeleton-block skeleton-tab"></div>
            <div class="skeleton-block skeleton-tab"></div>
        </div>
        <div class="skeleton-row">
            <div class="skeleton-col">
                <div class="skeleton-block skeleton-input" style="margin-bottom: 1rem;"></div>
            </div>
            <div class="skeleton-col">
                <div class="skeleton-block skeleton-input" style="margin-bottom: 1rem;"></div>
            </div>
        </div>
        <div class="skeleton-block skeleton-textarea"></div>
        <div class="skeleton-block skeleton-textarea"></div>
        <div class="skeleton-block skeleton-button"></div>
    </div>
    """
    st.markdown(skeleton_html, unsafe_allow_html=True)


def main():
    """Función principal."""
    import time
    
    # Cargar CSS custom antes de todo
    load_custom_css()
    
    init_session_state()
    
    # Skeleton loader en carga inicial (solo una vez por sesión)
    if 'app_loaded' not in st.session_state:
        placeholder = st.empty()
        with placeholder.container():
            render_skeleton()
        time.sleep(0.8)
        placeholder.empty()
        st.session_state.app_loaded = True
        st.rerun()
    
    # Si no hay modo seleccionado, mostrar welcome screen
    if st.session_state.modo_seleccionado is None:
        # Sidebar minimal en welcome screen
        st.sidebar.markdown("### Generador")
        st.sidebar.caption("Análisis Funcional")
        st.sidebar.divider()
        st.sidebar.info("Seleccioná un modo de trabajo para comenzar.")
        
        render_welcome_screen()
        return
    
    # Renderizar sidebar completo
    modo, _ = render_sidebar()
    
    # Renderizar contenido principal según modo
    if modo == "Formulario Web":
        render_formulario()
    else:
        render_upload_mode()


if __name__ == "__main__":
    main()
