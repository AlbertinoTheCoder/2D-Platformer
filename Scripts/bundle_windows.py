"""Bundle the staged Windows game, its prerequisites, and player instructions."""
import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'Build/Packages/Windows'
RELEASES = ROOT / 'Build/Releases'
launcher = PACKAGE / 'Platformer_2D_Game.exe'
if launcher.exists():
    launcher.replace(PACKAGE / 'SCINTILLA.exe')
if not (PACKAGE / 'SCINTILLA.exe').exists():
    raise RuntimeError('Packaged Windows launcher is missing')
if not list(PACKAGE.glob('Platformer_2D_Game/Content/Paks/*.utoc')):
    raise RuntimeError('Packaged game content is missing')
if not (PACKAGE / 'Engine/Extras/Redist/en-us/vc_redist.x64.exe').exists():
    raise RuntimeError('Windows x64 runtime installer is missing')
shutil.copy2(ROOT / 'Docs/windows-release.txt', PACKAGE / 'README.txt')
RELEASES.mkdir(parents=True, exist_ok=True)
archive = RELEASES / 'SCINTILLA-Windows.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as output:
    for path in sorted(PACKAGE.rglob('*')):
        if path.is_file() and 'Saved' not in path.relative_to(PACKAGE).parts:
            output.write(path, 'SCINTILLA/' + path.relative_to(PACKAGE).as_posix())
with archive.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
(RELEASES / 'SCINTILLA-Windows.sha256.txt').write_text(digest + '  ' + archive.name + '\n')
with zipfile.ZipFile(archive) as output:
    if output.testzip() is not None:
        raise RuntimeError('ZIP integrity check failed')
print('RELEASE_ZIP', archive)
print('SIZE_MB', round(archive.stat().st_size / (1024 * 1024), 1))
print('SHA256', digest)
