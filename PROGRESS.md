# Generador AF - Avances y Estado Actual

**Versión actual:** v1.5  
**Última actualización:** 17-05-2026  
**Estado:** En desarrollo activo

---

## Funcionalidades Implementadas

### Core
- [x] Generador de Análisis Funcional para COMEX (ahora genérico)
- [x] Generación de documentos DOCX con plantilla corporativa
- [x] Generación de HTML con acordeones (compatible con Microsoft Loop)
- [x] Generación de HTML completo (sin acordeones)
- [x] Exportación a Markdown (.md) nativo
- [x] Parser de archivos Markdown (.md) para importación
- [x] ZIP con todos los formatos (DOCX + HTML + MD)

### UI/UX Mejoras
- [x] **Welcome Screen** - Selección inicial de modo (Formulario Web / Subir Archivos)
- [x] **Modo oscuro automático** - Detecta preferencia del sistema operativo
- [x] **Sidebar compacta** - Sin scroll, espacio optimizado
- [x] **Skeleton loaders** - Animación shimmer al cargar la app
- [x] **Animaciones suaves** - Fade + slide en tabs (0.3s)
- [x] **Iconos Bootstrap** - Reemplazaron emojis genéricos
- [x] **Progress bar nativo** - Reemplazó metric cards problemáticas con dark mode
- [x] **Header nativo** con `st.header(..., divider="orange")` (colored_header deprecado removido)

### Estructura de Documento
- [x] **Portada** - Metadatos (DMND, título, fecha, ciclo, sistema, versión, autor)
- [x] **Índice** - Autogenerado, vista previa de secciones completadas
- [x] **Información General** - Dashboard con cards de estado de las 7 subsecciones
- [x] **Historial de Versiones** - Solo tabla editable (sin campo de texto)
- [x] **Necesidad** - Editor de texto con herramientas rápidas
- [x] **Objetivos y Condiciones** - Editor de texto
- [x] **Descripción de las Actividades** - Editor de texto (requiere código/bloques)
- [x] **Reglas para el Desarrollo** - Editor + tabla (requiere código o tabla)
- [x] **Criterios de Aceptación** - Editor de texto
- [x] **Aprobaciones** - Editor de texto

### Lógica de Progreso
- [x] **Cálculo inteligente** - Excluye Portada, Índice e Información General
- [x] **7 secciones editables** contabilizadas para el progreso
- [x] **Secciones técnicas** (Reglas, Descripción) requieren bloques de código o tabla para marcar como completadas
- [x] **Badge de estado** en cada pestaña (completada/en progreso)
- [x] **Detección de contenido** - Texto >20 chars O tabla con filas O bloques de código

### Editor desde .md
- [x] **Parseo de archivos .md** con metadatos y secciones
- [x] **Mapeo automático** a secciones predefinidas
- [x] **Editor visual post-parseo** - Botón "Editar contenido parseado"
- [x] **Sincronización** de widgets con datos parseados

---

## Arquitectura Técnica

### Stack
- **Frontend:** Streamlit 1.57.0
- **Librerías UI:** streamlit-option-menu, streamlit-extras, stqdm
- **DOCX:** python-docx 1.1.2
- **HTML:** Jinja2 3.1.4 + markdown
- **Datos:** Pandas 2.2.0
- **Deploy:** Streamlit Community Cloud + GitHub

### Archivos Clave
```
generador-af/
├── app.py                          # App principal (1199 líneas)
├── engine/
│   ├── docx_generator.py           # Generador DOCX corporativo
│   ├── html_generator.py           # Generador HTML (acordeones/full)
│   ├── md_parser.py                # Parser Markdown
│   ├── markdown_parser.py          # Parser Markdown texto
│   └── table_editor.py             # Utilidades de tablas
├── forms/
│   └── sections_config.py          # Configuración de 10 secciones
├── assets/
│   ├── loop.css                    # CSS para Loop
│   └── streamlit_custom.css        # Estilos custom (animaciones, skeletons)
├── .streamlit/
│   └── config.toml                 # Config (sin tema custom para dark mode)
└── requirements.txt                # Dependencias
```

### Configuración importante
- **config.toml** NO tiene sección `[theme]` para permitir modo oscuro automático
- CSS custom NO fuerza colores de fondo/texto (respeta tema del sistema)
- `primaryColor` eliminado - usa colores default de Streamlit

---

## Problemas Conocidos / Pendientes

### Bugs a verificar
- [ ] Verificar que al parsear .md, el contenido se muestra correctamente en todas las pestañas del editor
- [ ] Confirmar que secciones vacías post-parseo no marcan como "completadas" incorrectamente
- [ ] Revisar que el date picker de Portada funciona correctamente en modo oscuro

### Mejoras futuras sugeridas
- [ ] **Templates/Pre-sets** de documentos (vacío, estructura base, desarrollo SQL, fix de bug)
- [ ] **Autosave** de borradores en session_state + archivo JSON temporal
- [ ] **Importar/Exportar proyecto JSON** para backup/compartir
- [ ] **Validación de campos** (DMND numérico, fechas con formato válido)
- [ ] **Historial de versiones del documento** (snapshots, diff)
- [ ] **Dashboard de documentos** generados (lista filtrable por fecha/sistema/autor)
- [ ] **Tooltips explicativos** en cada campo (qué va en "Ciclo", qué es "DMND")
- [ ] **Animaciones** skeleton al cambiar de modo (Formulario ↔ Archivos)
- [ ] **Vista previa en tiempo real** - split screen editor + HTML renderizado

### UX Pendiente
- [ ] Revisar contraste de cards en modo oscuro (dashboard de Información General)
- [ ] Ajustar tamaño de sidebar en modo oscuro (algunos elementos pueden quedar cortados)
- [ ] Considerar agregar toggle manual de tema claro/oscuro en sidebar

---

## Notas de Implementación

### Dark Mode
Para que funcione el modo oscuro automático, fue necesario:
1. Eliminar toda sección `[theme]` del `config.toml`
2. Quitar `backgroundColor`, `textColor`, `secondaryBackgroundColor` hardcodeados
3. Eliminar `colored_header` deprecado de streamlit-extras
4. Usar `st.header(..., divider="orange")` nativo
5. CSS custom solo ajusta acentos, NO fuerza fondos ni textos

### Reglas de Progreso
- **Secciones técnicas** (`reglas_desarrollo`, `descripcion_actividades`):  
  Requieren bloque de código (```) o tabla con filas para marcar como completadas
- **Secciones de texto** (Necesidad, Objetivos, Criterios, Aprobaciones):  
  Texto >20 caracteres o tabla es suficiente
- **Historial**: Solo tabla (sin campo de texto)

### Parseo de .md
- Formato esperado: `# DMND123 - Título` + `## Metadatos` + `## Secciones`
- Tablas markdown nativas se extraen y convierten a DataFrames
- El mapeo busca coincidencias parciales en títulos de secciones

---

## Comandos Útiles

```bash
# Ejecutar local
cd C:\Proyectos\generador-af
streamlit run app.py

# Deploy
# La app se auto-deploya en Streamlit Cloud al hacer push a main
```

### URL de Producción
https://generador-af-cq4act8tvcpcsvszsztiou.streamlit.app/

### Repo GitHub
https://github.com/muruapablo/generador-af

---

## Cambios Recientes (v1.5)

- Agregado editor visual para contenido parseado desde archivos .md
- Fix de sincronización de widgets con datos parseados
- Mejoras en detección de contenido (bloques de código para secciones técnicas)

## Próximos Pasos Sugeridos

1. **Verificar funcionamiento** del editor post-parseo con archivos reales .md
2. **Implementar templates/pre-sets** de documentos
3. **Agregar autosave** para no perder trabajo accidentalmente
4. **Mejorar dashboard** de Información General con más métricas
5. **Agregar tests** básicos de integración
