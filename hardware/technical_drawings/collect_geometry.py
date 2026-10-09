"""Read existing CAD without changing it; collect dimensions and visible edges."""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import cadquery as cq
from cadquery.occ_impl.exporters.svg import getSVG
from hardware.pokeball_v2.build import make_parts

OUT = ROOT / "output/pdf/pocket_pet_technical"
OUT.mkdir(parents=True, exist_ok=True)


def view(shape, direction):
    svg = getSVG(shape.val(), {"projectionDir": direction, "showAxes": False,
                              "showHidden": False, "width": 200, "height": 200,
                              "marginLeft": 10, "marginTop": 10})
    result = []
    for node in ET.fromstring(svg).iter():
        if node.tag.endswith("}path"):
            path = node.attrib["d"]
            commands = re.findall(r"[A-DF-Za-df-z]", path)
            assert set(commands) <= {"M", "L"}, commands
            values = [float(n) for n in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", path)]
            assert len(values) % 2 == 0
            result.append(list(zip(values[::2], values[1::2])))
    return result


def main():
    report = {"units": "mm", "sources": {}, "parts": {}}
    for name in ("hardware/pokeball_v1/build.py", "hardware/pokeball_v2/build.py"):
        report["sources"][name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    parts = make_parts()
    for name, shape in parts.items():
        b = shape.val().BoundingBox()
        item = {"valid": shape.val().isValid(), "solids": len(shape.solids().vals()),
                "bbox": [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax],
                "size": [b.xlen, b.ylen, b.zlen],
                "top": view(shape, (0, 0, 1)), "bottom": view(shape, (0, 0, -1))}
        if name in ("04_handheld_front", "05_handheld_back", "07_button_left", "11_battery_tray"):
            item["side"] = view(shape, (1, 0, 0))
        report["parts"][name] = item
        print(name, [round(v, 2) for v in item["size"]], item["valid"], item["solids"], flush=True)
    board = cq.importers.importStep(str(ROOT / "output/cad-research/ESP32-S3-LCD-2-20250122.stp"))
    b = board.val().BoundingBox()
    report["board_step_bbox"] = [b.xlen, b.ylen, b.zlen]
    (OUT / "geometry_reference.json").write_text(json.dumps(report), encoding="utf-8")


if __name__ == "__main__":
    main()
