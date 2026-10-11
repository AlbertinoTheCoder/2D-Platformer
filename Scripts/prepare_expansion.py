"""Append four varied, generously spaced districts without altering levels 1-4."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'Config/campaign.json'
campaign=json.loads(path.read_text())
campaign['levels']=campaign['levels'][:4]
specs=[
 ('Cryo','CRYO LABS',[900,440,600,460,800,720,460,620,460,950],[0,55,105,40,90,90,150,95,155,100],220,145),
 ('Scrap','SCRAP YARDS',[1000,600,440,620,760,680,460,540,440,620,900],[0,65,125,60,110,110,170,100,40,105,140],230,150),
 ('Solar','SOLAR WORKS',[1000,460,520,440,780,720,460,500,440,540,440,950],[0,75,145,80,135,135,70,140,75,145,90,150],240,155),
 ('Bio','BIO GARDENS',[1050,500,460,580,850,760,460,540,460,620,440,500,1000],[0,65,130,70,140,140,80,145,90,155,95,160,115],250,160),
]
checks=[]
for n,(name,title,widths,tops,gap,speed) in enumerate(specs,5):
    platforms=[]; x=0
    for j,(w,z) in enumerate(zip(widths,tops)):
        if j==5: x+=620-gap  # Broad service-lift crossing.
        platforms.append(dict(id=f'exp{n}_{j}',x=x,width=w,top=z))
        x+=w+gap
    a,b=platforms[4:6]
    lift_start=a['x']+a['width']+150; lift_end=b['x']-150
    checkpoints=[[p['x']+80,0,p['top']+50] for p in (platforms[4],platforms[6],platforms[-2])]
    enemies=[]; hazards=[]
    combat_indices={5:(2,5,7,9),6:(1,3,5,9),7:(2,5,9,11),8:(3,5,7,9,12)}[n]
    for j,p in enumerate(platforms):
        if j in combat_indices:
            enemies.append(dict(id=f'exp{n}_drone{j}',position=[p['x']+p['width']*.55,0,p['top']+27],
                patrol_min_x=p['x']+p['width']*.40,patrol_max_x=p['x']+p['width']*.65,speed=145+(n-5)*10))
        if j in (0,4,len(platforms)-1):
            hazards.append(dict(id=f'exp{n}_cable{j}',position=[p['x']+p['width']*.60,0,p['top']+15],width=65))
    pickups=[[p['x']+p['width']*.3,0,p['top']+80] for p in platforms]
    pickups += [[lift_start,0,a['top']+90],[lift_end,0,a['top']+90]]
    last=platforms[-1]; goal=[last['x']+last['width']-100,0,last['top']+50]
    cfg=dict(index=n,name=f'L_{n:02}_{name}',title=title,spawn=[100,0,100],platforms=platforms,
        moving_platform=dict(id='bridge',start=[lift_start,0,a['top']],end=[lift_end,0,a['top']],width=320,speed=speed,wait_seconds=1.1,loop='ping_pong'),
        enemies=enemies,hazards=hazards,checkpoints=checkpoints,collectibles=pickups,goal=goal,
        kill_zone=dict(center=[x/2,0,-450],extent=[x/2+600,400,100]))
    for j,(a,b) in enumerate(zip(platforms,platforms[1:])):
        if j==4: continue
        rise=b['top']-a['top']; d=b['x']-a['x']-a['width']; peak=780**2/3600
        airtime=780/1800+math.sqrt(2*(peak-rise)/2700); margin=600*airtime-d-55
        check=dict(level=cfg['name'],gap=d,rise=rise,margin_cm=round(margin,1),passed=margin>80 and rise<peak)
        if not check['passed']: raise ValueError(check)
        checks.append(check)
    campaign['levels'].append(cfg)
path.write_text(json.dumps(campaign,indent=2))
(ROOT/'Assets/Models/expansion_jump_validation.json').write_text(json.dumps(checks,indent=2))
print('EXPANSION_CONFIG_OK',len(checks),'jumps; 8 districts')
import runpy
runpy.run_path(str(ROOT/'Scripts/prepare_enemies.py'))
