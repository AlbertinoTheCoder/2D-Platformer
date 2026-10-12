"""Publish the verified Windows ZIP using GitHub credentials already held by Git."""
import argparse
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'AlbertinoTheCoder/2D-Platformer'
API = 'https://api.github.com/repos/' + REPO
TAG = 'v0.1.0'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def credentials():
    env = dict(os.environ, GCM_INTERACTIVE='Never', GIT_TERMINAL_PROMPT='0')
    result = subprocess.run(['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n', text=True,
        capture_output=True, check=True, cwd=ROOT, env=env)
    values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    if not values.get('password'):
        raise RuntimeError('No existing GitHub credential is available')
    return values['password']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--make-public', action='store_true', help='Requires explicit repository-visibility authorization')
    args = parser.parse_args()
    if git('remote', 'get-url', 'origin') != 'https://github.com/' + REPO + '.git':
        raise RuntimeError('Unexpected repository destination')
    token = credentials()
    def request(url, method='GET', payload=None, file=None):
        if urllib.parse.urlparse(url).hostname not in ('api.github.com', 'uploads.github.com'):
            raise RuntimeError('Unexpected GitHub API destination')
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2026-03-10', 'User-Agent': 'Scintilla-release'}
        if file is not None:
            headers['Content-Type'] = 'application/zip' if file.name.endswith('.zip') else 'text/plain'
            headers['Content-Length'] = str(Path(file.name).stat().st_size)
            data = file
        else:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(payload).encode() if payload is not None else None
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=headers), timeout=600) as response:
            return json.load(response)
    repo = request(API)
    if not repo.get('permissions', {}).get('push'):
        raise RuntimeError('Current GitHub credential lacks repository write access')
    print('REPOSITORY', repo['full_name'], 'public' if not repo['private'] else 'private', flush=True)
    if not args.publish:
        print('RELEASE_ACCESS_OK', flush=True)
        return
    commit = git('rev-parse', 'HEAD')
    remote_commit = request(API + '/git/ref/heads/main')['object']['sha']
    if commit != remote_commit:
        raise RuntimeError('Push the verified release commit to main before publication')
    smoke = json.loads((ROOT / 'Build/PackagingLogs/packaged_smoke_report.json').read_text())
    if smoke['failures']:
        raise RuntimeError('Packaged gameplay checks failed')
    archive = ROOT / 'Build/Releases/SCINTILLA-Windows.zip'
    checksum = ROOT / 'Build/Releases/SCINTILLA-Windows.sha256.txt'
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if checksum.read_text().split()[0] != digest:
        raise RuntimeError('Release ZIP checksum mismatch')
    if repo['private']:
        if not args.make_public:
            raise RuntimeError('Repository is private; authorize public visibility before publishing for everyone')
        repo = request(API, 'PATCH', {'visibility': 'public'})
        if repo['private']:
            raise RuntimeError('Repository visibility did not change')
        print('REPOSITORY_PUBLIC', repo['html_url'], flush=True)
    body = ('First playable Windows build of **SCINTILLA**. All eight districts are included.\n\n'
        'Download **SCINTILLA-Windows.zip**, extract the entire archive, then run **SCINTILLA.exe**. '
        'Keep its accompanying folders together. Unreal Editor is not required.\n\n'
        'For missing runtime components, use the included `Engine/Extras/Redist/en-us/vc_redist.x64.exe`.\n\n'
        '**Controls:** A/D or arrows to move, Space to jump, J to attack, E to activate, W/S to turn, U to pause.\n\n'
        'Obstacle hints are removed, and the restoration ground extends below the full zoom-out.\n\n'
        f'Validation: {len(smoke["checks"])} packaged gameplay/HUD checks passed; ZIP integrity verified. '
        'Tested locally on Windows; other PCs have not yet been tested.\n\n'
        f'Source commit: `{commit}`. A SHA-256 checksum file is included with the downloads.\n')
    releases = request(API + '/releases?per_page=100')
    release = next((item for item in releases if item['tag_name'] == TAG), None)
    if release is None:
        release = request(API + '/releases', 'POST', {'tag_name': TAG, 'target_commitish': commit,
            'name': 'SCINTILLA v0.1.0 - Windows', 'body': body, 'draft': True, 'prerelease': True})
    elif not release['draft']:
        raise RuntimeError('This version is already published; use a new release version')
    for path in (archive, checksum):
        existing = next((asset for asset in release['assets'] if asset['name'] == path.name), None)
        with path.open('rb') as stream:
            local_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
        if existing:
            if existing.get('digest') != 'sha256:' + local_hash:
                raise RuntimeError('Existing release asset differs: ' + path.name)
            continue
        upload = release['upload_url'].split('{')[0] + '?name=' + urllib.parse.quote(path.name)
        with path.open('rb') as stream:
            asset = request(upload, 'POST', file=stream)
        if asset['size'] != path.stat().st_size or asset.get('digest') != 'sha256:' + local_hash:
            raise RuntimeError('Uploaded release asset failed verification')
        print('ASSET_UPLOADED', path.name, asset['size'], flush=True)
    published = request(API + '/releases/' + str(release['id']), 'PATCH',
        {'draft': False, 'prerelease': True, 'body': body})
    print('RELEASE_PUBLISHED', published['html_url'], flush=True)

if __name__ == '__main__':
    main()
