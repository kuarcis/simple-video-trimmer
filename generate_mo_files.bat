@echo off
setlocal enabledelayedexpansion

REM Set the project root directory (adjust if needed)
set "PROJECT_ROOT=%~dp0"

REM Set the path to your locale directory
set "LOCALE_DIR=%PROJECT_ROOT%locale"

REM Compile all .po files to .mo files
pybabel compile -d "%LOCALE_DIR%"

echo .mo files generated successfully.
pause