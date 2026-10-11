"""Distribute existing obstacles across safe, seeded positions in every district."""
import json, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'Config/campaign.json'
campaign = json.loads(path.read_text())
base = json.loads((ROOT / 'Config/platformer.json').read_text())['level']
report = []
for cfg in campaign['levels']:
    original = base if cfg['index'] == 1 else cfg
    ext = cfg['difficulty_extension']
    platforms = sorted(original['platforms'] + ext['platforms'], key=lambda p:p['x'])
    rng = random.Random(7100 + cfg['index'])
    occupied = [e['position'][0] for e in original['enemies']]
    occupied += [h['position'][0] for h in original['hazards']]
    occupied += [c[0] for c in original.get('checkpoints', [])]
    candidates = []
    for p in platforms[1:-1]:
        if p['width'] < 400: continue
        for fraction in (.40, .50, .60):
            x = p['x'] + p['width'] * fraction
            if min([abs(x-v) for v in occupied], default=9999) >= 190:
                candidates.append((p,x))
    # Pick across the route, preserving safe spawn/landing/checkpoint areas.
    rng.shuffle(candidates)
    used = set()
    kinds = ['FallingSpikes', 'Ice', 'RisingSpikes', 'Hammer', 'Axe']
    rng.shuffle(kinds)
    stations = {}
    old_end = ext['platforms'][0]['x']
    for i,kind in enumerate(kinds):
        early = i < 3
        choices = [(p,x) for p,x in candidates if p['id'] not in used and (p['x'] < old_end) == early]
        if not choices: raise RuntimeError(f"No safe {kind} station in level {cfg['index']}")
        # Spread early placements instead of grouping them next to each other.
        target = old_end*(.20 + .24*i) if early else ext['goal'][0]*(.73+.14*(i-3))
        p,x = min(choices, key=lambda item:abs(item[1]-target)+rng.uniform(0,180))
        if kind=='Ice' and p['width']<600:
            wide=[deck for deck in ext['platforms'][:-1] if deck['id'] not in used]
            p=min(wide,key=lambda deck:abs(deck['x']-ext['goal'][0]*.6))
            x=p['x']+p['width']/2
        used.add(p['id']); stations[kind]=p
        h = next(h for h in ext['obstacles'] if h['kind']==kind)
        h['position']=[p['x']+p['width']/2 if kind=='Ice' else round(x,1),0,p['top']]
        h['phase_offset']=round(rng.uniform(0,2.4),3)
        h['half_width']=p['width']/2 if kind=='Ice' else min(140,p['width']/2-70)
    gaps=[]
    for a,b in zip(platforms,platforms[1:]):
        gap=b['x']-a['x']-a['width']
        if 70 <= gap <= 250 and a['id']!='start' and a['width']>=400 and b['width']>=400:
            gaps.append((a,b,gap))
    rng.shuffle(gaps)
    winds=[h for h in ext['obstacles'] if h['kind']=='Wind']
    for i,h in enumerate(winds):
        desired=.25 if i==0 else .65
        a,b,gap=min(gaps,key=lambda g:abs(g[1]['x']-ext['goal'][0]*desired))
        gaps.remove((a,b,gap))
        h['position']=[a['x']+a['width']+gap/2,0,min(a['top'],b['top'])+(150 if i else 100)]
        h['half_width']=gap/2+60; h['phase_offset']=round(rng.uniform(0,6),3)
    # Aerial encounters also move out of the old all-at-the-end queue.
    available=[p for p in platforms[2:-1] if p['id'] not in used and p['width']>=600 and not any(p['x']-120 <= x <= p['x']+p['width']+120 for x in occupied)]
    rng.shuffle(available)
    for i,e in enumerate(ext['flyers']):
        p=available[i]; x=p['x']+p['width']/2
        e['position']=[x,0,p['top']+150]
        e['patrol_min_x']=p['x']+100; e['patrol_max_x']=p['x']+p['width']-100
    ext['scatter_seed']=7100+cfg['index']
    report.append({'level':cfg['index'],'seed':ext['scatter_seed'],'original_route_obstacles':sum(h['position'][0]<old_end for h in ext['obstacles']),'positions':ext['obstacles']})
path.write_text(json.dumps(campaign,indent=2)+'\n')
(ROOT/'Assets/Models/Difficulty/scatter_plan.json').write_text(json.dumps(report,indent=2)+'\n')
print('SCATTER_PLANNED',[(r['level'],r['original_route_obstacles']) for r in report])
