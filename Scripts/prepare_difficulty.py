"""Plan longer routes with safe waiting space and separated obstacle stations."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'Config/campaign.json'; campaign=json.loads(path.read_text())
base=json.loads((ROOT/'Config/platformer.json').read_text())['level']
report=[]
for cfg in campaign['levels']:
    if cfg.get('difficulty_extension'): continue
    original=base if cfg['index']==1 else cfg
    platforms=original['platforms']; last=max(platforms,key=lambda p:p['x']+p['width'])
    end=last['x']+last['width']; top=last['top']; extension=[]; hazards=[]; flights=[]; energy=[]
    gap=90+min(cfg['index']-1,5)*10
    x=end+gap
    # Six wide decks plus a seventh aerial station; all hazards have waiting pads.
    kinds=['Wind','FallingSpikes','Ice','Flyer','RisingSpikes','Hammer','Axe']
    for i,kind in enumerate(kinds):
        z=top+[0,40,0,-30,20,50,0][i]
        p=dict(id='challenge_'+str(i),x=x,width=680,top=z); extension.append(p)
        energy.append([x+560,0,z+90])
        if kind=='Flyer':
            for j in range(1 if cfg['index']<4 else 2):
                flights.append(dict(position=[x+270+j*180,0,z+115],patrol_min_x=x+180,patrol_max_x=x+510,speed=65+cfg['index']*7,kind='Flyer' if j==0 else 'SurveyFlyer'))
        else:
            hazards.append(dict(kind=kind,position=[x+340,0,z],phase_offset=(i*.73)%6,half_width=150))
            if kind=='Wind':
                hazards[-1]['position']=[x-45,0,z+100]; hazards[-1]['direction']=[-1,0,0]
                hazards.append(dict(kind='Wind',position=[x+680+gap/2,0,z+180],phase_offset=2.4,direction=[0,0,-1],half_width=gap/2+45))
        x+=680+gap
    newgoal=[extension[-1]['x']+570,0,extension[-1]['top']+50]
    cfg['difficulty_extension']={'original_goal':original['goal'],'platforms':extension,'obstacles':hazards,'flyers':flights,'collectibles':energy,'checkpoint':[extension[3]['x']+70,0,extension[3]['top']+50],'goal':newgoal,'attempt_limits':[8,5,3]}
    cfg['goal']=newgoal
    # Fixed jumps have short gaps and at least 500 cm to brake before each edge.
    chain=[last]+extension
    for a,b in zip(chain,chain[1:]):
        height=b['top']-a['top']; discriminant=780**2-2*1800*height
        flight=(780+math.sqrt(discriminant))/1800
        margin=600*flight-(b['x']-a['x']-a['width'])
        report.append({'level':cfg['index'],'gap_cm':b['x']-a['x']-a['width'],'height_cm':height,'jump_margin_cm':round(margin,1)})
path.write_text(json.dumps(campaign,indent=2)+'\n')
(ROOT/'Assets/Models/Difficulty/route_plan.json').write_text(json.dumps(report,indent=2))
print('DIFFICULTY_EXTENSION_PLANNED',len(report),'jumps; minimum margin',min([r['jump_margin_cm'] for r in report],default=0))
