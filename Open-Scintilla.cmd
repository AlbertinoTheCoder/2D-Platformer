@echo off
set "SCINTILLA_EDITOR=E:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
if not exist "%SCINTILLA_EDITOR%" (
    echo Unreal Editor was not found at %SCINTILLA_EDITOR%
    pause
    exit /b 1
)
start "" "%SCINTILLA_EDITOR%" "%~dp0Platformer_2D_Game\Platformer_2D_Game.uproject" -ModelContextProtocolStartServer -nosplash
