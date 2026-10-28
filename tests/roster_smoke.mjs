import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'output','roster');await fs.mkdir(output,{recursive:true});
const fixture=await fs.mkdtemp(path.join(output,'fixture-'));
const port=8890,url=`http://127.0.0.1:${port}`;
const server=spawn(process.env.PYTHON||'python',['desktop/server.py','--manual-clock','--port',String(port),'--save',path.join(fixture,'pet.json')],{cwd:root,windowsHide:true});
let logs='';server.stderr.on('data',s=>logs+=s);
const browser=await chromium.launch({headless:true});
try {
  let ready=false;
  for(let i=0;i<100;i++) {
    if(server.exitCode!==null)throw new Error(logs);
    try{ready=(await fetch(`${url}/api/state`)).ok;}catch{}
    if(ready)break;await new Promise(r=>setTimeout(r,50));
  }
  assert(ready,'server started');
  const page=await browser.newPage({viewport:{width:1100,height:850}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const initial=await (await fetch(`${url}/api/info`)).json();
  assert.equal(initial.starters,130);
  await page.goto(url);await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
  const state=()=>page.evaluate(()=>JSON.parse(window.render_game_to_text()));
  // Raw key levels go through the C++ decoder in real time (30 ms debounce, 80 ms minimum press).
  const key=async name=>{await page.keyboard.press(name);await page.waitForTimeout(250);await page.evaluate(()=>window.advanceTime(0));};
  const snapshots=[];
  const seenStarters=new Set();
  for(let index=0;index<initial.starters;index++) {
    const s=await state();assert(!seenStarters.has(s.starter),'each starter shown once');seenStarters.add(s.starter);
    assert((await page.locator('#art-credit').textContent()).includes(s.credit));
    snapshots.push({label:`${index+1}. ${s.starter_name} ${s.starter_form}`,image:await page.locator('#screen').evaluate(canvas=>canvas.toDataURL())});
    await key('ArrowRight');
  }
  assert.equal((await state()).starter,1,'complete selection wraps');
  await page.keyboard.down('ArrowRight');await page.waitForTimeout(1450);await page.keyboard.up('ArrowRight');
  await page.evaluate(()=>window.advanceTime(0));
  const held=(await state()).starter;assert.notEqual(held,4,'holding side button browses multiple entries');
  await page.waitForTimeout(300);assert.equal((await state()).starter,held,'release stops repeat');
  await page.waitForTimeout(200);await key('Enter');await page.locator('#skip').click();await page.evaluate(()=>window.advanceTime(0));
  assert.equal((await state()).species,held,'selected imported pet hatches');
  const frames=new Set();
  for(let i=0;i<80;i++){await page.evaluate(()=>window.advanceTime(100));frames.add(JSON.stringify((await state()).animation));}
  assert(frames.size>5,'new companion animates');
  await page.locator('#save').click();await page.evaluate(()=>window.advanceTime(0));
  await page.reload();await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
  assert.equal((await state()).species,held,'reload preserves chosen species');
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'mobile-new-pet.png'),fullPage:true});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no mobile overflow');
  assert.equal((await fetch(`${url}/api/assets/255`)).status,404);
  assert.equal((await fetch(`${url}/api/frame?reduced=2`)).status,404);
  assert.equal((await fetch(`${url}/api/frame`)).headers.get('content-length'),String(240*320*2));
  assert.equal((await fetch(`${url}/credits`)).status,200);
  assert.deepEqual(errors,[]);
  const gallery=await browser.newPage({viewport:{width:1440,height:1050}});
  for(let start=0;start<snapshots.length;start+=24) {
    await gallery.setContent('<html><body style="margin:0;background:#ebe7d9;font:12px sans-serif"><main style="display:grid;grid-template-columns:repeat(8,180px)"></main></body></html>');
    await gallery.locator('main').evaluate((element,items)=>{
      for(const item of items){const figure=document.createElement('figure');figure.style.margin='5px';const label=document.createElement('div');label.textContent=item.label;label.style.height='32px';const image=document.createElement('img');image.src=item.image;image.style.cssText='width:170px;height:227px;image-rendering:pixelated';figure.append(label,image);element.append(figure);}
    },snapshots.slice(start,start+24));
    await gallery.screenshot({path:path.join(output,`contact-${start/24}.png`),fullPage:true});
  }
  await fs.writeFile(path.join(output,'report.json'),JSON.stringify({starters:initial.starters,errors,chosen:held},null,2));
  console.log('PASS: all 130 starters, credits, device frames, held navigation, hatch, animation, save/reload, mobile and HTTP bounds');
}finally{await browser.close();server.kill();}
