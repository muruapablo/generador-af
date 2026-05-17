# Contexto del Proyecto: Generador de Análisis Funcional

> **Instrucciones para agentes de IA**: Este archivo contiene todo el contexto necesario para entender, mantener y escalar este proyecto. Leerlo completamente antes de realizar cualquier cambio.

---

## 1. Descripción y Propósito

Este proyecto es un **generador de documentos de análisis funcional** diseñado para un analista funcional que trabaja con el sistema **COMEX** (comercio exterior).

**Problema que resuelve:**
- Los análisis funcionales se creaban manualmente en Word y se guardaban en SharePoint.
- Cada documento requería aplicar formato manual: encabezado/pie de página, tipografías específicas, tablas de estructuras, bloques de código SQL con fondo negro, secciones colapsables, etc.
- Esto consumía mucho tiempo en formato en lugar de en contenido.

**Solución:**
Una aplicación web (Streamlit) que permite:
1. Escribir el contenido del análisis funcional en formularios web o subir archivos Markdown.
2. Generar automáticamente tres salidas:
   - **DOCX**: Documento Word con plantilla corporativa completa (header con "COMEX | DOCUMENTO FUNCIONAL", footer con DMND/fecha/página, estilos, tablas, código con fondo negro).
   - **HTML (Loop)**: Página web con acordeones colapsables, bloques de código estilizados, botón "Copiar sección" para pegar fácilmente en **Microsoft Loop**.
   - **HTML (Completo)**: Versión plana sin acordeones, ideal para leer completo o imprimir.

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión Mínima | Propósito |
|------------|-----------|----------------|-----------|
| Lenguaje | Python | 3.10+ | Backend y lógica de generación |
| Framework Web | Streamlit | 1.40.0+ | Interfaz de usuario web |
| Generación DOCX | python-docx | 1.1.2+ | Crear documentos Word programáticamente |
| Generación HTML | Jinja2 | 3.1.4+ | Templates HTML con acordeones |
| Parseo Markdown | markdown | 3.7+ | Convertir Markdown a HTML |
| Manipulación Datos | pandas | 2.2.0+ | Editor de tablas visual |
| Imágenes | Pillow | 10.4.0+ | Procesamiento del logo |
| Serialización | PyYAML | 6.0.2+ | Metadatos en YAML (futuro) |

**NOTA:** Pandoc NO está instalado actualmente. La generación es 100% nativa con Python para evitar dependencias externas.

---

## 3. Arquitectura de Carpetas

```
C:\Proyectos\generador-af\
├── AGENTS.md                     # Este archivo (contexto para IA)
├── README.md                     # Documentación de usuario
├── app.py                        # Interfaz Streamlit (punto de entrada)
├── requirements.txt              # Dependencias Python
├── engine/                       # Motores de generación (lógica pura)
│   ├── __init__.py
│   ├── docx_generator.py         # Motor DOCX: logo, estilos, código, tablas
│   ├── html_generator.py         # Motor HTML: acordeones, copiar, Loop CSS
│   ├── markdown_parser.py        # Parser de Markdown a estructura de datos
│   └── table_editor.py           # Utilidades para tablas (DataFrame <-> Markdown)
├── forms/                        # Configuración de formularios
│   ├── __init__.py
│   └── sections_config.py        # 10 secciones predefinidas del análisis funcional
├── assets/                       # Recursos estáticos
│   └── loop.css                  # Estilos CSS para la versión HTML/Loop
└── generated/                    # OUTPUT de documentos generados
    └── {DMNDXXXXX}/
        ├── DMNDXXXXX.docx
        ├── DMNDXXXXX.html
        └── DMNDXXXXX.zip
```

---

## 4. Cómo Ejecutar

### Instalación inicial
```bash
cd C:\Proyectos\generador-af
pip install -r requirements.txt
```

### Ejecutar la aplicación
```bash
streamlit run app.py
```

Se abre automáticamente en el navegador en `http://localhost:8501`.

---

## 5. Flujo de Datos

```
Usuario (Streamlit)
  ├── Sidebar: Metadatos + Logo upload
  ├── Tabs: 10 secciones predefinidas
  │   ├── Texto libre (Markdown)
  │   └── Tablas visuales (st.data_editor de Pandas)
  └── Botón "Generar Documentos"
        │
        ▼
    [app.py] ──▶ engine/markdown_parser.py
        │
        ├──▶ engine/docx_generator.py ──▶ .docx (plantilla corporativa)
        └──▶ engine/html_generator.py ──▶ .html (acordeones + Loop CSS)
        │
        ▼
    generated/{nombre}/ (DOCX + HTML + ZIP)
```

---

## 6. Estructura del Documento (Secciones Predefinidas)

Las secciones están definidas en `forms/sections_config.py`. **NO modificar los IDs** sin actualizar también los generadores.

| ID | Título | Tabla | Especial |
|---|---|---|---|
| `portada` | Portada | No | Metadatos (se renderiza aparte) |
| `indice` | Índice | No | Auto-generado |
| `info_general` | Información General | No | Texto libre |
| `historial` | Historial de Versiones | **Sí** | Columnas: Versión, Comentario, DMND, Fecha, Autor |
| `necesidad` | Necesidad | No | Texto libre |
| `objetivos` | Objetivos y Condiciones | No | Texto libre |
| `descripcion_actividades` | Descripción de las Actividades | No | Texto libre |
| `reglas_desarrollo` | Reglas para el Desarrollo | **Sí** | Columnas: Nº Campo, Campo, Inicio, Fin, Tamaño, Formato, Decimales, Observaciones, Ejemplo |
| `criterios_aceptacion` | Criterios de Aceptación | No | Texto libre |
| `aprobaciones` | Aprobaciones | No | Texto libre |

**Regla:** Si se agrega una nueva sección, debe seguir el mismo patrón de diccionario con `id`, `titulo`, `descripcion`, `requiere_tabla` (bool), y opcionalmente `columnas_tabla` (list).

---

## 7. Convenciones de Código

### Estilo General
- **Python**: PEP 8, docstrings en español (el usuario es hispanohablante).
- **Nombres**: `snake_case` para variables/funciones, `PascalCase` para clases.
- **Imports**: Agrupados en orden: stdlib, terceros, locales.

### Patrones de Arquitectura
- **Separación de responsabilidades**: `app.py` solo maneja UI. Toda la lógica de generación está en `engine/`.
- **Módulos reutilizables**: Cada generador (DOCX, HTML) es una clase independiente que puede instanciarse y usarse sin Streamlit.
- **Configuración centralizada**: Las secciones del formulario viven en `forms/`, no hardcodeadas en `app.py`.

### Manejo de Estado (Streamlit)
- Usar `st.session_state` para persistir datos entre interacciones.
- Keys de session_state:
  - `metadata`: dict con campos del formulario de metadatos.
  - `sections_data`: dict anidado `{section_id: {text: "", table: {headers: [], rows: []}}}`.
  - `uploaded_logo` / `logo_temp_path`: manejo del logo subido.
  - `custom_filename`: sobrescribe el nombre automático `DMND{numero}`.

---

## 8. Decisiones Técnicas Clave

### ¿Por qué python-docx y no Pandoc?
- Pandoc no está instalado en el entorno del usuario.
- python-docx ofrece control granular sobre estilos, tablas, celdas con shading (fondo de color), imágenes en headers, etc.
- Evita dependencia externa.

### ¿Por qué Jinja2 para HTML?
- Plantillas limpias y mantenibles.
- Facilita insertar CSS inline, acordeones HTML5 nativos (`<details>/<summary>`), y scripts JavaScript para "Copiar sección".

### ¿Por qué acordeones con `<details>/<summary>`?
- Son nativos de HTML5, no requieren JavaScript para funcionar.
- Funcionan perfectamente al copiar y pegar en **Microsoft Loop** (Loop respeta la estructura de detalles/summary).
- Se mantienen **colapsados por defecto** para facilitar la navegación en documentos largos.

### ¿Por qué Streamlit?
- Despliegue ultra-rápido sin necesidad de frontend complejo (React, Vue, etc.).
- El usuario es analista funcional, no desarrollador frontend. Streamlit es suficiente para formularios y data editors.

### Header/Footer en DOCX
- Se implementa con **tablas** dentro del header/footer (como en el documento original).
- Header: Tabla 1x2 con "COMEX" (izquierda) y "DOCUMENTO FUNCIONAL" (derecha).
- Footer: Tabla 1x3 con DMND+título (izquierda), fecha (centro), número de página (derecha, campo dinámico `PAGE`).

### Editor enriquecido en Streamlit
- Streamlit no tiene editor WYSIWYG nativo. La solución usa **botones de herramientas** que insertan templates markdown al final del text_area.
- El usuario hace clic en "Insertar SQL" y se añade un bloque ```sql ... ``` listo para completar.
- Se usa `st.rerun()` para forzar la actualización del text_area con el nuevo contenido.

### HTML Doble Salida
- Se generan **dos HTML**: uno con acordeones (`{nombre}.html`) y otro plano (`{nombre}_completo.html`).
- El usuario puede elegir en el sidebar cuál quiere como principal.
- Ambos se incluyen en el ZIP.

---

## 9. Cómo Escalar / Agregar Funcionalidades

### A. Agregar una nueva sección al formulario
1. Editar `forms/sections_config.py`.
2. Añadir un nuevo dict a la lista `SECTIONS` con `id`, `titulo`, `descripcion`, `requiere_tabla`.
3. Si requiere tabla, definir `columnas_tabla`.
4. No es necesario tocar `app.py` ni los generadores: el loop `for sec in SECTIONS` los detecta automáticamente.

### B. Agregar un nuevo campo de metadatos
1. Añadir el campo a `DEFAULT_METADATA` en `forms/sections_config.py`.
2. Añadir el widget correspondiente en `render_sidebar()` de `app.py`.
3. Asegurar que `docx_generator.py` y `html_generator.py` lo lean del dict `metadata`.

### C. Modificar estilos del HTML (Loop)
- Editar únicamente `assets/loop.css`.
- Probar copiando el HTML generado a Microsoft Loop para verificar compatibilidad.

### D. Modificar estilos del DOCX
- Editar `engine/docx_generator.py`, método `setup_styles()`.
- Para cambiar colores de tablas, buscar los `parse_xml` de shading (`w:fill`).
- Para cambiar fuentes, modificar las propiedades `font.name` y `font.size`.

### E. Agregar un nuevo modo de entrada (ej: importar desde JSON)
1. Crear un nuevo módulo en `engine/` (ej: `json_importer.py`).
2. Añadir opción en el `radio` del sidebar en `app.py`.
3. Mantener la misma estructura de salida: `sections_data` + `metadata`.

### F. Soporte para múltiples plantillas DOCX
- Actualmente se crea la plantilla desde cero en cada ejecución.
- Para soportar múltiples plantillas: añadir un `file_uploader` para `.docx` de plantilla y usar `Document(plantilla_path)` como base en `DOCXGenerator`.

---

## 10. Metadatos del Proyecto

| Campo | Valor |
|---|---|
| Nombre del proyecto | Generador de Análisis Funcional |
| Sistema objetivo | COMEX (Comercio Exterior) |
| Usuario final | Analista Funcional |
| Plataforma de destino DOCX | SharePoint / Microsoft Word |
| Plataforma de destino HTML | Microsoft Loop |
| Entorno de desarrollo | Windows (python 3.13) |
| Ruta del proyecto | `C:\Proyectos\generador-af` |
| Repositorio Git | No inicializado aún (pendiente si se desea) |

---

## 11. TODOs y Mejoras Futuras Identificadas

### Alta Prioridad
- [ ] **Modo "Subir Archivos"**: Actualmente muestra advertencia "en desarrollo". Implementar parser de múltiples `.md` y metadata desde YAML frontmatter.
- [ ] **Editor de tablas mejorado**: Validación de tipos (ej: Inicio/Fin deben ser numéricos), autocalcular columna "Tamaño".
- [ ] **Vista previa en tiempo real**: Mostrar el renderizado HTML mientras se escribe, no solo al final.

### Media Prioridad
- [ ] **Persistencia local**: Guardar borradores automáticamente en `generated/drafts/{timestamp}.json` para recuperar sesiones.
- [ ] **Importar documentos Word existentes**: Script para extraer contenido de `.docx` actuales y convertirlos a este formato.
- [ ] **Soporte para Pandoc opcional**: Si Pandoc está instalado, usarlo para mejor calidad de conversión Markdown → DOCX.

### Baja Prioridad
- [ ] **Autenticación**: Login básico si se despliega en red compartida.
- [ ] **Historial de versiones del generador**: Registrar qué cambios se hicieron en cada documento generado.
- [ ] **Plantillas múltiples**: Permitir elegir entre distintos estilos corporativos (no solo COMEX).

---

## 12. Reglas Críticas para Agentes de IA

**ANTES de modificar cualquier archivo, verificar:**

1. **NO romper la estructura de `sections_data`**: Debe mantenerse como `{section_id: {text: str, table: {headers: list, rows: list}}}`.
2. **NO cambiar IDs de secciones existentes** sin migrar referencias en `docx_generator.py` y `html_generator.py`.
3. **NO instalar dependencias sin actualizar `requirements.txt`**.
4. **Mantener compatibilidad con Microsoft Loop**: El HTML debe seguir usando `<details>/<summary>` nativos y CSS inline o en `<style>`.
5. **Probar siempre ambas salidas**: después de cualquier cambio, generar un DOCX y un HTML para verificar que no se rompieron.
6. **Las rutas deben usar `os.path.join`** y ser relativas a `__file__` para que funcionen en cualquier sistema.

---

## 13. Ejemplo de Uso Rápido (para testing)

Si necesitas probar el generador sin levantar Streamlit:

```python
# Ejecutar desde C:\Proyectos\generador-af
import sys
sys.path.insert(0, r'C:\Proyectos\generador-af')

from engine.docx_generator import DOCXGenerator
from engine.html_generator import HTMLGenerator

metadata = {
    'numero_demanda': '5158443',
    'titulo': 'Reportes automáticos DATA LAKE',
    'fecha': '10-04-2026',
    'ciclo': '104',
    'sistema': 'COMEX',
    'version': '1',
    'autor': 'Ronald Petrussa'
}

sections = [
    {'id': 'necesidad', 'title': 'Necesidad', 'text': 'Es necesario...', 'table': None},
    {'id': 'reglas_desarrollo', 'title': 'Reglas para el Desarrollo', 'text': 'Reglas...', 
     'table': {'headers': ['Campo'], 'rows': [['Cod movimiento']]}},
]

DOCXGenerator().generate(metadata, sections, r'C:\Proyectos\generador-af\generated\test.docx')
HTMLGenerator().generate(metadata, sections, r'C:\Proyectos\generador-af\generated\test.html')
```

---

## 14. Contacto y Contexto del Usuario

- **Rol del usuario**: Analista Funcional de sistema COMEX (comercio exterior).
- **Flujo actual**: Word → SharePoint. El usuario quiere automatizar el formato para enfocarse en el contenido.
- **Destinos**: DOCX para archivo formal, HTML para compartir en **Microsoft Loop**.
- **Preferencias de formato**: Bloques de código SQL con fondo negro, tipografía Consolas para código, tablas corporativas con bordes definidos, acordeones clickeables.

---

> **Nota final para agentes:** Este proyecto está en etapa MVP (Minimum Viable Product). La prioridad es estabilidad y facilidad de uso para un usuario no técnico. Cualquier cambio debe ser intuitivo y bien documentado.
