"""Independent source-to-runtime pixel oracle; run with Pillow available."""
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('server',ROOT/'desktop/server.py')
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
engine=server.Engine(server.find_library())
checks=0
try:
    entries=json.loads((ROOT/'assets/roster.json').read_text(encoding='utf-8'))['entries']
    for entry in entries:
        source=ROOT/'assets/vendor/spritecollab'/entry['directory']
        atlas=engine.assets(entry['id'])['animations'][0]
        tree=ET.parse(source/'AnimData.xml')
        nodes={n.findtext('Name'):n for n in tree.findall('./Anims/Anim')}
        for clip,name in enumerate(['Idle','Walk','Hop','Pose','Sleep','Eat','Sit','Hurt','LookUp']):
            while nodes[name].findtext('CopyOf'):name=nodes[name].findtext('CopyOf')
            node=nodes[name]
            w,h=int(node.findtext('FrameWidth')),int(node.findtext('FrameHeight'))
            sheet=Image.open(source/f'{name}-Anim.png').convert('RGBA')
            assert len(atlas[clip])==len(node.findall('./Durations/Duration'))
            for i,frame in enumerate(atlas[clip]):
                for y in range(h):
                    for x in range(w):
                        r,g,b,a=sheet.getpixel((i*w+x,y))
                        expected=65536 if not a else ((r//8)*2048+(g//4)*32+b//8)
                        px,py=x-w//2-frame['x'],y-h//2-frame['y']
                        actual=frame['pixels'][py*frame['width']+px] if 0<=px<frame['width'] and 0<=py<frame['height'] else 65536
                        assert actual==expected,(entry['path'],name,i,x,y)
                        checks+=1
    print(f'PASS: {checks} source pixels across {len(entries)} sets match compiled frames including transparent borders')
finally:
    engine.close()
