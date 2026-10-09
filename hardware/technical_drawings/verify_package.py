"""Validate the Revision B document artifacts and assemble its delivery ZIP."""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/pocket_pet_technical_rev_b'
PDF=OUT/'Pocket_Pet_V2_RevB_Einbau_und_Montage.pdf'
reader=PdfReader(PDF)
assert len(reader.pages)==14
for i,page in enumerate(reader.pages,1):
    assert abs(float(page.mediabox.width)-420/25.4*72)<.01
    assert abs(float(page.mediabox.height)-297/25.4*72)<.01
    text=page.extract_text()
    assert f'Blatt {i} / 14' in text
    assert 'REV B' in text
    assert 'KEINE FERTIGUNGSFREIGABE' in text
    assert (OUT/f'blatt-{i:02d}.png').is_file()
    tree=ET.parse(OUT/f'PP-V2-Z{i:02d}.svg')
    assert tree.getroot().get('width')=='420mm'
    assert tree.getroot().get('height')=='297mm'
assert len(reader.pages[7].get('/Annots',[]))==6
with (OUT/'Stueckliste_2_Geraete_RevB.csv').open(encoding='utf-8-sig',newline='') as fp:
    rows=list(csv.reader(fp,delimiter=';'))
assert len(rows)==1+15+12+11 and all(len(row)==6 for row in rows)
fit=json.loads((OUT/'integration_check.json').read_text(encoding='utf-8'))
assert fit['pairs_checked']==92 and not fit['intersections']
for name,digest in fit['sources'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
assert hashlib.sha256((ROOT/'output/cad-research/ESP32-S3-LCD-2-20250122.stp').read_bytes()).hexdigest()==fit['board_step_sha256']
status=json.loads((OUT/'drawing_status.json').read_text(encoding='utf-8'))
assert status['pdf_sha256']==hashlib.sha256(PDF.read_bytes()).hexdigest()
shutil.copyfile(ROOT/'hardware/technical_drawings/README.md',OUT/'README.md')
report={'pages':14,'page_size_mm':[420,297],'svg_sheets':14,'bom_rows':38,
        'manufacturer_links_pdf':6,'rendered_pages':14,'electronic_pairs_checked':92,
        'electronic_envelope_intersections':0,'physical_validation':False,
        'pdf_sha256':status['pdf_sha256']}
(OUT/'document_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
archive=OUT/'Pocket_Pet_V2_RevB_Zeichnungssatz.zip'
files=[PDF,*sorted(OUT.glob('PP-V2-Z*.svg')),OUT/'Stueckliste_2_Geraete_RevB.csv',
       OUT/'README.md',OUT/'QUELLEN.md',OUT/'integration_check.json',OUT/'drawing_status.json',OUT/'document_validation.json']
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in files:z.write(file,file.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==len(files)
print(json.dumps(report))
print(archive)
