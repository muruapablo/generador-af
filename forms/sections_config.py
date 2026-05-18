"""
Configuración de secciones predefinidas para el Análisis Funcional.
Cada sección define su título, descripción y si requiere editor de tablas.
"""

SECTIONS = [
    {
        "id": "portada",
        "titulo": "Portada",
        "descripcion": "Metadatos del documento: DMND, título, fecha, ciclo, sistema, versión, autor.",
        "requiere_tabla": False,
        "es_metadatos": True
    },
    {
        "id": "indice",
        "titulo": "Índice",
        "descripcion": "Índice automático de secciones del documento.",
        "requiere_tabla": False,
        "es_indice": True
    },
    {
        "id": "info_general",
        "titulo": "Información General",
        "descripcion": "Título agrupador de las secciones del análisis funcional.",
        "requiere_tabla": False,
        "es_titulo_agrupador": True,
        "subsecciones": ["historial", "necesidad", "objetivos", "descripcion_actividades", "reglas_desarrollo", "criterios_aceptacion", "aprobaciones"]
    },
    {
        "id": "historial",
        "titulo": "1. Historial de Versiones",
        "descripcion": "Registro de cambios y versiones del documento.",
        "requiere_tabla": True,
        "columnas_tabla": ["Versión", "Comentario", "Número de llamado", "Fecha", "Autor"],
        "grupo": "Información General"
    },
    {
        "id": "necesidad",
        "titulo": "2. Necesidad",
        "descripcion": "Descripción de la necesidad de negocio que motiva el desarrollo.",
        "requiere_tabla": False,
        "grupo": "Información General"
    },
    {
        "id": "objetivos",
        "titulo": "3. Objetivos y Condiciones",
        "descripcion": "Objetivos del desarrollo y condiciones que debe cumplir.",
        "requiere_tabla": False,
        "grupo": "Información General"
    },
    {
        "id": "descripcion_actividades",
        "titulo": "4. Descripción de las Actividades",
        "descripcion": "Flujo de operación actual y propuesto, actividades detalladas.",
        "requiere_tabla": False,
        "grupo": "Información General"
    },
    {
        "id": "reglas_desarrollo",
        "titulo": "5. Reglas para el Desarrollo",
        "descripcion": "Reglas técnicas y funcionales. Incluye definición de endpoints, SQL, estructuras de datos.",
        "requiere_tabla": True,
        "columnas_tabla": ["Nº do Campo", "Campo", "Início", "Fin", "Tamaño", "Formato", "Dígitos decimales", "Observaciones", "Ejemplo"],
        "grupo": "Información General"
    },
    {
        "id": "criterios_aceptacion",
        "titulo": "6. Criterios de Aceptación",
        "descripcion": "Condiciones que deben cumplirse para dar por aceptado el desarrollo.",
        "requiere_tabla": False,
        "grupo": "Información General"
    },
    {
        "id": "aprobaciones",
        "titulo": "7. Aprobaciones",
        "descripcion": "Espacio para registro de aprobaciones del documento.",
        "requiere_tabla": False,
        "grupo": "Información General"
    }
]

# Metadatos por defecto
DEFAULT_METADATA = {
    "numero_demanda": "",
    "titulo": "",
    "fecha": "",
    "ciclo": "",
    "sistema": "COMEX",
    "version": "1.0",
    "autor": "",
    "nombre_archivo": ""
}
