"""Read-only OCCT intersection check of proposed electronics envelopes."""
from pathlib import Path
import sys
import json
import hashlib
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import cadquery as cq
from hardware.pokeball_v2.build import make_parts
from hardware.pokeball_v1.build import box

OUT = ROOT / 'output/pdf/pocket_pet_technical_rev_b'
OUT.mkdir(parents=True, exist_ok=True)
parts = make_parts()
board_path = ROOT / 'output/cad-research/ESP32-S3-LCD-2-20250122.stp'
board = cq.importers.importStep(str(board_path)).rotate((0,0,0),(0,0,1),180).translate((0,6.3,.1))
items = {'E01_board_step':board,
         'E04_battery_max':box(36,63,5.2,0,0,-19.5),
         'E03_FR4':box(43,12,1.6,0,-28,-6.4),
         'E08_speaker_candidate':box(30,20,5,9.5,-26,-13.8),
         'E09_amp_flat_candidate':box(17.8,19.4,3,-17.2,-26,-13.3)}
for x in (-16,0,16):
    items[f'E02_switch_{x}'] = box(6,6,4.3,x,-28,-4.8)
report = {'units':'mm','board_step_sha256':hashlib.sha256(board_path.read_bytes()).hexdigest(),
          'sources':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                     ('hardware/pokeball_v1/build.py','hardware/pokeball_v2/build.py')},
          'scope':'Electronic nominal envelopes versus existing handheld CAD and one another',
          'excluded':['cables','solder joints and switch leads','audio holders','speaker membrane motion',
                      'amplifier terminal block','fasteners','printed part to printed part validation','ball motion'],
          'physical_validation':False,'items':{},'intersections':[],'pairs_checked':0}
for name, shape in items.items():
    b=shape.val().BoundingBox()
    report['items'][name]={'bbox':[round(v,5) for v in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)],'size':[round(v,5) for v in (b.xlen,b.ylen,b.zlen)]}
all_items={**{n:p for n,p in parts.items() if 4<=int(n[:2])<=11},**items}
names=list(all_items)
for i,a in enumerate(names):
    for b in names[i+1:]:
        if a in parts and b in parts: continue
        report['pairs_checked']+=1
        ba,bb=all_items[a].val().BoundingBox(),all_items[b].val().BoundingBox()
        if any(min(getattr(ba,k+'max'),getattr(bb,k+'max'))-max(getattr(ba,k+'min'),getattr(bb,k+'min'))<1e-7 for k in 'xyz'): continue
        v=sum(s.Volume() for s in all_items[a].val().intersect(all_items[b].val()).Solids())
        if v>1e-5: report['intersections'].append({'a':a,'b':b,'volume_mm3':round(v,5)})
(OUT/'integration_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
