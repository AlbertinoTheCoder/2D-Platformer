"""Live MCP inspection / preview for the Scintilla interface."""
import base64
import json
import sys
from pathlib import Path
from unreal_rpc import rpc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Assets/UI'
OUT.mkdir(parents=True, exist_ok=True)
DIAGNOSTICS = ROOT / 'Platformer_2D_Game/Saved/ScintillaUIDiagnostics'
DIAGNOSTICS.mkdir(parents=True, exist_ok=True)

def call(toolset, tool, args=None):
    result = rpc('tools/call', {'name':'call_tool', 'arguments':{
        'toolset_name':toolset, 'tool_name':tool, 'arguments':args or {}}}, 20)
    if result.get('isError'): raise RuntimeError(result)
    texts = [b['text'] for b in result.get('content',[]) if b['type']=='text']
    value = json.loads(texts[0]) if texts else {}
    if isinstance(value, dict) and value.get('success') is False: raise RuntimeError(value)
    return value

def describe(name):
    result = rpc('tools/call', {'name':'describe_toolset','arguments':{'toolset_name':name}},21)
    value = json.loads(result['content'][0]['text'])
    (DIAGNOSTICS / (name.split('.')[-1] + '.json')).write_text(json.dumps(value,indent=2),encoding='utf-8')
    return value

if sys.argv[1]=='list':
    result=rpc('tools/call',{'name':'list_toolsets','arguments':{}},22)
    for line in result['content'][0]['text'].splitlines():
        if any(s in line.lower() for s in ['slate','livecoding','assettools','python']): print(line)
elif sys.argv[1]=='describe':
    value=describe(sys.argv[2])
    for t in value['tools']:
        if len(sys.argv)<4 or sys.argv[3].lower() in t['name'].lower(): print(json.dumps(t))
elif sys.argv[1]=='skills':
    print(json.dumps(call('ToolsetRegistry.AgentSkillToolset','ListSkills')))
elif sys.argv[1]=='save':
    running=call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']
    if running: call('EditorToolset.EditorAppToolset','StopPIE')
    result=call('editor_toolset.toolsets.asset.AssetTools','save_assets',{'asset_paths':[]})
    if not result['returnValue']: raise RuntimeError('Editor save failed')
    print('EDITOR_SAVED')
elif sys.argv[1]=='console':
    import re
    import time
    slate='SlateInspectorToolset.SlateInspectorToolset'
    windows=call(slate,'Windows',{'action':'list'})
    print(windows)
    call(slate,'Windows',{'action':'select','index':0})
    observer=call(slate,'Observe',{'ref':'w1','maxDepth':40})['returnValue']
    try:
        time.sleep(.3)
        snapshot=call(slate,'Snapshot',{'ref':'w1','maxDepth':40})['returnValue']
        candidates=[line for line in snapshot.splitlines() if 'textbox' in line.lower()]
        (DIAGNOSTICS/'console_snapshot.txt').write_text(snapshot,encoding='utf-8')
        print('\n'.join(candidates))
        if len(sys.argv)>2:
            lines=snapshot.splitlines()
            cmd_index=max(i for i,line in enumerate(lines) if 'text "Cmd"' in line and '[pos=0,0' not in line)
            line=next(line for line in lines[cmd_index+1:] if 'textbox' in line.lower())
            ref=re.search(r'\b(tb\d+)\b',line).group(1)
            command=sys.argv[2] if sys.argv[2].startswith('py ') else "py exec(open("+repr(str(ROOT/sys.argv[2]).replace('\\','/'))+", encoding='utf-8').read())"
            response=call(slate,'Type',{'ref':ref,'text':command,'submit':True})
            if not response['returnValue']: raise RuntimeError('Console input failed')
            print('CONSOLE_SUBMITTED')
    finally:
        call(slate,'Unobserve',{'identifier':observer})
elif sys.argv[1]=='capture':
    value=call('EditorToolset.EditorAppToolset','CaptureEditorImage')['returnValue']
    path=OUT / (sys.argv[2]+'.png')
    path.write_bytes(base64.b64decode(value['data']))
    print(path)
elif sys.argv[1]=='start':
    print(json.dumps(call('EditorToolset.EditorAppToolset','StartPIE',{'options':{
        'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})))
elif sys.argv[1]=='app':
    print(json.dumps(call('EditorToolset.EditorAppToolset',sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv)>3 else {})))
