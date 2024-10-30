@echo off
:menu
echo ==============================================
echo             Download Tool Menu
echo ==============================================
echo 1. Yt-dlp
echo 2. Gallery-dl
echo ==============================================
set /p choice="Choose an option (1-2): "

if "%choice%"=="1" goto runV1
if "%choice%"=="2" goto runV2
echo Invalid choice, please select a valid option.
goto menu

:runV1
echo Running Yt-dlp
set "SCRIPT_PATH=%~dp0Yt-Ins.py"
python "%SCRIPT_PATH%"
goto menu

:runV2
echo Running Gallery-dl
set "SCRIPT_PATH=%~dp0gldl.py"
python "%SCRIPT_PATH%"
goto menu

:exit
echo Exiting...
exit