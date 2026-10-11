$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskProject = Join-Path $taskRoot 'Platformer_2D_Game\Platformer_2D_Game.uproject'
$editorPath = 'E:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$connection = Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object -First 1
$editorProcess = Get-Process -Id $connection.OwningProcess
if ($editorProcess.ProcessName -ne 'UnrealEditor') { throw 'Port 8000 is not owned by UnrealEditor' }
$editorProcess.Refresh()
if (-not $editorProcess.CloseMainWindow()) { throw 'Could not request a graceful editor shutdown' }
if (-not $editorProcess.WaitForExit(60000)) { throw 'Editor is still closing; build was not started' }
try {
    & 'E:\UE_5.8\Engine\Build\BatchFiles\Build.bat' Platformer_2D_GameEditor Win64 Development "-Project=$taskProject" -WaitMutex -NoHotReloadFromIDE
    if ($LASTEXITCODE -ne 0) { throw "Unreal build failed ($LASTEXITCODE)" }
} finally {
    Start-Process -FilePath $editorPath -ArgumentList @('"'+$taskProject+'"','-ModelContextProtocolStartServer','-nosplash') -WindowStyle Normal
    Write-Output 'UNREAL_REOPENED'
}
