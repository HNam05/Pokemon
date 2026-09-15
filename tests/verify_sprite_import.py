"""Independent source-to-runtime pixel oracle; run with Pillow available."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('server',ROOT/'desktop/server.py')
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
source=ROOT/'assets/vendor/spritecollab/eevee-alternate'
engine=server.Engine(server.find_library())
checks=0
try:
    atlas=engine.assets()['animations'][1]
    tree=ET.parse(source/'AnimData.xml')
    for clip,name in enumerate(['Idle','Walk','Hop','Pose','Sleep','Eat','Sit','Hurt','LookUp']):
        node=next(n for n in tree.findall('./Anims/Anim') if n.findtext('Name')==name)
        w,h=int(node.findtext('FrameWidth')),int(node.findtext('FrameHeight'))
        sheet=Image.open(source/f'{name}-Anim.png').convert('RGBA')
        for i,frame in enumerate(atlas[clip]):
            for y in range(h):
                for x in range(w):
                    r,g,b,a=sheet.getpixel((i*w+x,y))
                    expected=65536 if not a else ((r//8)*2048+(g//4)*32+b//8)
                    px,py=x-w//2-frame['x'],y-h//2-frame['y']
                    actual=frame['pixels'][py*frame['width']+px] if 0<=px<frame['width'] and 0<=py<frame['height'] else 65536
                    assert actual==expected,(name,i,x,y)
                    checks+=1
    print(f'PASS: {checks} source pixels match compiled frames including transparent registration borders')
finally:
    engine.close()
