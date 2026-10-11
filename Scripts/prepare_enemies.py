"""Place modestly denser, varied encounters away from hazards, goals and lift docks."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
campaign_path=ROOT/'Config/campaign.json'; campaign=json.loads(campaign_path.read_text())
base_path=ROOT/'Config/platformer.json'; base=json.loads(base_path.read_text())
targets=[2,3,4,5,5,5,6,7]; report=[]
for cfg,target in zip(campaign['levels'],targets):
    n=cfg['index']; level=base['level'] if n==1 else cfg
    platforms=level['platforms']; chosen=[]
    blockers=[(h['position'][0],350 if n>=5 else 200) for h in level['hazards']]
    blockers += [(p[0],130) for p in level['checkpoints']]
    blockers += [(level['goal'][0],170)]
    order=sorted(range(len(platforms)),key=lambda j:(j!=3,j==4,-platforms[j]['width']))
    def valid(x,j):
        p=platforms[j]
        if j==0 and x<620: return False
        if j==4 and x>p['x']+p['width']-260: return False
        return all(abs(x-b)>=d for b,d in blockers) and all(abs(x-e['position'][0])>=250 for e in chosen)
    for pass_number in range(3):
        for j in order:
            p=platforms[j]
            if p['width']<420: continue
            if pass_number==0 and any(e['platform']==j for e in chosen): continue
            candidates=list(range(p['x']+140,p['x']+p['width']-139,15))
            candidates.sort(key=lambda x:abs(x-(p['x']+p['width']*.55)))
            pos=next((x for x in candidates if valid(x,j)),None)
            if pos is None: continue
            kind='Scout'
            if n>=2 and len(chosen)%3==1 and p['width']>=520: kind='Charger'
            if n>=3 and len(chosen)%3==2 and p['width']>=600 and p['x']+p['width']-pos>230: kind='Sentinel'
            chosen.append(dict(id=f'enemy{n}_{len(chosen)}',kind=kind,platform=j,position=[pos,0,p['top']+27],
                patrol_min_x=pos-55,patrol_max_x=pos+55,speed=(90+min(n,6)*8 if kind=='Scout' else 65+n*4 if kind=='Charger' else 45)))
            if len(chosen)==target: break
        if len(chosen)==target: break
    if len(chosen)!=target: raise RuntimeError(f'Insufficient safe encounters in level {n}: {len(chosen)}/{target}')
    # Ensure the tougher guard is introduced on broad ground, rather than a small jump landing.
    if n>=3 and not any(e['kind']=='Sentinel' for e in chosen):
        for e in chosen[1:]:
            p=platforms[e['platform']]
            if p['width']>=600 and min(e['position'][0]-p['x'],p['x']+p['width']-e['position'][0])>=230:
                e['kind']='Sentinel'; e['speed']=45; break
    level['enemies']=chosen
    report.append(dict(level=n,count=len(chosen),types=sorted(set(e['kind'] for e in chosen))))
base_path.write_text(json.dumps(base,indent=2)); campaign_path.write_text(json.dumps(campaign,indent=2))
(ROOT/'Assets/Models/Enemies/encounter_plan.json').write_text(json.dumps(report,indent=2))
print('ENEMY_ENCOUNTERS_OK',report)
