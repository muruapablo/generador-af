# Generador de Análisis Funcional

> Genera documentos de análisis funcional en formato Word (DOCX) y HTML para Microsoft Loop de forma automática.

---

## Qué hace esta herramienta

Si escribís análisis funcionales para el sistema **COMEX** (comercio exterior), esta app te permite:

1. **Escribir el contenido** en un formulario web simple.
2. **Generar automáticamente** tres documentos:
   - **DOCX**: Formato profesional con header "COMEX | DOCUMENTO FUNCIONAL", footer con DMND/fecha/página, estilos corporativos, tablas, código SQL con fondo negro.
   - **HTML (Loop)**: Versión con secciones colapsables (acordeones), ideal para copiar y pegar en **Microsoft Loop**.
   - **HTML (Completo)**: Versión plana sin acordeones, ideal para leer el documento entero de una vez.

**Resultado:** Ahorrás horas de formateo manual en Word. Te enfocás solo en el contenido.

---

## Cómo empezar

### 1. Instalar dependencias (una sola vez)

Abrí una terminal en la carpeta del proyecto y ejecutá:

```bash
cd C:\Proyectos\generador-af
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## Cómo usar la app

### Paso 1: Completar metadatos (barra lateral)

En la barra lateral izquierda ingresá:
- **Número de demanda** (ej: `5158443`)
- **Título** del análisis
- **Fecha, Ciclo, Sistema, Versión, Autor**
- (Opcional) **Nombre de archivo personalizado** (si no querés que sea `DMND5158443`)
- (Opcional) **Subí tu logo corporativo** (.png). Aparecerá centrado en ambos documentos.

### Paso 2: Completar las secciones (pestañas)

La app tiene **10 pestañas** predefinidas:

| Pestaña | Qué escribir acá |
|---|---|
| Portada | Solo verificá que los metadatos estén bien |
| Índice | Se genera solo, no escribas nada |
| Información General | Contexto y alcance del análisis |
| Historial de Versiones | Tabla editable: versión, comentario, fecha, autor |
| Necesidad | Descripción de la necesidad de negocio |
| Objetivos y Condiciones | Qué debe lograr el desarrollo |
| Descripción de Actividades | Flujo de operación actual y propuesto |
| Reglas para el Desarrollo | Endpoints, SQL, estructuras de datos (tabla incluida) |
| Criterios de Aceptación | Condiciones para dar por terminado el desarrollo |
| Aprobaciones | Espacio para registro de firmas/aprobaciones |

**Herramientas rápidas:** En cada pestaña tenés botones para:
- **📄 Insertar SQL**: Agrega un bloque de código SQL listo para completar.
- **💻 Insertar código**: Agrega un bloque de código genérico.
- **📊 Insertar tabla**: Agrega una tabla markdown editable.
- **🗑️ Limpiar**: Borra el contenido de la sección.

**Formato del texto:** También podés escribir Markdown manualmente:
- `# Título` para subtítulos, `**negrita**` para resaltar
- Bloques de código con triple backtick (se verán con fondo negro):
  ````sql
  SELECT * FROM tabla
  ````

### Paso 3: Opciones de salida (sidebar)

En la barra lateral podés elegir:
- **HTML con acordeones**: Secciones colapsables para Loop (por defecto).
- **HTML completo**: Versión plana sin acordeones (se genera adicionalmente).

### Paso 4: Generar documentos

Hacé clic en el botón **"Generar Documentos"**.

Se descargarán:
1. **`.docx`**: Con header "COMEX | DOCUMENTO FUNCIONAL" y footer con DMND/fecha/página.
2. **`.html`**: Versión con acordeones para Loop.
3. **`_completo.html`**: Versión plana sin acordeones (si elegiste acordeones).
4. **`.zip`**: Paquete con todos los archivos.

También verás una **vista previa** en la misma app.

---

## Tips para usar en Microsoft Loop

1. Abrí el archivo `.html` en tu navegador.
2. Cada sección tiene un botón **"Copiar sección"**. Usalo para pegar partes del documento en Loop fácilmente.
3. Las secciones están **colapsadas por defecto**. Hacé clic para expandirlas.
4. Los bloques de código conservan el formato con fondo oscuro al pegarlos.

---

## Deploy en Streamlit Cloud (Recomendado)

### Opción 1: Deploy automático con GitHub (más fácil)

1. **Crear repositorio en GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/generador-af.git
   git push -u origin main
   ```

2. **Conectar a Streamlit Cloud:**
   - Andá a [share.streamlit.io](https://share.streamlit.io)
   - Iniciá sesión con tu cuenta de GitHub
   - Hacé clic en **"New app"**
   - Seleccioná tu repositorio `generador-af`
   - El archivo principal es `app.py` (ya está configurado)
   - Hacé clic en **Deploy**

3. **Configuración automática:**
   - Streamlit Cloud detecta automáticamente `requirements.txt`
   - El tema corporativo se carga desde `.streamlit/config.toml`
   - Los documentos generados se guardan temporalmente en `generated/` (se borran al reiniciar la app)

### Opción 2: Deploy local (sin GitHub)

Si no querés usar GitHub, podés seguir usando la app localmente:

```bash
cd C:\Proyectos\generador-af
streamlit run app.py
```

---

## Estructura de archivos

```
generador-af/
├── app.py                 # App principal (no tocar)
├── engine/                # Motores de generación (no tocar)
├── forms/                 # Configuración de secciones
├── assets/                # Estilos visuales
├── generated/             # Acá se guardan tus documentos
└── requirements.txt       # Dependencias
```

**Tus documentos generados se guardan en:** `generated/{nombre}/` (dentro de la carpeta del proyecto)

---

## ¿Necesitás ayuda?

Si algo no funciona, verificá que:
1. Estés dentro de `C:\Proyectos\generador-af` al ejecutar los comandos.
2. Tengas Python 3.10 o superior instalado.
3. Hayas ejecutado `pip install -r requirements.txt` sin errores.

Para desarrollo o escalabilidad, leé `AGENTS.md`.
