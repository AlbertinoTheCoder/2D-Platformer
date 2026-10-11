"""Apply English display text without renaming asset paths or save identifiers."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
translations=json.loads((ROOT/'Config/english-text.json').read_text(encoding='utf-8'))
for path in [ROOT/'Platformer_2D_Game/Source/Scintilla/ScintillaUI.cpp', ROOT/'Platformer_2D_Game/Source/Scintilla/ScintillaCampaign.h', ROOT/'Scripts/build_unreal_assets.py']:
    source=path.read_text(encoding='utf-8')
    for old,new in translations.items():
        source=source.replace(json.dumps(old,ensure_ascii=False),json.dumps(new,ensure_ascii=False))
    path.write_text(source,encoding='utf-8')
path=ROOT/'Config/campaign.json'
campaign=json.loads(path.read_text(encoding='utf-8'))
for cfg,title in zip(campaign['levels'],['Workshop 07','Foundry','Pipeworks','Central Tower','Cryo Labs','Scrap Yards','Solar Works','Bio Gardens']): cfg['title']=title
path.write_text(json.dumps(campaign,indent=2)+'\n',encoding='utf-8')
path=ROOT/'Scripts/prepare_campaign.py'
source=path.read_text(encoding='utf-8').replace("'title':'Officina 07'","'title':'Workshop 07'").replace('title=names[i]','title=["Foundry","Pipeworks","Central Tower"][i]')
path.write_text(source,encoding='utf-8')
print('ENGLISH_DISPLAY_TEXT_APPLIED')
