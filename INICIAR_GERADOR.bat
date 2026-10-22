@echo off
title Gerador de Relatorios - Estudio Empena
echo ======================================================
echo    GERADOR DE RELATORIOS - ESTUDIO EMPENA
echo ======================================================
echo.
echo Iniciando o sistema no navegador...
echo.

cd /d "%~dp0Sistema"
python -m streamlit run app.py --server.headless false

pause
