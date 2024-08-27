@echo off
setlocal enabledelayedexpansion

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"

REM Set the path to your main Python file
set "MAIN_PY=%PROJECT_ROOT%main.py"

REM Set the path to your locale directory
set "LOCALE_DIR=%PROJECT_ROOT%locale"

REM Update the .pot file
pybabel extract -k "translate" -o "%LOCALE_DIR%\video_trimmer.pot" "%MAIN_PY%"

REM Update or create .po files for each language
for %%L in (zh_TW en_US) do (
    if exist "%LOCALE_DIR%\%%L\LC_MESSAGES\messages.po" (
        echo Updating %%L translations...
        pybabel update -i "%LOCALE_DIR%\video_trimmer.pot" -d "%LOCALE_DIR%" -l %%L
    ) else (
        echo Creating %%L translations...
        pybabel init -i "%LOCALE_DIR%\video_trimmer.pot" -d "%LOCALE_DIR%" -l %%L
    )
)

echo Translation files (.po/.pot) updated successfully.
pause