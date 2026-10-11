"""Dispatch a discovered Unreal MCP tool through the local HTTP connection."""
import contextlib
import io
import json
import sys

with contextlib.redirect_stdout(io.StringIO()):
    from check_unreal_connection import rpc

if __name__ == '__main__':
    from pathlib import Path
    args = json.loads(Path(sys.argv[2]).read_text()) if sys.argv[2].endswith('.json') else json.loads(sys.argv[2])
    result = rpc('tools/call', {'name': sys.argv[1], 'arguments': args}, 10)
    for block in result.get('content', []):
        if block.get('type') == 'text': print(block['text'])
    if result.get('isError'):
        raise SystemExit(1)
