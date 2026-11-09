@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Markup UI Documentation Preview
cd /d "%~dp0"
if errorlevel 1 goto failed

rem Always use the interpreter inside this project's virtual environment.
set "DOCS_PYTHON=%~dp0.venv-zensical\Scripts\python.exe"
if exist "%DOCS_PYTHON%" goto environment_ready

echo [1/3] Creating the local Python environment...
py -3 --version >nul 2>&1
if errorlevel 1 goto try_python
py -3 -m venv "%~dp0.venv-zensical"
if errorlevel 1 goto failed
goto environment_ready

:try_python
python --version >nul 2>&1
if errorlevel 1 goto python_missing
python -m venv "%~dp0.venv-zensical"
if errorlevel 1 goto failed

:environment_ready
echo [2/3] Installing documentation dependencies...
rem Prefer the project's own dependency list, shared with CI.
if exist "%~dp0requirements-docs.txt" goto install_docs_requirements
if exist "%~dp0requirements.txt" goto install_requirements
echo No requirements file found. Installing Zensical.
"%DOCS_PYTHON%" -m pip install zensical==0.0.74
if errorlevel 1 goto failed
goto configuration_check

:install_docs_requirements
"%DOCS_PYTHON%" -m pip install -r "%~dp0requirements-docs.txt"
if errorlevel 1 goto failed
goto configuration_check

:install_requirements
"%DOCS_PYTHON%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto failed

:configuration_check
set "DOCS_CONFIG=%~dp0zensical.toml"
if exist "%DOCS_CONFIG%" goto preview
echo.
echo ERROR: No zensical.toml found beside this BAT file.
echo Add the site configuration and docs source files, then run this BAT again.
goto failed

:preview
echo [3/3] Building both documentation editions...
"%DOCS_PYTHON%" scripts\build-docs.py
if errorlevel 1 goto failed
echo Leave this window open. Press Ctrl+C to stop the preview.
echo Chinese: http://127.0.0.1:15861/
echo English: http://127.0.0.1:15861/en/
"%DOCS_PYTHON%" -m http.server 15861 --bind 127.0.0.1 --directory site
if errorlevel 1 goto failed
exit /b 0

:python_missing
echo.
echo ERROR: Python 3 was not found. Install Python 3 with pip and PATH enabled.
goto failed

:failed
echo.
echo Preview could not start. Review the error above and run this BAT again.
pause
exit /b 1
