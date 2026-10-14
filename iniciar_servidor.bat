@echo off
chcp 65001 >nul
title Cursos MEF - Panel de Capacitaciones
color 0F
cd /d "%~dp0"

echo ======================================================================
echo          PORTAL DE CAPACITACIONES MEF - CURSOS DEL DÍA
echo ======================================================================
echo.
echo  Iniciando servidor local y abriendo el panel en tu navegador...
echo  Dirección: http://localhost:8000
echo.
echo  Presiona Ctrl+C en esta ventana para detener el servidor.
echo ======================================================================
echo.

start "" "http://localhost:8000"
python server.py
pause
