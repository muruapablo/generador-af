@echo off
chcp 65001 >nul
title Generador de Análisis Funcional
color 0A

echo ============================================
echo   GENERADOR DE ANALISIS FUNCIONAL
echo ============================================
echo.
echo Iniciando aplicacion...
echo.
echo Se abrira automaticamente en tu navegador.
echo Si no se abre, ve a: http://localhost:8501
echo.
echo Para detener, cierra esta ventana o presiona Ctrl+C
echo.
echo ============================================
echo.

cd /d "C:\Proyectos\generador-af"
streamlit run app.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar la aplicacion.
    echo Asegurate de tener instaladas las dependencias:
    echo   pip install -r requirements.txt
    echo.
    pause
)
