"""Talk to the installed Blender addon's local socket without changing client setup."""
import argparse
import json
from pathlib import Path
import socket

def call(kind, params=None):
    with socket.create_connection(('127.0.0.1', 9876), timeout=10) as sock:
        sock.settimeout(180)
        sock.sendall(json.dumps({'type': kind, 'params': params or {}}).encode())
        data = b''
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                raise RuntimeError('Blender disconnected before returning a result')
            data += chunk
            try:
                result = json.loads(data)
                break
            except json.JSONDecodeError:
                continue
    if result.get('status') == 'error':
        raise RuntimeError(result)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--script', type=Path)
    args = parser.parse_args()
    print(json.dumps(call('execute_code', {'code': args.script.read_text(encoding='utf-8')})
                     if args.script else call('get_scene_info'), ensure_ascii=False))
