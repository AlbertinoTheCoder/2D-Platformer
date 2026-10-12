"""Capture the restoration reveal with the deeper ground, preserving user progress."""
from pathlib import Path
source = Path(__file__).with_name('capture_restoration.py').read_text(encoding='utf-8')
source = source.replace("for phase in ('before','repair','reveal','chooser'):", "for phase in ('reveal',):")
source = source.replace("('city_'+phase+'.png')", "('city_'+phase+'_deep_ground.png')")
exec(compile(source, str(Path(__file__).with_name('capture_restoration.py')), 'exec'))
