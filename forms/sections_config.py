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
        "descripcion": "Contexto, alcance y descripción general del análisis funcional.",
        "requiere_tabla": False
    },
    {
        "id": "historial",
        "titulo": "Historial de Versiones",
        "descripcion": "Registro de cambios y versiones del documento.",
        "requiere_tabla": True,
        "columnas_tabla": ["Versión", "Comentario", "Número de llamado", "Fecha", "Autor"]
    },
    {
        "id": "necesidad",
        "titulo": "Necesidad",
        "descripcion": "Descripción de la necesidad de negocio que motiva el desarrollo.",
        "requiere_tabla": False
    },
    {
        "id": "objetivos",
        "titulo": "Objetivos y Condiciones",
        "descripcion": "Objetivos del desarrollo y condiciones que debe cumplir.",
        "requiere_tabla": False
    },
    {
        "id": "descripcion_actividades",
        "titulo": "Descripción de las Actividades",
        "descripcion": "Flujo de operación actual y propuesto, actividades detalladas.",
        "requiere_tabla": False
    },
    {
        "id": "reglas_desarrollo",
        "titulo": "Reglas para el Desarrollo",
        "descripcion": "Reglas técnicas y funcionales. Incluye definición de endpoints, SQL, estructuras de datos.",
        "requiere_tabla": True,
        "columnas_tabla": ["Nº do Campo", "Campo", "Início", "Fin", "Tamaño", "Formato", "Dígitos decimales", "Observaciones", "Ejemplo"]
    },
    {
        "id": "criterios_aceptacion",
        "titulo": "Criterios de Aceptación",
        "descripcion": "Condiciones que deben cumplirse para dar por aceptado el desarrollo.",
        "requiere_tabla": False
    },
    {
        "id": "aprobaciones",
        "titulo": "Aprobaciones",
        "descripcion": "Espacio para registro de aprobaciones del documento.",
        "requiere_tabla": False
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
