"""Run the gameplay/HUD probe in the packaged executable using isolated save data."""
import json
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / 'Build/Packages/Windows'
executable = package / 'Platformer_2D_Game/Binaries/Win64/Platformer_2D_Game-Win64-Shipping.exe'
test_dir = ROOT / 'Build/PackagingLogs/PackagedSmoke' / uuid.uuid4().hex
test_dir.mkdir(parents=True)
subprocess.run([str(executable), '-ScintillaSmoke',
    '-ScintillaProgressSlot=Scintilla_Packaged_Automation',
    '-UserDir=' + str(test_dir), '-nullrhi', '-nosound', '-unattended', '-nosplash'],
    cwd=package, check=True, timeout=120)
reports = list(test_dir.rglob('ScintillaPlaytest.json'))
if len(reports) != 1:
    raise RuntimeError('Packaged executable did not produce the gameplay test report')
result = json.loads(reports[0].read_text(encoding='utf-8-sig'))
output = ROOT / 'Build/PackagingLogs/packaged_smoke_report.json'
output.write_text(json.dumps(result, indent=2) + '\n')
print('PACKAGED_SMOKE', len(result['checks']), 'checks', result['failures'], 'failures')
if result['failures']:
    raise SystemExit(1)
