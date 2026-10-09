"""Independent STL topology and CAD collision/kinematic checks for V2."""
import hashlib
import itertools
import json
import math
import cadquery as cq
import trimesh
from build import OUT,ROOT,HY,HZ,LIFT,box,cyl,make_parts,is_handheld


def overlap(a,b):
    ba,bb = a.val().BoundingBox(),b.val().BoundingBox()
    if any(min(getattr(ba,k+"max"),getattr(bb,k+"max"))-max(getattr(ba,k+"min"),getattr(bb,k+"min"))<1e-7 for k in "xyz"):
        return 0.0
    return sum(s.Volume() for s in a.val().intersect(b.val()).Solids())


def source_hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [ROOT/"hardware/pokeball_v2/build.py",ROOT/"hardware/pokeball_v1/build.py"]}


def main():
    parts = make_parts()
    fixed = {n:s for n,s in parts.items() if "coupon" not in n}
    result = {"sources":source_hashes(),"meshes":{},"assembly_collisions":[],"cover_motion_collisions":[],
              "extraction_collisions":[],"hardware_collisions":[],"button_motion_collisions":[]}
    for path in sorted((OUT/"STL_print").glob("*.stl")):
        m = trimesh.load_mesh(path)
        result["meshes"][path.stem] = {"watertight":bool(m.is_watertight),"winding":bool(m.is_winding_consistent),
                                      "components":len(m.split()),"volume_positive":bool(m.volume>0),
                                      "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    for (an,a),(bn,b) in itertools.combinations(fixed.items(),2):
        v = overlap(a,b)
        if v>.01: result["assembly_collisions"].append([an,bn,round(v,3)])
    print("Pair checks",result["assembly_collisions"],flush=True)
    lid = fixed["02_ball_lid"].union(fixed["12_ball_emblem"])
    for angle in range(0,131,5):
        moved = lid.rotate((0,HY,HZ),(1,HY,HZ),-angle)
        for name,part in fixed.items():
            if name in ("02_ball_lid","12_ball_emblem"): continue
            v = overlap(moved,part)
            if v>.01: result["cover_motion_collisions"].append([angle,name,round(v,3)])
    opened = lid.rotate((0,HY,HZ),(1,HY,HZ),-110)
    obstacles = {"ball":fixed["01_ball_lower"],"cradle":fixed["03_removable_cradle"],"cover_open110":opened}
    for height in (0,1,3,6,10,15,20,30,45,60,80,100):
        for name,part in fixed.items():
            if not is_handheld(name): continue
            for obstacle,shape in obstacles.items():
                v = overlap(part.translate((0,0,height)),shape)
                if v>.01: result["extraction_collisions"].append([height,name,obstacle,round(v,3)])
    print("Motion checks",result["cover_motion_collisions"],result["extraction_collisions"],flush=True)
    board = cq.importers.importStep(str(ROOT/"output/cad-research/ESP32-S3-LCD-2-20250122.stp"))
    board = board.rotate((0,0,0),(0,0,1),180).translate((0,6.3,-5.9+LIFT))
    hardware = {"official_board":board,"max_battery":box(36,63,5.2,z=-25.5+LIFT),
                "switch_pcb":box(43,12,1.6,y=-28,z=-12.4+LIFT)}
    for label,part in hardware.items():
        for name,obstacle in fixed.items():
            v = overlap(part,obstacle)
            if v>.01: result["hardware_collisions"].append([label,name,round(v,3)])
    for name,button in fixed.items():
        if not name.startswith(("07_","08_","09_")): continue
        for travel in (0,.2,.45,.6):
            for angle in range(8):
                dx,dy = .25*math.cos(angle*math.pi/4),.25*math.sin(angle*math.pi/4)
                moved = button.translate((dx,dy,-travel))
                for target in ("04_handheld_front","10_switch_tray"):
                    v = overlap(moved,fixed[target])
                    if v>.01: result["button_motion_collisions"].append([name,travel,angle,target,round(v,3)])
    (OUT/"validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if "collisions" in k},indent=2))
    assert len(result["meshes"])==15
    assert all(m["watertight"] and m["winding"] and m["components"]==1 and m["volume_positive"] for m in result["meshes"].values())
    assert all(not v for k,v in result.items() if "collisions" in k), "Collisions remain"


if __name__=="__main__":
    main()
