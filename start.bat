@echo off
title CampusOS - Full Stack Server
color 0A
echo.
echo  ==========================================
echo   CampusOS  -  University Digital Twin
echo   Flask + PostgreSQL 18 Full Stack
echo  ==========================================
echo.
if not defined CAMPUSOS_DB_USER set CAMPUSOS_DB_USER=postgres
if not defined CAMPUSOS_DB_NAME set CAMPUSOS_DB_NAME=university_digital_twin
if not defined CAMPUSOS_DB_HOST set CAMPUSOS_DB_HOST=localhost
if not defined CAMPUSOS_DB_PORT set CAMPUSOS_DB_PORT=5432
if not defined CAMPUSOS_DB_PASSWORD set CAMPUSOS_DB_PASSWORD=Sasank
echo.
echo  Installing dependencies...
py -m pip install flask psycopg2-binary werkzeug --quiet
echo.
echo  Starting server at http://127.0.0.1:5000
echo  Open your browser to: http://127.0.0.1:5000
echo.
set PYTHONUTF8=1
py server.py
pause
