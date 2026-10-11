"""Author four districts with increasing gaps, enemy speed and lift precision."""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'Config/platformer.json').read_text())['level']
layouts=[
    [(0,900,0),(1120,420,70),(1760,400,145),(2320,1020,10),(3600,620,70),(4930,520,70),(5670,330,150),(6260,320,50),(6820,900,110)],
    [(0,900,0),(1120,420,60),(1760,420,125),(2400,940,20),(3560,660,80),(4920,600,80),(5740,420,125),(6380,420,55),(7020,900,100)],
    [(0,900,0),(1140,400,70),(1780,400,130),(2420,1050,20),(3710,650,90),(4980,640,90),(5860,400,145),(6500,420,75),(7160,900,125)],
]
names=['Fonderia','Condotte','Torre']
enemy_specs=[[(2500,2450,2750),(5150,5020,5370)],[(2530,2450,2750),(5120,5020,5330),(7180,7080,7380)],[(2760,2710,2900),(4110,4050,4180),(5370,5270,5460),(7410,7320,7480)]]
hazard_specs=[[2960,7030],[2820,3800,7270],[500,3200,3970,7650]]
campaign={'levels':[{'index':1,'name':base['name'],'title':'Workshop 07','source':'platformer.json'}]}
for i,layout in enumerate(layouts):
    n=i+2
    platforms=[dict(id=p['id'],x=x,width=w,top=z) for p,(x,w,z) in zip(base['platforms'],layout)]
    top=lambda x: next(p['top'] for p in platforms if p['x']<=x<=p['x']+p['width'])
    enemies=[dict(id=f'drone_{j}',position=[x,0,top(x)+27],patrol_min_x=a,patrol_max_x=b,speed=115+i*30) for j,(x,a,b) in enumerate(enemy_specs[i])]
    hazards=[dict(id=f'cable_{j}',position=[x,0,top(x)+15],width=100) for j,x in enumerate(hazard_specs[i])]
    checkpoints=[[3900,0,top(3900)+50]]
    if i==1: checkpoints.append([5100,0,top(5100)+50])
    pickups=[[p['x']+p['width']*.55,0,p['top']+80] for p in platforms]
    pickups += [[4390,0,195]]
    for j in range(i*2):
        p=platforms[3 if j%2==0 else 8]
        pickups.append([p['x']+150+(j//2)*200,0,p['top']+120])
    campaign['levels'].append(dict(index=n,name=f'L_0{n}_{names[i]}',title=["Foundry","Pipeworks","Central Tower"][i],spawn=[100,0,100],platforms=platforms,
        moving_platform=dict(id='bridge',start=[4390,0,90+i*10],end=[4790,0,90+i*10],width=200-i*20,speed=150+i*35,wait_seconds=.4-i*.125,loop='ping_pong'),
        enemies=enemies,hazards=hazards,checkpoints=checkpoints,collectibles=pickups,goal=[7440,0,top(7440)+50],kill_zone=base['kill_zone']))
    if n==3:
        campaign['levels'][-1]['moving_platform'].update(width=280,speed=125,wait_seconds=1.0,start=[4390,0,80],end=[4790,0,80])
        for enemy in enemies: enemy['speed']=135
    if n==4:
        cfg=campaign['levels'][-1]
        cfg['moving_platform'].update(width=300,speed=145,wait_seconds=1.0,start=[4390,0,90],end=[4790,0,90])
        cfg['checkpoints']=[[4250,0,140],[5090,0,140],[7260,0,175]]
        cfg['goal']=[7840,0,175]
        for enemy in enemies: enemy['speed']=150
        for hazard in hazards: hazard['width']=80

# Analytical check of every fixed-platform gap; a 55 cm runway keeps a margin.
checks=[]
for level in campaign['levels'][1:]:
    for j,(a,b) in enumerate(zip(level['platforms'],level['platforms'][1:])):
        if j==4: continue  # This crossing is served by the moving lift.
        gap=b['x']-a['x']-a['width']; rise=b['top']-a['top']
        peak=780**2/(2*1800)
        time=780/1800+math.sqrt(max(0,2*(peak-rise)/2700))
        margin=600*time-(gap+55)
        checks.append(dict(level=level['name'],from_platform=a['id'],gap=gap,rise=rise,margin_cm=round(margin,1),passed=rise<peak and margin>25))
        if not checks[-1]['passed']: raise ValueError(checks[-1])
(ROOT/'Config/campaign.json').write_text(json.dumps(campaign,indent=2),encoding='utf-8')
(ROOT/'Assets/Models/campaign_jump_validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(f'Campaign: {len(campaign["levels"])} levels, {len(checks)} fixed jumps validated')
import runpy
runpy.run_path(str(ROOT/'Scripts/prepare_expansion.py'))
