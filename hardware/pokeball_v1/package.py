"""Bundle the verified design; generic 3MF plates carry geometry, no G-code."""
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile
import trimesh
from build import OUT, ROOT


def plate(name, placements):
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    tag = lambda name: f"{{{ns}}}{name}"
    model = ET.Element(tag("model"), {"unit":"millimeter", "xml:lang":"de-DE"})
    ET.SubElement(model,tag("metadata"),{"name":"Title"}).text = name
    resources, build = ET.SubElement(model,tag("resources")), ET.SubElement(model,tag("build"))
    for index, (prefix,x,y) in enumerate(placements,1):
        path, = (OUT/"STL_print").glob(f"{prefix}_*.stl")
        m = trimesh.load_mesh(path)
        obj = ET.SubElement(resources,tag("object"),{"id":str(index),"type":"model","name":path.stem})
        mesh = ET.SubElement(obj,tag("mesh"))
        vertices, triangles = ET.SubElement(mesh,tag("vertices")),ET.SubElement(mesh,tag("triangles"))
        for v in m.vertices:
            ET.SubElement(vertices,tag("vertex"),dict(zip(("x","y","z"),(f"{n:.6f}" for n in v))))
        for f in m.faces:
            ET.SubElement(triangles,tag("triangle"),dict(zip(("v1","v2","v3"),(str(n) for n in f))))
        dx,dy,dz = x-m.bounds[0,0], y-m.bounds[0,1], -m.bounds[0,2]
        ET.SubElement(build,tag("item"),{"objectid":str(index),"transform":f"1 0 0 0 1 0 0 0 1 {dx:.6f} {dy:.6f} {dz:.6f}"})
    with zipfile.ZipFile(OUT/f"{name}.3mf","w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("3D/3dmodel.model",ET.tostring(model,encoding="utf-8",xml_declaration=True))
        z.writestr("[Content_Types].xml",'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels",'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')


def drill_template():
    holes = []
    for x in (-16,0,16):
        for dx in (-3.25,3.25):
            for dy in (-2.25,2.25):
                holes.append(f'<circle cx="{45+x+dx}" cy="{23+dy}" r="0.5"/>')
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="90mm" height="52mm" viewBox="0 0 90 52">'
    svg += '<rect width="90" height="52" fill="white"/><g fill="black" font-family="Arial" font-size="3"><text x="5" y="6">TASTERPLATINE 43 x 12 x 1,6 mm / V1</text><text x="5" y="11">Druck 100 %, keine Seitenanpassung. Alle Masse in mm.</text></g>'
    svg += '<g fill="none" stroke="black" stroke-width="0.15"><rect x="23.5" y="17" width="43" height="12"/>' + ''.join(holes)
    svg += '<path d="M 5,39 h20 M 5,37 v4 M 25,37 v4"/></g><g fill="black" font-family="Arial" font-size="2.5"><text x="5" y="35">12 Bohrungen D1,0; je Taster 6,5 x 4,5; Tasterabstand 16.</text><text x="5" y="45">Kontrollmass 20 mm</text><text x="5" y="49">Omron B3F-1000: Lochlage vor Bohren am echten Taster pruefen.</text></g></svg>'
    (OUT/"Tasterplatine_Bohrbild_1zu1.svg").write_text(svg,encoding="utf-8")


def main():
    validation = json.loads((OUT/"validation.json").read_text())
    assert validation["build_source_sha256"] == hashlib.sha256((ROOT/"hardware/pokeball_v1/build.py").read_bytes()).hexdigest()
    for name, result in validation["meshes"].items():
        assert result["sha256"] == hashlib.sha256((OUT/"STL_print"/f"{name}.stl").read_bytes()).hexdigest()
        assert result["watertight"] and result["winding_consistent"] and result["positive_volume"] and result["components"] == 1
    for key, result in validation.items():
        if "collisions" in key:
            assert not result, key
    plate("START_Passproben",[("11",10,10),("12",65,10),("05",95,10)])
    plate("Platte_1_Schalen",[("01",12,12),("02",128,12)])
    plate("Platte_2_Innenteile",[("03",10,10),("04",120,10),("09",180,10),
                                  ("08",120,90),("05",120,115),("06",140,115),("07",160,115),("10",190,115)])
    drill_template()
    summary = {}
    for result_path in sorted((OUT/"slicer").glob("*/result.json")):
        result = json.loads(result_path.read_text())
        assert result["return_code"] == 0 and result["sliced_plates"], result_path
        p = result["sliced_plates"][0]
        summary[result_path.parent.name] = {"seconds":round(p["total_predication"]),
                                          "grams":round(sum(f["total_used_g"] for f in p["filaments"]),2),
                                          "warning":p.get("warning_message","")}
    assert len(summary)==12
    (OUT/"slicer_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    shutil.copyfile(ROOT/"hardware/pokeball_v1/README.md",OUT/"README.md")
    files = [p for p in OUT.iterdir() if p.is_file() and p.suffix in (".step",".3mf",".svg",".json",".md")]
    files += [OUT/"preview.png"]
    files += list((OUT/"STL_print").glob("*.stl")) + list((OUT/"STEP_parts").glob("*.step"))
    archive = OUT/"Pocket_Pet_V1_Druckpaket.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p,p.relative_to(OUT))
        for p in (ROOT/"hardware/pokeball_v1").iterdir():
            if p.is_file():
                z.write(p,p.relative_to(ROOT))
    print(archive,archive.stat().st_size)
    print("All parts separately:",sum(p["seconds"] for p in summary.values()),"seconds;",sum(p["grams"] for p in summary.values()),"grams")


if __name__ == "__main__":
    main()
