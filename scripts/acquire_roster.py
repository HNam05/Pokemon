"""Audit the pinned SpriteCollab catalog and acquire qualified fan sets.

Online asset-maintenance tool, never part of the game or normal build.
Run after reviewing the source license. Existing IDs are preserved.
"""
import concurrent.futures
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
REV='83681005aa8f37cea7dfe8e68c51aa4b7bf8384a'
BASE=f'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/{REV}/'
CACHE=ROOT/'output/sprite-catalog/cache'
MOTIONS=['Idle','Walk','Hop','Pose','Sleep','Eat','Sit','Hurt','LookUp']
NAMES_SOURCE='https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_names.csv'


def fetch(path):
    target=CACHE/path
    if not target.exists():
        data=urllib.request.urlopen(BASE+path,timeout=45).read()
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    return target.read_bytes()


def main():
    tracker=fetch('tracker.json')
    candidates=[]
    excluded=[]
    def visit(tree,path=(),names=()):
        for key,n in tree.items():
            parts=path+(key,); labels=names+(n['name'],)
            credit=n['sprite_credit']; authors=[credit['primary']]+credit['secondary']
            reason=None
            if n['sprite_complete']:
                if parts[0]=='0000': reason='not a Pokemon species'
                elif 'CHUNSOFT' in authors: reason='official or mixed official art'
                elif any(any(word in name.lower() for word in ['shiny','altcolor','female']) for name in labels): reason='color/gender variant, not a separate animation set'
                elif n['sprite_complete']!=2: reason='upstream not fully featured'
                elif len(n['sprite_files'])<25: reason='fewer than 25 upstream actions'
                if reason: excluded.append({'path':'/'.join(parts),'reason':reason})
                else: candidates.append({'path':'/'.join(parts),'source_name':' '.join(x for x in labels if x),'credits':authors})
            visit(n['subgroups'],parts,labels)
    visit(json.loads(tracker))

    def inspect(entry):
        path='sprite/'+entry['path']+'/'
        xml=fetch(path+'AnimData.xml'); credits=fetch(path+'credits.txt').decode()
        if 'CHUNSOFT' in credits.upper(): return entry,'official credit in source history'
        rows=[line.split('\t') for line in credits.splitlines() if line]
        if any(len(row)<5 or row[3] not in ('PMDCollab_1','PMDCollab_2','CC_BY-NC_4') for row in rows): return entry,'unverified source credit terms'
        anims={a.findtext('Name'):a for a in ET.fromstring(xml).findall('./Anims/Anim')}
        resolved=[]
        for motion in MOTIONS:
            name=motion; visited=set()
            while name in anims and anims[name].findtext('CopyOf'):
                if name in visited: return entry,'cyclic CopyOf'
                visited.add(name);name=anims[name].findtext('CopyOf')
            if name not in anims: return entry,'missing care action '+motion
            frames=anims[name].findall('./Durations/Duration')
            if not frames or any(int(d.text)<=0 for d in frames): return entry,'invalid frame timing'
            resolved.append({'motion':motion,'source':name,'frames':len(frames)})
        counts={a['motion']:a['frames'] for a in resolved}
        if counts['Walk']<4 or counts['Sleep']<2 or counts['Hop']<4 or sum(counts.values())<35:
            return entry,'insufficient care-animation frames'
        entry['actions']=resolved;entry['frames']=sum(counts.values())
        entry['credits']=sorted({r[1] for r in rows})
        entry['licenses']=sorted({r[3] for r in rows})
        return entry,None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        audited=list(pool.map(inspect,candidates))
    accepted=[]
    for entry,reason in audited:
        if reason:excluded.append({'path':entry['path'],'reason':reason})
        else:accepted.append(entry)
    print(f'Audited {len(candidates)} complete fan sets: {len(accepted)} pass frame/credit criteria',flush=True)
    # Naming data only, no PokeAPI sprite artwork is imported.
    names_path=CACHE/'pokemon_species_names.csv'
    if not names_path.exists():
        names_path.write_bytes(urllib.request.urlopen(NAMES_SOURCE,timeout=45).read())
    names={int(r['pokemon_species_id']):r['name'] for r in csv.DictReader(io.StringIO(names_path.read_text(encoding='utf-8'))) if r['local_language_id']=='6'}
    roster_path=ROOT/'assets/roster.json'
    prior=json.loads(roster_path.read_text())['entries'] if roster_path.exists() else []
    ids={e['path']:e['id'] for e in prior}; ids['0133/0002']=1
    next_id=max([4,*ids.values()])+1
    for entry in accepted:
        if entry['path'] not in ids: ids[entry['path']]=next_id;next_id+=1
        entry['id']=ids[entry['path']]
        dex=int(entry['path'].split('/')[0]); entry['dex']=dex
        entry['name']=names[dex]
        entry['form']=' '.join(entry['source_name'].split()[1:]).replace('_',' ')
        entry['directory']='eevee-alternate' if entry['id']==1 else entry['path'].replace('/','-')
    if next_id>256: raise ValueError('Roster exceeds 8-bit species IDs; explicitly migrate format first')
    tasks=[]
    for entry in accepted:
        for name in ['AnimData.xml','credits.txt']+sorted({a['source']+'-Anim.png' for a in entry['actions']}): tasks.append((entry,name))
    def acquire(item):
        entry,name=item;data=fetch('sprite/'+entry['path']+'/'+name)
        target=ROOT/'assets/vendor/spritecollab'/entry['directory']/name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        return entry['path'],name,hashlib.sha256(data).hexdigest()
    hashes={e['path']:{} for e in accepted}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for path,name,digest in pool.map(acquire,tasks):hashes[path][name]=digest
    for entry in accepted: entry['files']=hashes[entry['path']]
    roster_path.write_text(json.dumps({'revision':REV,'tracker_sha256':hashlib.sha256(tracker).hexdigest(),
        'names_source':NAMES_SOURCE,'names_sha256':hashlib.sha256(names_path.read_bytes()).hexdigest(),
        'entries':accepted,'excluded':excluded},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Acquired {len(tasks)} files, {len(accepted)} sets, {len({e["dex"] for e in accepted})} Pokemon; {sum(e["frames"] for e in accepted)} care frames',flush=True)


if __name__=='__main__':main()
