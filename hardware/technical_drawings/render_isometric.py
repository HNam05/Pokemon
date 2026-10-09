"""Read-only true isometric CAD renders for the one-sheet Revision C plan.

Actual enclosure CAD and original vendor STEP are kept unchanged. Other
electronics use explicitly labelled dimension envelopes, not invented CAD.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import itertools
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import cadquery as cq
import vtk
from hardware.pokeball_v2.build import make_parts,HY,HZ
from hardware.pokeball_v1.build import box,cyl

OUT=ROOT/'output/pdf/pocket_pet_technical_rev_c'
IMAGES=OUT/'images'
IMAGES.mkdir(parents=True,exist_ok=True)
WHITE=(1,1,1)
COLORS={'case':(.81,.83,.80),'lid':(.73,.16,.12),'frame':(.34,.47,.54),
        'board':(.27,.53,.36),'screen':(.035,.19,.21),'battery':(.83,.64,.28),
        'button':(.78,.28,.20),'audio':(.49,.39,.58),'connector':(.22,.52,.65)}
N=(1/math.sqrt(3),-1/math.sqrt(3),1/math.sqrt(3))
U=(1/math.sqrt(2),1/math.sqrt(2),0)
V=(-1/math.sqrt(6),1/math.sqrt(6),2/math.sqrt(6))


def dot(a,b):return sum(x*y for x,y in zip(a,b))


def bounds(shape):
    b=shape.val().BoundingBox()
    return [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]


def mesh(shape):
    vertices,faces=shape.val().tessellate(.10,.12)
    points=vtk.vtkPoints()
    for p in vertices:points.InsertNextPoint(p.x,p.y,p.z)
    cells=vtk.vtkCellArray()
    for face in faces:cells.InsertNextCell(3,face)
    poly=vtk.vtkPolyData()
    poly.SetPoints(points);poly.SetPolys(cells)
    return poly


def add_actor(ren,poly,color,translation=(0,0,0)):
    normals=vtk.vtkPolyDataNormals()
    normals.SetInputData(poly);normals.SetFeatureAngle(40)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper);actor.SetPosition(*translation)
    prop=actor.GetProperty();prop.SetColor(*color);prop.SetAmbient(.42);prop.SetDiffuse(.58)
    prop.SetSpecular(0)
    ren.AddActor(actor)
    edges=vtk.vtkFeatureEdges();edges.SetInputData(poly)
    edges.FeatureEdgesOn();edges.BoundaryEdgesOn();edges.ManifoldEdgesOff();edges.NonManifoldEdgesOff()
    edges.SetFeatureAngle(35);edges.ColoringOff()
    em=vtk.vtkPolyDataMapper();em.SetInputConnection(edges.GetOutputPort())
    ea=vtk.vtkActor();ea.SetMapper(em);ea.SetPosition(*translation)
    ea.GetProperty().SetColor(.20,.24,.25);ea.GetProperty().SetLineWidth(1.0)
    ren.AddActor(ea)


def render(name,objects,width,height,anchors=None,dimensions=None,margin=1.12):
    """objects: (poly, bounds, colour, translation); return normalized labels."""
    anchors=anchors or {};dimensions=dimensions or []
    pts=[]
    for poly,b,_,t in objects:
        pts += [tuple(poly.GetPoint(j)[i]+t[i] for i in range(3)) for j in range(poly.GetNumberOfPoints())]
    pts += list(anchors.values())
    for dim in dimensions:
        pts.extend(dim['line']);pts.extend(dim['ends'])
    uv=[(dot(p,U),dot(p,V)) for p in pts]
    u0,u1=min(p[0] for p in uv),max(p[0] for p in uv)
    v0,v1=min(p[1] for p in uv),max(p[1] for p in uv)
    cn=dot(tuple(sum(p[i] for p in pts)/len(pts) for i in range(3)),N)
    center=tuple(U[i]*(u0+u1)/2+V[i]*(v0+v1)/2+N[i]*cn for i in range(3))
    parallel=max((v1-v0)/2,(u1-u0)/(2*width/height))*margin
    ren=vtk.vtkRenderer();ren.SetBackground(*WHITE)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(width,height)
    window.SetMultiSamples(8);window.AddRenderer(ren)
    for poly,b,color,t in objects:add_actor(ren,poly,color,t)
    camera=ren.GetActiveCamera();camera.SetFocalPoint(*center)
    camera.SetPosition(*(center[i]+N[i]*1000 for i in range(3)))
    camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(parallel)
    ren.ResetCameraClippingRange();window.Render()
    def project(p):
        ren.SetWorldPoint(*p,1);ren.WorldToDisplay();px,py,_=ren.GetDisplayPoint()
        return [px/width,1-py/height]
    axes=[]
    c0=project(center)
    for i in range(3):
        p=list(center);p[i]+=10;p=project(p)
        axes.append(math.hypot((p[0]-c0[0])*width,(p[1]-c0[1])*height))
    assert max(axes)-min(axes)<1e-5,(name,axes)
    projected={key:project(p) for key,p in anchors.items()}
    dd=[{**dim,'line':[project(p) for p in dim['line']],
         'ends':[project(p) for p in dim['ends']]} for dim in dimensions]
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(IMAGES/f'{name}.png'))
    writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
    print(name,flush=True)
    return {'path':f'images/{name}.png','pixels':[width,height],
            'anchors':projected,'dimensions':dd,'axis_10mm_pixels':axes,
            'projection':'orthographic_isometric','world_per_pixel_mm':2*parallel/height}


def main():
    fit=json.loads((ROOT/'output/pdf/pocket_pet_technical_rev_b/integration_check.json').read_text())
    for path,digest in fit['sources'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    parts=make_parts()
    step=ROOT/'output/cad-research/ESP32-S3-LCD-2-20250122.stp'
    assert hashlib.sha256(step.read_bytes()).hexdigest()==fit['board_step_sha256']
    board=cq.importers.importStep(str(step)).rotate((0,0,0),(0,0,1),180).translate((0,6.3,.1))
    fr4=box(43,12,1.6,0,-28,-6.4)
    for x in (-16,0,16):
        for dx in (-3.25,3.25):
            for dy in (-2.25,2.25):fr4=fr4.cut(cyl(.5,3,x+dx,-28+dy,-7))
    electronics={'E01':board,'E03':fr4,'E04':box(36,63,5.2,0,0,-19.5),
                 'E08':box(30,20,5,9.5,-26,-13.8),'E09':box(17.8,19.4,3,-17.2,-26,-13.3)}
    # Taster body is a conservative nominal envelope, not the manufacturer's CAD.
    for x in (-16,0,16):electronics[f'E02_{x}']=box(6,6,4.3,x,-28,-4.8)
    electronics['screen']=box(30.6,40.8,.04,0,6.2,2.20)
    shapes={**parts,**electronics}
    # Capture analytic OCCT bounds before triangulation adds mesh tolerances.
    analytic_bounds={name:bounds(shape) for name,shape in shapes.items()}
    polys={name:mesh(shape) for name,shape in shapes.items()}
    colors={name:COLORS['case'] for name in parts}
    colors.update({'02_ball_lid':COLORS['lid'],'03_removable_cradle':COLORS['frame'],
                   '06_board_carrier':COLORS['frame'],'10_switch_tray':COLORS['frame'],
                   '11_battery_tray':COLORS['frame'],'12_ball_emblem':COLORS['button']})
    for name in parts:
        if name.startswith(('07','08','09')):colors[name]=COLORS['button']
    colors.update({name:COLORS['board'] for name in electronics})
    colors.update({'screen':COLORS['screen'],'E04':COLORS['battery'],'E08':COLORS['audio'],'E09':COLORS['audio']})
    for name in electronics:
        if name.startswith('E02'):colors[name]=COLORS['button']
    def obj(name,t=(0,0,0)):return (polys[name],bounds(shapes[name]),colors[name],t)
    report={'revision':'C','sources':fit['sources'],'board_step_sha256':fit['board_step_sha256'],
            'camera_direction':[1,-1,1],'renders':{},'parts':{},
            'model_classes':{'enclosure':'actual_existing_CAD','E01':'original_vendor_STEP',
                            'E03':'planned_FR4_with_drill_pattern','E02/E04/E08/E09':'dimension_envelopes'},
            'physical_validation':False}
    for name,shape in parts.items():
        b=analytic_bounds[name]
        report['parts'][name]={'bbox':b,'size':[b[1]-b[0],b[3]-b[2],b[5]-b[4]],
                                'valid':shape.val().isValid(),'solids':len(shape.solids().vals())}
        item=shape
        # Isolate the inside of the front; expose the battery tray without hiding it.
        if name=='04_handheld_front':
            item=shape.rotate((0,0,0),(1,0,0),180)
        p=mesh(item) if item is not shape else polys[name]
        report['renders'][name]=render(name,[(p,bounds(item),colors[name],(0,0,0))],1000,600,margin=1.16)
    cap_objects=[obj(name) for name in ('07_button_left','08_button_ok','09_button_right')]
    report['renders']['caps']=render('caps',cap_objects,1000,420)
    handheld_names=[n for n in parts if 4<=int(n[:2])<=11]
    assembled=[obj(n) for n in handheld_names]+[obj('E01'),obj('screen')]
    dims=[{'text':'62,0','ends':[(-31,-43,-26.4),(31,-43,-26.4)],'line':[(-31,-54,-34),(31,-54,-34)]},
          {'text':'90,0','ends':[(31,-43,-26.4),(31,47,-26.4)],'line':[(44,-43,-34),(44,47,-34)]},
          {'text':'31,4','ends':[(31,-43,-26.4),(31,-43,5)],'line':[(47,-54,-26.4),(47,-54,5)]}]
    report['renders']['handheld_closed']=render('handheld_closed',assembled,1600,1300,
                                               {'buttons':(16,-28,6.8),'screen':(0,6.2,2.24)},dims)
    opened=[]
    for name in ('01_ball_lower','02_ball_lid','03_removable_cradle','12_ball_emblem'):
        shape=parts[name]
        if name in ('02_ball_lid','12_ball_emblem'):shape=shape.rotate((0,HY,HZ),(1,HY,HZ),-110)
        opened.append((mesh(shape),bounds(shape),colors[name],(0,0,0)))
    theta=math.radians(-110)
    lid_y,lid_z=0,math.sqrt(65**2-40**2)+.6
    lid_anchor=(40,HY+(lid_y-HY)*math.cos(theta)-(lid_z-HZ)*math.sin(theta),
                HZ+(lid_y-HY)*math.sin(theta)+(lid_z-HZ)*math.cos(theta))
    ballanchors={'P01':(math.sqrt(65**2-30**2-26**2),-30,-26),'P02':lid_anchor,
                 'P03':(-33.2,-20,-16),'handheld':(0,-28,5)}
    report['renders']['ball_open']=render('ball_open',opened+assembled,1900,1600,ballanchors)
    offsets={'caps':300,'P04':220,'E01':130,'P06':70,'P10':25,'E08':-20,'P11':-80,'P05':-170}
    groups={'caps':('07_button_left','08_button_ok','09_button_right'),
            'P04':('04_handheld_front',),'E01':('E01','screen'),'P06':('06_board_carrier',),
            'P10':('10_switch_tray','E03','E02_-16','E02_0','E02_16'),
            'E08':('E08','E09'),'P11':('11_battery_tray','E04'),'P05':('05_handheld_back',)}
    exploded=[obj(n,(0,0,offsets[group])) for group,names in groups.items() for n in names]
    points={'caps':(16,-28,6.8+offsets['caps']),'P04':(31,-10,2.6+offsets['P04']),
            'E01':(17.5,-5,2.2+offsets['E01']),'P06':(26.5,0,-6.1+offsets['P06']),
            'P10':(28,-28,-6.4+offsets['P10']),'E08':(24.5,-26,-8.8+offsets['E08']),
            'P11':(27.5,0,-19.5+offsets['P11']),'P05':(31,-5,-24+offsets['P05'])}
    report['renders']['exploded']=render('exploded',exploded,1500,2800,points)
    report['explosion_offsets_mm']=offsets
    # Render electronics separately where no enclosure conceals them.
    for name in ('E01','E03','E04','E08','E09'):
        objs=[obj(name)]
        if name=='E01':objs.append(obj('screen'))
        report['renders'][name]=render(name,objs,900,550)
    (OUT/'isometric_geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Isometric metadata complete',flush=True)


if __name__=='__main__':main()
