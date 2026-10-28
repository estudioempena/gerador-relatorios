@echo off
title Gerador de Relatorios - Estudio Empena
echo ======================================================
echo    GERADOR DE RELATORIOS - ESTUDIO EMPENA
echo ======================================================
echo.

cd /d "%~dp0Sistema"

echo Verificando dependencias do sistema...
python -c "import streamlit, docx, PIL, dotenv, win32com" >nul 2>&1
if errorlevel 1 (
    echo Instalando bibliotecas necessarias para esta maquina...
    python -m pip install -r requirements.txt
    echo.
)

echo Iniciando o sistema no navegador...
echo.
python -m streamlit run app.py --server.headless false

pause
