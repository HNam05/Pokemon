"""Own parametric Pocket Pet enclosure. Millimetres; CadQuery 2.8.

Run with the CAD venv, never the game runtime. Outputs stay in output/.
Assembly: XY equator, +Y hinge/USB, +Z cover, LCD faces +Z.
"""
from pathlib import Path
import json
import math
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/pokeball_v1"
R, WALL, GAP = 50.0, 2.4, 0.6
DECK_R, DECK_Z, DECK_T = 46.9, -3.4, 2.4
HINGE_Y, HINGE_Z = 52.0, 0.3
DECK_SCREWS = [(-39, 0), (39, 0), (-33, 27), (33, 27)]
BOARD_SCREWS = [(x, y) for x in (-23, 23) for y in (-18, 34)]
BUTTON_X = (-16, 0, 16)


def box(w, d, h, x=0, y=0, z=0):
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((x, y, z))


def cyl(r, h, x=0, y=0, z=0):
    return cq.Workplane("XY").circle(r).extrude(h).translate((x, y, z))


def rounded(w, d, h, radius, x=0, y=0, z=0):
    return box(w, d, h, x, y, z).edges("|Z").fillet(radius)


def hinge(x0, length):
    return (cq.Workplane("YZ").circle(4.2).circle(1.7).extrude(length)
            .translate((x0, HINGE_Y, HINGE_Z)))


def make_parts():
    outer = cq.Workplane("XY").sphere(R)
    inner = cq.Workplane("XY").sphere(R-WALL)
    # Flat poles leave a true 2.4 mm floor, rather than thinning a sphere by clipping.
    lower = outer.intersect(box(130, 130, 45, z=-45)).cut(
        inner.intersect(box(130, 130, 60, z=-42.6)))
    for x, y in DECK_SCREWS:
        support = cyl(4.0, 27, x, y, -30.4).intersect(outer)
        lower = lower.union(support).cut(cyl(1.25, 10, x, y, -11.4))
    for x in (-23.5, 23.5):
        lower = lower.union(cyl(4, 17.5, x, 0, -45).intersect(outer))
        lower = lower.cut(cyl(1.25, 9, x, 0, -34.5))
    # Rear access is a roomy recessed cable corridor, not an assumed panel-mount port.
    lower = lower.cut(box(22, 35, 13, 0, 47, -17))
    # Space for the cover's middle knuckle, including below the equator.
    lower = lower.cut(box(14.4, 20, 7, 0, 53, -5.5))
    for x in (-18, 7.2):
        lower = lower.union(box(10.8, 7.5, 8.3, x+5.4, 48.25, -8))
        lower = lower.union(hinge(x, 10.8))
    lower = lower.union(box(12, 8.7, 6, 0, -49.65, -6))
    lower = lower.cut(cyl(1.3, 9, 0, -51, -8))

    lid = outer.intersect(box(130, 130, 45, z=0)).cut(
        inner.intersect(box(130, 130, 42.6, z=0))).translate((0, 0, GAP))
    for x in (-19, 7.0):
        lid = lid.cut(cq.Workplane("YZ").circle(4.5).extrude(12).translate((x, HINGE_Y, HINGE_Z)))
    lid = lid.union(box(13.6, 7, 6.2, 0, 48.5, 0.3)).union(hinge(-6.8, 13.6))
    lid = lid.union(box(12, 9, 5, 0, -49.5, GAP))
    lid = lid.cut(cyl(1.7, 65, 0, -51, 0))
    # The screw head and driver need clearance from the curved shell above the ear.
    lid = lid.cut(cyl(3.2, 55, 0, -51, 5.6))
    # Shallow locating recess for a separately printed white emblem.
    badge = (cq.Workplane("XZ").circle(8.5).extrude(1.8)
             .translate((0, -54.55, 0.3)))
    # XZ normal points -Y; badge glues to the lid stem, clear of the lower tab.
    lid = lid.union(box(8, 1.0, 3.0, 0, -54.05, 1.2))

    deck = cyl(DECK_R, DECK_T, z=DECK_Z)
    deck = deck.cut(box(13, 12, 8, 0, -51, -7))
    deck = deck.cut(box(40, 12, 8, 0, 50, -7))
    # Board rotated 180 degrees: USB toward hinge. Active area offset from outline.
    deck = deck.cut(box(31.2, 41.4, 10, 0, 6.2, -6))
    # Narrow rails locate the module without assuming the entire bezel is active glass.
    for x in (-18.4, 18.4):
        deck = deck.union(box(1.2, 47, 3.5, x, 8, -6.9))
    for x, y in BOARD_SCREWS:
        deck = deck.union(cyl(3.3, 8.7, x, y, -12.1))
        deck = deck.cut(cyl(1.05, 7.5, x, y, -12.2))
    for x in (-25, 25):
        deck = deck.union(cyl(3, 9, x, -28, -12.4))
        deck = deck.union(box(3.0, 6, 1.5, math.copysign(21.5, x), -28, -10.8))
        deck = deck.cut(cyl(1.05, 8, x, -28, -12.5))
    for x in BUTTON_X:
        deck = deck.cut(cyl(5, 8, x, -28, -6))
    for x, y in DECK_SCREWS:
        deck = deck.cut(cyl(1.6, 6, x, y, -5))
        deck = deck.cut(cyl(3, 1.2, x, y, -2.2))
    # A slot above the recessed USB plug keeps the insertion path visible.
    deck = deck.cut(box(15, 16, 8, 0, 40, -7))

    carrier = rounded(53, 56, 2, 2, y=8, z=-14.1)
    carrier = carrier.cut(box(41, 49, 5, 0, 8, -15))
    for x in (-14.5, 14.5):
        for y, sign in ((-13.1, -1), (29.1, 1)):
            carrier = carrier.union(box(5.4, 7, 2, x, y+sign*2, -14.1))
            carrier = carrier.cut(cyl(1.15, 5, x, y, -15))
    for x, y in BOARD_SCREWS:
        carrier = carrier.cut(cyl(1.25, 5, x, y, -15))
    # Preserve the complete USB insertion corridor through the rear rail.
    carrier = carrier.cut(box(15, 12, 6, 0, 36, -16))

    buttons = {}
    for i, x in enumerate(BUTTON_X):
        cap = cyl(5.6, 1.2, x, -28, -4.6).union(cyl(4.75, 4.2, x, -28, -3.4))
        cap = cap.union(cyl(1.7, 1.7, x, -28, -6.3))
        if i == 1:
            cap = cap.cut(cyl(1.5, 0.5, x, -28, 0.5))
        else:
            cap = cap.cut(box(3.5, 0.8, 0.5, x, -28, 0.5))
        buttons[f"0{5+i}_button_{('left','ok','right')[i]}"] = cap

    switch_tray = rounded(56, 15, 2, 2, y=-28, z=-14.4)
    for x in (-25, 25):
        switch_tray = switch_tray.cut(cyl(1.25, 5, x, -28, -16))
    # 43 x 12 x 1.6 mm drilled FR4: perimeter support, free solder space beneath.
    switch_tray = switch_tray.cut(box(41, 10, 5, 0, -28, -16))
    for x in (-22, 22):
        switch_tray = switch_tray.union(box(.6, 12.6, 1.5, x, -28, -12.4))
    for y in (-34.5, -21.5):
        switch_tray = switch_tray.union(box(43.4, .6, 1.5, 0, y, -12.4))
    for x in (-25, 25):
        switch_tray = switch_tray.cut(cyl(3.2, 3, x, -28, -12.4))

    tray = rounded(42, 69, 2, 5, z=-27.5)
    walls = rounded(42, 69, 5, 5, z=-25.5).cut(rounded(38, 65, 7, 3, z=-26))
    tray = tray.union(walls)
    for x in (-23.5, 23.5):
        tray = tray.union(box(8, 10, 2, x, 0, -27.5))
        tray = tray.cut(cyl(1.6, 5, x, 0, -29))
        tray = tray.cut(cyl(3.2, 7, x, 0, -25.5))
    tray = tray.cut(box(12, 7, 6, 0, 33, -25.5))
    # Two slots for a soft strap; the cell is not compressed by a screw.
    for x in (-18.5, 18.5):
        tray = tray.cut(box(2, 12, 4, x, 0, -29))

    coupon = rounded(46, 19, 2.4, 2)
    for x, radius in ((-14, 4.9), (0, 5.0), (14, 5.1)):
        coupon = coupon.cut(cyl(radius, 5, x, 0, -1))
    hinge_coupon = box(16, 12, 3).union(
        cq.Workplane("YZ").circle(4.2).extrude(16).translate((-8, 0, 6.5)))
    hinge_coupon = hinge_coupon.cut(
        cq.Workplane("YZ").circle(1.7).extrude(20).translate((-10, 0, 6.5)))
    parts = {"01_lower_shell": lower, "02_lid": lid, "03_control_deck": deck,
             "04_board_carrier": carrier, **buttons, "08_switch_tray": switch_tray,
             "09_battery_tray": tray, "10_front_emblem": badge,
             "11_button_fit_coupon": coupon, "12_hinge_fit_coupon": hinge_coupon}
    return parts


def print_pose(name, shape):
    # Flip lid to its flat pole; flip deck so its visible face is on the bed.
    # Buttons stand on their visible 9.5 mm face, with the actuator facing up.
    if name in ("02_lid", "03_control_deck") or "button_" in name and "coupon" not in name:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    if name == "10_front_emblem":
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    b = shape.val().BoundingBox()
    return shape.translate((-(b.xmin+b.xmax)/2, -(b.ymin+b.ymax)/2, -b.zmin))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "STL_print").mkdir(exist_ok=True)
    (OUT / "STEP_parts").mkdir(exist_ok=True)
    parts = make_parts()
    report = {}
    assembly = cq.Assembly(name="Pocket_Pet_V1")
    colors = {"01": (0.88, .85, .78), "02": (.68, .055, .045), "03": (.075, .085, .08)}
    for name, shape in parts.items():
        solid = shape.val()
        if not solid.isValid() or len(shape.solids().vals()) != 1:
            raise ValueError(f"Invalid or disconnected CAD part: {name}")
        posed = print_pose(name, shape)
        cq.exporters.export(posed, str(OUT / "STL_print" / f"{name}.stl"), tolerance=.06, angularTolerance=.12)
        cq.exporters.export(shape, str(OUT / "STEP_parts" / f"{name}.step"))
        b = posed.val().BoundingBox()
        report[name] = {"print_bbox_mm": [round(b.xlen, 3), round(b.ylen, 3), round(b.zlen, 3)],
                        "volume_mm3": round(solid.Volume(), 2), "cad_valid": True}
        if "coupon" not in name:
            assembly.add(shape, name=name, color=cq.Color(*colors.get(name[:2], (.7, .69, .64))))
        print(name, report[name], flush=True)
    assembly.export(str(OUT / "Pocket_Pet_V1_assembly.step"))
    (OUT / "geometry.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
