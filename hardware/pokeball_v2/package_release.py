"""Create download-ready V2 geometry plates from validated CAD exports."""
import json
import shutil
import trimesh
import xml.etree.ElementTree as ET
import zipfile
from build import OUT, ROOT

RELEASE = ROOT / "hardware/pokeball_v2/release"
PLATES = {
    "00_Passproben": [("13", 8, 8), ("14", 65, 8), ("15", 90, 8)],
    "01_Ball_unten": [("01", 8, 8)],
    "02_Ball_Deckel": [("02", 8, 8)],
    "03_Handheld_und_Halter": [("04", 8, 8), ("05", 78, 8), ("03", 148, 8),
                                ("06", 8, 112), ("10", 70, 112), ("11", 132, 112),
                                ("07", 198, 112), ("08", 213, 112), ("09", 228, 112),
                                ("12", 198, 132)],
}


def make_plate(name, placements):
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    tag = lambda item: f"{{{ns}}}{item}"
    model = ET.Element(tag("model"), {"unit": "millimeter", "xml:lang": "de-DE"})
    ET.SubElement(model, tag("metadata"), {"name": "Title"}).text = name
    resources = ET.SubElement(model, tag("resources"))
    build = ET.SubElement(model, tag("build"))
    for index, (prefix, x, y) in enumerate(placements, 1):
        path, = (OUT / "STL_print").glob(f"{prefix}_*.stl")
        mesh = trimesh.load_mesh(path)
        obj = ET.SubElement(resources, tag("object"),
                            {"id": str(index), "type": "model", "name": path.stem})
        geometry = ET.SubElement(obj, tag("mesh"))
        vertices = ET.SubElement(geometry, tag("vertices"))
        triangles = ET.SubElement(geometry, tag("triangles"))
        for vertex in mesh.vertices:
            ET.SubElement(vertices, tag("vertex"), dict(zip(
                ("x", "y", "z"), (f"{value:.6f}" for value in vertex))))
        for face in mesh.faces:
            ET.SubElement(triangles, tag("triangle"), dict(zip(
                ("v1", "v2", "v3"), (str(value) for value in face))))
        delta = (x - mesh.bounds[0, 0], y - mesh.bounds[0, 1], -mesh.bounds[0, 2])
        transform = f"1 0 0 0 1 0 0 0 1 {delta[0]:.6f} {delta[1]:.6f} {delta[2]:.6f}"
        ET.SubElement(build, tag("item"), {"objectid": str(index), "transform": transform})
    path = RELEASE / f"{name}.3mf"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))
        archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')


def main():
    validation = json.loads((OUT / "validation.json").read_text(encoding="utf-8"))
    assert not any(value for key, value in validation.items() if "collisions" in key)
    assert len(validation["meshes"]) == 15
    RELEASE.mkdir(parents=True, exist_ok=True)
    for folder in ("STL_print", "STEP_parts"):
        destination = RELEASE / folder
        destination.mkdir(parents=True, exist_ok=True)
        for source in (OUT / folder).glob("*"):
            if source.is_file():
                shutil.copy2(source, destination / source.name)
    for name, placements in PLATES.items():
        make_plate(name, placements)
    for name in ("Pocket_Pet_V2_assembly.step", "Handheld_V2.step", "validation.json", "preview.png"):
        shutil.copy2(OUT / name, RELEASE / name)
    for path in RELEASE.rglob("*.step"):
        lines = path.read_bytes().splitlines()
        path.write_bytes(b"\n".join(line.rstrip(b" \t") for line in lines) + b"\n")
    print("Release prepared:", RELEASE)
    print("STL:", len(list((RELEASE / "STL_print").glob("*.stl"))),
          "STEP:", len(list((RELEASE / "STEP_parts").glob("*.step"))),
          "3MF:", len(list(RELEASE.glob("*.3mf"))))


if __name__ == "__main__":
    main()
