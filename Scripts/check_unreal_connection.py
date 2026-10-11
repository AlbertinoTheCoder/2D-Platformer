"""Read-only MCP handshake and tool discovery for the local Unreal editor."""
import json,urllib.request
URL='http://127.0.0.1:8000/mcp'
headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
def rpc(method,params=None,number=1):
    payload={'jsonrpc':'2.0','method':method,'params':params or {}}
    if number is not None: payload['id']=number
    request=urllib.request.Request(URL,json.dumps(payload).encode(),headers=headers)
    with urllib.request.urlopen(request,timeout=180) as response:
        session=response.headers.get('Mcp-Session-Id')
        if session: headers['Mcp-Session-Id']=session
        raw=response.read().decode()
    if not raw.strip(): return {}
    if raw.lstrip().startswith('data:') or 'event:' in raw:
        raw=next(line[5:].strip() for line in raw.splitlines() if line.startswith('data:') and '"id"' in line)
    parsed=json.loads(raw)
    if 'error' in parsed: raise RuntimeError(parsed['error'])
    return parsed.get('result',{})
init=rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'Scintilla-connection-check','version':'1.0'}})
rpc('notifications/initialized',number=None)
catalog=rpc('tools/list',number=2)
names=[t['name'] for t in catalog.get('tools',[])]
print(json.dumps({'endpoint':URL,'server':init.get('serverInfo'),'tools':names}))
if 'list_toolsets' in names:
    result=rpc('tools/call',{'name':'list_toolsets','arguments':{}},3)
    if result.get('isError'): raise RuntimeError(result)
    entries='\n'.join(c.get('text','') for c in result.get('content',[]))
    print('UNREAL_LIVE_TOOLSETS_OK', 'EditorAppToolset' in entries)
