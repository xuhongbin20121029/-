@echo off
chcp 65001 >nul
title Project Setup

echo Creating project structure...
mkdir ollama-ai-assistant
cd ollama-ai-assistant

mkdir backend
mkdir frontend
mkdir frontend\templates
mkdir scripts
mkdir logs

echo Project structure created
echo Please place files in the following directories:
echo   - start.bat, setup.bat -^> scripts folder
echo   - main.py, requirements.txt -^> backend folder
echo   - index.html -^> frontend\templates folder

echo Run install_dependencies.bat in the root directory to install dependencies
pause