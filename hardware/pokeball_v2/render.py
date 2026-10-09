"""Render actual V2 CAD solids for assembly review."""
from pathlib import Path
import vtk
from PIL import Image,ImageDraw,ImageFont
from build import OUT,HY,HZ,box,make_parts,is_handheld


def actor(shape,color):
    vertices,faces=shape.val().tessellate(.18,.15)
    points=vtk.vtkPoints()
    for v in vertices: points.InsertNextPoint(v.x,v.y,v.z)
    cells=vtk.vtkCellArray()
    for f in faces: cells.InsertNextCell(3,f)
    data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(45)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    result=vtk.vtkActor();result.SetMapper(mapper);result.GetProperty().SetColor(*color)
    result.GetProperty().SetAmbient(.27);result.GetProperty().SetDiffuse(.73)
    result.GetProperty().SetSpecular(.15);result.GetProperty().SetSpecularPower(24)
    return result


def view(parts,which):
    renderer=vtk.vtkRenderer();renderer.SetBackground(.92,.91,.88)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1000,950);window.SetMultiSamples(8);window.AddRenderer(renderer)
    colors={"01":(.84,.82,.75),"02":(.68,.045,.035),"03":(.66,.66,.62),"04":(.79,.78,.72),"05":(.19,.20,.18),"06":(.09,.10,.095)}
    drawset=[]
    for name,part in parts.items():
        if "coupon" in name: continue
        if which=="open" and name in ("02_ball_lid","12_ball_emblem"):
            part=part.rotate((0,HY,HZ),(1,HY,HZ),-110)
        if which=="portable" and name.startswith("03_removable_cradle"): continue
        if which=="portable" and name.startswith(("01_","02_","12_")): continue
        if which=="portable" and name=="05_handheld_back": continue
        if which=="inside" and name.startswith(("01_","02_","12_")): continue
        color=colors.get(name[:2],(.80,.79,.73))
        renderer.AddActor(actor(part,color))
    if which in ("open","inside"):
        renderer.AddActor(actor(box(30.6,40.8,.25,0,6.3,5.9),(.12,.23,.18)))
        if which=="inside":
            renderer.AddActor(actor(box(36,63,5.2,0,0,-19.5),(.57,.6,.56)))
    camera=renderer.GetActiveCamera();camera.ParallelProjectionOn();camera.SetViewUp(0,0,1)
    if which=="open": camera.SetFocalPoint(0,16,13);camera.SetPosition(174,-244,205);camera.SetParallelScale(130)
    elif which=="portable": camera.SetFocalPoint(0,2,-7);camera.SetPosition(142,-194,154);camera.SetParallelScale(72)
    else: camera.SetFocalPoint(0,3,-8);camera.SetPosition(154,-220,190);camera.SetParallelScale(81)
    renderer.ResetCameraClippingRange();window.Render()
    image=vtk.vtkWindowToImageFilter();image.SetInput(window);image.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/f"view_{which}.png"));writer.SetInputConnection(image.GetOutputPort());writer.Write();window.Finalize()


def main():
    OUT.mkdir(parents=True,exist_ok=True);parts=make_parts()
    for which in ("open","portable","inside"): view(parts,which)
    canvas=Image.new("RGB",(1800,790),(235,232,223));draw=ImageDraw.Draw(canvas)
    title=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",40);small=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",23)
    draw.text((38,24),"POCKET PET / HERAUSNEHMBARES HANDHELD V2",font=title,fill=(33,39,33))
    draw.text((40,78),"Handheld 62 x 90 x 33 mm   /   Ball 130 mm   /   CAD-Ansichten",font=small,fill=(52,59,51))
    labels=(("open","Im Ball / 110 Grad geoeffnet"),("portable","Eigenstaendig spielbares Handheld"),("inside","Aufnahme und Displayseite"))
    for i,(key,label) in enumerate(labels):
        canvas.paste(Image.open(OUT/f"view_{key}.png").convert("RGB").resize((600,600)),(i*600,130))
        draw.text((i*600+22,744),label,font=small,fill=(33,39,33))
    canvas.save(OUT/"preview.png")


if __name__=="__main__":main()
