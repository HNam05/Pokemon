"""V2: independent handheld in removable cradle inside a protective ball.

All coordinates mm. Handheld is shown seated, front facing +Z; rear/USB is +Y.
V1 is read-only; reuse its proven bought-part adapters and geometry primitives.
"""
from pathlib import Path
import sys
import json
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hardware.pokeball_v1.build import box, cyl, rounded, make_parts as v1_parts

OUT = ROOT / "output/pokeball_v2"
R, WALL, GAP = 65.0, 2.4, .6
HY, HZ = 67.0, .3
LIFT = 6.0
CASE_SCREWS = [(x,y) for x in (-26,26) for y in (-13,13)]
BOARD_SCREWS = [(x,y) for x in (-23,23) for y in (-18,34)]
DOCK_SCREWS = [(x,y) for x in (-24,24) for y in (-20,20)]


def cone(r1, r2, height, x, y, z):
    return cq.Workplane("XY").newObject([cq.Solid.makeCone(r1,r2,height,cq.Vector(x,y,z))])


def knuckle(x, length):
    return cq.Workplane("YZ").circle(4.2).circle(1.7).extrude(length).translate((x,HY,HZ))


def make_parts():
    old = v1_parts()
    # A closed independent 62 x 90 mm housing replaces the round control deck.
    front = rounded(62,90,2.4,6,y=2,z=-3.4)
    walls = rounded(62,90,13.6,6,y=2,z=-17).cut(rounded(57.2,85.2,16,3.6,y=2,z=-18))
    front = front.union(walls)
    front = front.cut(box(31.2,41.4,10,0,6.2,-7))
    for x in (-18.4,18.4):
        front = front.union(box(1.2,47,3.5,x,8,-6.9))
    for x,y in BOARD_SCREWS:
        front = front.union(cyl(3.3,8.7,x,y,-12.1)).cut(cyl(.8,7.5,x,y,-12.2))
    for x in (-25,25):
        front = front.union(cyl(3,9,x,-28,-12.4))
        front = front.union(box(3,6,1.5,21.5 if x>0 else -21.5,-28,-10.8))
        front = front.cut(cyl(.8,8,x,-28,-12.5))
    for x in (-16,0,16):
        front = front.cut(cyl(5,8,x,-28,-6))
    for x,y in CASE_SCREWS:
        boss = cyl(2.5,26.6,x,y,-30).intersect(rounded(62,90,30,6,y=2,z=-31))
        front = front.union(boss).cut(cyl(.8,8,x,y,-30.1))
    front = front.cut(box(16,25,11,0,43,-16))

    back = rounded(62,90,15.4,6,y=2,z=-32.4)
    # 2.4 mm back plate, 13 mm deep side wall, open towards the front.
    back = back.cut(rounded(57.2,85.2,13,3.6,y=2,z=-30))
    for x,y in CASE_SCREWS:
        # The enlarged screw-head relief passes only through the 2.4-mm rear skin.
        back = back.cut(cyl(3.1,2.4,x,y,-32.4))
        back = back.cut(cyl(1.15,5,x,y,-33))
        back = back.cut(cone(2.4,1.15,1.25,x,y,-32.4))
    for x in (-23.5,23.5):
        back = back.union(cyl(3.8,2.5,x,0,-30))
        back = back.cut(cyl(1.25,4.1,x,0,-31.5))

    outer, inner = cq.Workplane("XY").sphere(R), cq.Workplane("XY").sphere(R-WALL)
    lower = outer.intersect(box(160,160,59,z=-59)).cut(inner.intersect(box(160,160,65,z=-56.6)))
    for x,y in DOCK_SCREWS:
        lower = lower.union(cyl(4,29.6,x,y,-59).intersect(outer))
        lower = lower.cut(cyl(1.25,10,x,y,-38.4))
    lower = lower.cut(box(14.4,20,7,0,68,-5.5))
    for x in (-18,7.2):
        lower = lower.union(box(10.8,7.5,8.3,x+5.4,63.25,-8)).union(knuckle(x,10.8))
    lower = lower.union(box(12,8.7,6,0,-64.65,-6)).cut(cyl(1.3,9,0,-66,-8))

    lid = outer.intersect(box(160,160,59,z=0)).cut(inner.intersect(box(160,160,56.6,z=0))).translate((0,0,GAP))
    for x in (-19,7):
        lid = lid.cut(cq.Workplane("YZ").circle(4.5).extrude(12).translate((x,HY,HZ)))
    lid = lid.union(box(13.6,7,6.2,0,63.5,.3)).union(knuckle(-6.8,13.6))
    lid = lid.union(box(12,9,5,0,-64.5,.6))
    lid = lid.cut(cyl(1.7,65,0,-66,0)).cut(cyl(3.2,70,0,-66,5.6))
    lid = lid.union(box(8,1,3,0,-69.05,1.2))
    badge = cq.Workplane("XZ").circle(8.5).extrude(1.8).translate((0,-69.55,.3))

    # Open cradle: a spine and two crossbars support the back, not the buttons.
    cradle = box(12,94.8,3,0,2,-29.4)
    for y in (-20,20):
        cradle = cradle.union(box(68.8,8,3,0,y,-29.4))
    for x in (-33.2,33.2):
        cradle = cradle.union(box(2.4,80,14.2,x,2,-26.6))
        # 10-mm textile retaining strap passes through these side slots.
        cradle = cradle.cut(box(5,11,2.2,x,33,-17))
    for y in (-45.2,49.2):
        cradle = cradle.union(box(20,2.4,12.2,0,y,-26.6))
    for x,y in DOCK_SCREWS:
        cradle = cradle.cut(cyl(1.65,6,x,y,-31))
        cradle = cradle.cut(cone(1.65,3.35,1.7,x,y,-28.1))

    # A short rail coupon checks the actual 64-mm cradle opening against the case.
    fit = box(68.8,12,2.4)
    for x in (-33.2,33.2):
        fit = fit.union(box(2.4,12,9,x,0,2.4))
    parts = {"01_ball_lower":lower,"02_ball_lid":lid,"03_removable_cradle":cradle,
             "04_handheld_front":front.translate((0,0,LIFT)),
             "05_handheld_back":back.translate((0,0,LIFT)),
             "06_board_carrier":old["04_board_carrier"].translate((0,0,LIFT)),
             "07_button_left":old["05_button_left"].translate((0,0,LIFT)),
             "08_button_ok":old["06_button_ok"].translate((0,0,LIFT)),
             "09_button_right":old["07_button_right"].translate((0,0,LIFT)),
             "10_switch_tray":old["08_switch_tray"].translate((0,0,LIFT)),
             "11_battery_tray":old["09_battery_tray"].translate((0,0,LIFT)),
             "12_ball_emblem":badge,"13_button_fit_coupon":old["11_button_fit_coupon"],
             "14_hinge_fit_coupon":old["12_hinge_fit_coupon"],"15_cradle_fit_coupon":fit}
    for x,y in CASE_SCREWS:
        parts["06_board_carrier"] = parts["06_board_carrier"].cut(cyl(3,4,x,y,-9))
    return parts


def is_handheld(name):
    return 4 <= int(name[:2]) <= 11


def print_pose(name, part):
    if name in ("02_ball_lid","04_handheld_front") or name.startswith(("07_","08_","09_")):
        part = part.rotate((0,0,0),(1,0,0),180)
    if name == "12_ball_emblem":
        part = part.rotate((0,0,0),(1,0,0),90)
    b = part.val().BoundingBox()
    return part.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))


def main():
    for folder in (OUT,OUT/"STL_print",OUT/"STEP_parts"):
        folder.mkdir(parents=True,exist_ok=True)
    parts = make_parts()
    assembly, handheld = cq.Assembly(name="Pocket_Pet_V2"), cq.Assembly(name="Standalone_Handheld")
    report = {}
    for name,part in parts.items():
        assert part.val().isValid() and len(part.solids().vals())==1, name
        posed = print_pose(name,part)
        cq.exporters.export(posed,str(OUT/"STL_print"/f"{name}.stl"),tolerance=.06,angularTolerance=.12)
        cq.exporters.export(part,str(OUT/"STEP_parts"/f"{name}.step"))
        b = posed.val().BoundingBox()
        report[name] = {"print_size_mm":[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)],"cad_valid":True}
        if "coupon" not in name:
            c = cq.Color(.7,.05,.035) if name.startswith("02") else cq.Color(.78,.77,.72)
            assembly.add(part,name=name,color=c)
            if is_handheld(name):
                handheld.add(part,name=name,color=c)
        print(name,report[name],flush=True)
    assembly.export(str(OUT/"Pocket_Pet_V2_assembly.step"))
    handheld.export(str(OUT/"Handheld_V2.step"))
    (OUT/"geometry.json").write_text(json.dumps(report,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
