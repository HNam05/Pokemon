"""Validate and package the single-sheet Revision C drawing.

Digital document checks only. The earlier bounded envelope check is included
as provenance, not presented as a fresh or complete hardware verification.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/pocket_pet_technical_rev_c'
PDF=OUT/'Pocket_Pet_V2_RevC_Isometrische_Gesamtzeichnung.pdf'
SVG=PDF.with_suffix('.svg')


def main():
    report=json.loads((OUT/'isometric_geometry.json').read_text(encoding='utf-8'))
    for name,digest in report['sources'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    assert hashlib.sha256((ROOT/'output/cad-research/ESP32-S3-LCD-2-20250122.stp').read_bytes()).hexdigest()==report['board_step_sha256']
    assert len(report['parts'])==15
    assert all(p['valid'] for p in report['parts'].values())
    assert report['parts']['05_handheld_back']['solids']==5
    old=json.loads((ROOT/'output/pdf/pocket_pet_technical/geometry_reference.json').read_text(encoding='utf-8'))
    for name,p in report['parts'].items():
        assert max(abs(a-b) for a,b in zip(p['bbox'],old['parts'][name]['bbox']))<1e-5,name
    for name,r in report['renders'].items():
        assert max(r['axis_10mm_pixels'])-min(r['axis_10mm_pixels'])<1e-5,name
        assert (OUT/r['path']).is_file()
    reader=PdfReader(PDF)
    assert len(reader.pages)==1
    page=reader.pages[0]
    assert abs(float(page.mediabox.width)-841/25.4*72)<.01
    assert abs(float(page.mediabox.height)-594/25.4*72)<.01
    text=page.extract_text()
    for prefix,n in [('P',15),('E',11),('M',12)]:
        for i in range(1,n+1):assert f'{prefix}{i:02d}' in text,(prefix,i)
    for required in ['KEINE FERTIGUNGSFREIGABE','Alle Werte in mm','ISO 5456-3','5 Körper','Lieferhöhe offen','13,71']:
        assert required in text,required
    assert len(page.get('/Annots',[]))==9
    tree=ET.parse(SVG)
    assert tree.getroot().get('width')=='841mm'
    assert tree.getroot().get('height')=='594mm'
    boxes=json.loads((OUT/'text_layout.json').read_text(encoding='utf-8'))
    for b in boxes:
        assert b[0]>=8 and b[2]<=833 and b[1]>=8 and b[3]<=587,b
    for i,b in enumerate(boxes):
        for c in boxes[i+1:]:
            assert not(min(b[2],c[2])-max(b[0],c[0])>.4 and min(b[3],c[3])-max(b[1],c[1])>.2),(b[4],c[4])
    bom=OUT/'Stueckliste_2_Geraete_RevC.csv'
    shutil.copyfile(ROOT/'output/pdf/pocket_pet_technical_rev_b/Stueckliste_2_Geraete_RevB.csv',bom)
    with bom.open(encoding='utf-8-sig',newline='') as fp:
        rows=list(csv.reader(fp,delimiter=';'))
    assert len(rows)==39
    fit_path=ROOT/'output/pdf/pocket_pet_technical_rev_b/integration_check.json'
    fit=json.loads(fit_path.read_text(encoding='utf-8'))
    assert fit['sources']==report['sources'] and fit['board_step_sha256']==report['board_step_sha256']
    assert fit['pairs_checked']==92 and not fit['intersections']
    shutil.copyfile(fit_path,OUT/'integration_check_rev_b_reference.json')
    assert (OUT/'full_resolution.png').is_file()
    result={'revision':'C','pages':1,'page_size_mm':[841,594],'parts':15,'bom_positions':38,
            'cad_isometric_renders':len(report['renders']),'equal_axis_projection_checked':True,
            'cad_part_bounds_match_original':True,'pdf_source_links':9,'text_collisions':0,
            'inspection':'One complete 150-dpi page and all four detail regions rendered; visual review performed separately.',
            'previous_envelope_check_reused':{'revision':'B','pairs':92,'intersections':0,'sources_unchanged':True},
            'physical_validation':False,'full_assembly_validation':False,'manufacturing_release':False,
            'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest()}
    validation=OUT/'document_validation.json'
    validation.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    files=[PDF,SVG,bom,validation,OUT/'QUELLEN.md',OUT/'README.md',OUT/'isometric_geometry.json',
           OUT/'integration_check_rev_b_reference.json']
    archive=OUT/'Pocket_Pet_V2_RevC_Isometrischer_Zeichnungsplan.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for path in files:z.write(path,path.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(files)
    print(json.dumps(result,ensure_ascii=False))
    print(archive)


if __name__=='__main__':main()
