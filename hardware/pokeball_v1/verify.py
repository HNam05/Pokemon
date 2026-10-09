"""CAD interference checks plus independent exported STL topology checks."""
import itertools
import json
import hashlib
import math
import cadquery as cq
import trimesh
from build import OUT, ROOT, HINGE_Y, HINGE_Z, box, cyl, make_parts


def overlap(a, b):
    ba, bb = a.val().BoundingBox(), b.val().BoundingBox()
    if any(min(getattr(ba,axis+"max"),getattr(bb,axis+"max")) - max(getattr(ba,axis+"min"),getattr(bb,axis+"min")) < 1e-7 for axis in "xyz"):
        return 0.0
    common = a.val().intersect(b.val())
    return sum(s.Volume() for s in common.Solids())


def main():
    parts = make_parts()
    meshes = {}
    for path in sorted((OUT / "STL_print").glob("*.stl")):
        m = trimesh.load_mesh(path)
        meshes[path.stem] = {"watertight": bool(m.is_watertight),
                             "winding_consistent": bool(m.is_winding_consistent),
                             "positive_volume": bool(m.volume > 0),
                             "components": len(m.split()), "faces": len(m.faces),
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    fixed = {n: p for n, p in parts.items() if "coupon" not in n}
    collisions = []
    for (an, a), (bn, b) in itertools.combinations(fixed.items(), 2):
        v = overlap(a, b)
        if v > .01:
            collisions.append([an, bn, round(v, 4)])
    moving = parts["02_lid"].union(parts["10_front_emblem"])
    sweep = []
    for angle in range(0, 131, 5):
        opened = moving.rotate((0, HINGE_Y, HINGE_Z), (1, HINGE_Y, HINGE_Z), -angle)
        for name, solid in fixed.items():
            if name in ("02_lid", "10_front_emblem"):
                continue
            v = overlap(opened, solid)
            if v > .01:
                sweep.append([angle, name, round(v, 4)])
    board_file = ROOT / "output/cad-research/ESP32-S3-LCD-2-20250122.stp"
    board = cq.importers.importStep(str(board_file)).rotate((0, 0, 0), (0, 0, 1), 180).translate((0, 6.3, -5.9))
    board_collisions = []
    for name, shape in fixed.items():
        v = overlap(board, shape)
        if v > .01:
            board_collisions.append([name, round(v, 4)])
    result = {"meshes": meshes, "assembly_collisions_mm3": collisions,
              "build_source_sha256": hashlib.sha256((ROOT/"hardware/pokeball_v1/build.py").read_bytes()).hexdigest(),
              "lid_sweep_0_to_130_step5_collisions_mm3": sweep,
              "official_board_collisions_mm3": board_collisions}
    envelopes = {"battery_max_36x63x5.2": box(36,63,5.2,z=-25.5),
                 "switch_pcb_43x12x1.6": box(43,12,1.6,y=-28,z=-12.4)}
    envelope_collisions = []
    for label, envelope in envelopes.items():
        for name, shape in {**fixed, "official_board": board}.items():
            v = overlap(envelope, shape)
            if v > .01:
                envelope_collisions.append([label,name,round(v,4)])
    result["purchased_part_envelope_collisions_mm3"] = envelope_collisions
    travel_collisions = []
    for name, button in fixed.items():
        if "button" not in name:
            continue
        for travel in (0,.2,.45,.6):
            offsets = [(0,0)] + [(.25*math.cos(a*math.pi/4),.25*math.sin(a*math.pi/4)) for a in range(8)]
            for dx,dy in offsets:
                for obstacle in ("03_control_deck","08_switch_tray"):
                    v = overlap(button.translate((dx,dy,-travel)), fixed[obstacle])
                    if v > .01:
                        travel_collisions.append([name,travel,[dx,dy],obstacle,round(v,4)])
    result["button_0_to_0.6mm_travel_collisions_mm3"] = travel_collisions
    result["button_radial_play_tested_mm"] = .25
    head_collisions = []
    head_spaces = {"closure_head":cyl(2.8,3,0,-51,5.6),
                   "battery_head_left":cyl(2.8,3,-23.5,0,-25.5),
                   "battery_head_right":cyl(2.8,3,23.5,0,-25.5)}
    for label, head in head_spaces.items():
        for name, shape in fixed.items():
            v = overlap(head, shape)
            if v > .01:
                head_collisions.append([label,name,round(v,4)])
    result["screw_head_clearance_collisions_mm3"] = head_collisions
    (OUT / "validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    assert all(m["watertight"] and m["winding_consistent"] and m["positive_volume"] and m["components"] == 1 for m in meshes.values())
    assert not (collisions or sweep or board_collisions or envelope_collisions or travel_collisions or head_collisions), "Mechanical collisions remain"


if __name__ == "__main__":
    main()
