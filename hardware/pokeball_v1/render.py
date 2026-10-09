"""Render actual CAD geometry with VTK. No generated product imagery."""
from pathlib import Path
import vtk
from PIL import Image, ImageDraw, ImageFont
from build import OUT, HINGE_Y, HINGE_Z, box, make_parts


def actor(shape, color):
    vertices, faces = shape.val().tessellate(.15, .15)
    pts = vtk.vtkPoints()
    for v in vertices:
        pts.InsertNextPoint(v.x, v.y, v.z)
    cells = vtk.vtkCellArray()
    for face in faces:
        cells.InsertNextCell(3, face)
    poly = vtk.vtkPolyData()
    poly.SetPoints(pts)
    poly.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.SetFeatureAngle(45)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(mapper)
    a.GetProperty().SetColor(*color)
    a.GetProperty().SetAmbient(.25)
    a.GetProperty().SetDiffuse(.75)
    a.GetProperty().SetSpecular(.13)
    a.GetProperty().SetSpecularPower(22)
    return a


def render(parts, mode):
    ren = vtk.vtkRenderer()
    ren.SetBackground(.91, .895, .855)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1000, 1000)
    window.SetMultiSamples(8)
    window.AddRenderer(ren)
    colors = {"01": (.86,.845,.79), "02": (.70,.045,.035), "03": (.055,.065,.06),
              "04": (.28,.31,.29), "09": (.4,.43,.38)}
    for name, part in parts.items():
        if "coupon" in name:
            continue
        if mode == "inside" and name in ("02_lid", "03_control_deck", "10_front_emblem"):
            continue
        color = colors.get(name[:2], (.81,.79,.72))
        band = None
        if name == "01_lower_shell":
            mask = box(160,160,20,z=-2)
            band, part = part.intersect(mask), part.cut(mask)
        elif name == "02_lid":
            mask = box(160,160,30,z=-27.4)
            band, part = part.intersect(mask), part.cut(mask)
        if mode == "open" and name in ("02_lid", "10_front_emblem"):
            part = part.rotate((0,HINGE_Y,HINGE_Z),(1,HINGE_Y,HINGE_Z),-110)
            if band is not None:
                band = band.rotate((0,HINGE_Y,HINGE_Z),(1,HINGE_Y,HINGE_Z),-110)
        ren.AddActor(actor(part, color))
        if band is not None:
            ren.AddActor(actor(band,(.045,.05,.045)))
    if mode != "inside":
        # Display datum only, not a functional screen or an imported game asset.
        ren.AddActor(actor(box(30.6,40.8,.3,0,6.3,-3.8),(.105,.22,.18)))
    else:
        ren.AddActor(actor(box(36,63,5.2,z=-25.5),(.59,.62,.60)))
    ren.ResetCamera()
    camera = ren.GetActiveCamera()
    focal = (0,25,17) if mode == "open" else (0,0,-4)
    camera.SetFocalPoint(*focal)
    camera.SetPosition(150,-220,195 if mode != "inside" else 280)
    camera.SetViewUp(0,0,1)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(108 if mode == "open" else 76)
    ren.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / f"view_{mode}.png"))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def main():
    parts = make_parts()
    for mode in ("open", "closed", "inside"):
        render(parts, mode)
    font_path = "C:/Windows/Fonts/arial.ttf"
    title = ImageFont.truetype(font_path, 42)
    small = ImageFont.truetype(font_path, 24)
    canvas = Image.new("RGB", (1800, 810), (232,228,218))
    draw = ImageDraw.Draw(canvas)
    draw.text((42,26), "POCKET PET / GEHAEUSE V1", font=title, fill=(30,38,33))
    draw.text((44,84), "Waveshare ESP32-S3-LCD-2   |   Kugel 100 mm   |   Alle Ansichten aus den CAD-Dateien", font=small, fill=(54,63,56))
    for i, (mode,label) in enumerate((("open","110 Grad geoeffnet"),("closed","Geschlossen / Schraubverschluss"),("inside","Innenraum / Bedienplatte abgenommen"))):
        canvas.paste(Image.open(OUT/f"view_{mode}.png").resize((600,600)), (600*i,130))
        draw.text((600*i+22,741), label, font=small, fill=(30,38,33))
    canvas.save(OUT/"preview.png")


if __name__ == "__main__":
    main()
