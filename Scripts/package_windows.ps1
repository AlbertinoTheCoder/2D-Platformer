param(
    [string]$EngineRoot = 'E:\UE_5.8',
    [ValidateSet('Development', 'Shipping')][string]$Configuration = 'Shipping'
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskProject = Join-Path $taskRoot 'Platformer_2D_Game\Platformer_2D_Game.uproject'
$archiveRoot = Join-Path $taskRoot 'Build\Packages'
$logRoot = Join-Path $taskRoot 'Build\PackagingLogs'
$uatPath = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
if (-not (Test-Path -LiteralPath $uatPath)) { throw "Unreal Automation Tool not found: $uatPath" }
New-Item -ItemType Directory -Path $archiveRoot, $logRoot -Force | Out-Null
$logPath = Join-Path $logRoot ("Windows-$Configuration.log")
& $uatPath BuildCookRun "-project=$taskProject" -noP4 -unattended -utf8output -nocompileeditor `
    -platform=Win64 "-clientconfig=$Configuration" -build -cook -stage -pak -iostore -compressed `
    -prereqs -archive "-archivedirectory=$archiveRoot" -nodebuginfo -ddc=InstalledNoZenLocalFallback *> $logPath
if ($LASTEXITCODE -ne 0) {
    Get-Content -LiteralPath $logPath -Tail 70
    throw "Windows packaging failed. Full log: $logPath"
}
Write-Output "WINDOWS_PACKAGE_READY $archiveRoot"
Write-Output "PACKAGING_LOG $logPath"
& python (Join-Path $PSScriptRoot 'bundle_windows.py')
if ($LASTEXITCODE -ne 0) { throw 'Windows release ZIP creation failed' }
