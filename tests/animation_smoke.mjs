import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'output','animations');
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true});
try {
  for (const species of [1,4]) {
    const fixture=await fs.mkdtemp(path.join(output,'fixture-'));
    const port=8878, url=`http://127.0.0.1:${port}`;
    const server=spawn(process.env.PYTHON||'python',['desktop/server.py','--manual-clock','--port',String(port),'--save',path.join(fixture,'pet.json')],{cwd:root,windowsHide:true});
    let logs=''; server.stderr.on('data',s=>logs+=s);
    const context=await browser.newContext({viewport:{width:1000,height:880}});
    try {
      let ready=false;
      for(let i=0;i<100;i++) {
        if(server.exitCode!==null) throw new Error(logs);
        try {ready=(await fetch(`${url}/api/state`)).ok;} catch {}
        if(ready) break;
        await new Promise(r=>setTimeout(r,50));
      }
      assert(ready,'animation test server started');
      const page=await context.newPage(); const errors=[];
      page.on('pageerror',e=>errors.push(e.message));
      await page.goto(url); await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
      const post=(endpoint,data)=>page.evaluate(async({endpoint,data})=>{
        const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
        if(!response.ok) throw new Error(await response.text()); return response.json();
      },{endpoint,data});
      if(species===4) await post('/api/button',{button:2});
      await post('/api/button',{button:1}); await post('/api/skip',{minutes:10});
      await page.evaluate(()=>window.advanceTime(0));
      const atlas=await (await fetch(`${url}/api/assets`)).json();
      const seen=new Set(), frames=new Set(), screenshots={};
      for(let i=0;i<700;i++) {
        await page.evaluate(()=>window.advanceTime(100));
        const state=await page.evaluate(()=>JSON.parse(window.render_game_to_text()));
        const a=state.animation; seen.add(a.name); frames.add(`${a.name}:${a.frame}`);
        const sprite=atlas.animations[species][a.clip][a.frame];
        assert(a.draw_y>=42,'sprite stays below header');
        assert(a.draw_y+sprite.height*a.scale<=210,'sprite stays above needs');
        assert(a.draw_x>=8 && a.draw_x+sprite.width*a.scale<=232,'sprite stays inside side edges');
        if(!screenshots[a.name]) {
          screenshots[a.name]=true;
          await page.locator('#screen').screenshot({path:path.join(output,`${species}-${a.name}.png`)});
        }
        if(a.name==='hop' && a.frame===5 && !screenshots.peak) {
          screenshots.peak=true;
          await page.locator('#screen').screenshot({path:path.join(output,`${species}-hop-peak.png`)});
        }
      }
      assert(['idle','walk','hop','happy','look'].every(name=>seen.has(name)),'all spontaneous motions visible');
      assert(frames.size>8,'several visible frame transitions');
      await post('/api/button',{button:1}); await post('/api/button',{button:1});
      await page.evaluate(()=>window.advanceTime(0));
      assert.equal(JSON.parse(await page.evaluate(()=>window.render_game_to_text())).animation.name,'eat');
      await page.locator('#screen').screenshot({path:path.join(output,`${species}-eat.png`)});
      await post('/api/button',{button:1}); await post('/api/button',{button:2}); await post('/api/button',{button:2}); await post('/api/button',{button:1});
      await page.evaluate(()=>window.advanceTime(0));
      const sleeping=JSON.parse(await page.evaluate(()=>window.render_game_to_text()));
      assert(sleeping.sleeping); assert.equal(sleeping.animation.name,'sleep');
      await page.locator('#screen').screenshot({path:path.join(output,`${species}-sleep.png`)});
      await post('/api/speed',{speed:0}); await page.evaluate(()=>window.advanceTime(0));
      const before=await page.locator('#screen').screenshot();
      await page.evaluate(()=>window.advanceTime(1200));
      assert(before.equals(await page.locator('#screen').screenshot()),'pause freezes rendered canvas');
      await page.emulateMedia({reducedMotion:'reduce'}); await page.reload();
      await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
      await post('/api/speed',{speed:1}); await page.evaluate(()=>window.advanceTime(0));
      const reduced=await page.locator('#screen').screenshot();
      await page.evaluate(()=>window.advanceTime(1200));
      assert(reduced.equals(await page.locator('#screen').screenshot()),'reduced motion keeps static sleeping pose');
      assert.deepEqual(errors,[]);
      await fs.writeFile(path.join(output,`${species}-report.json`),JSON.stringify({seen:[...seen],frameTransitions:frames.size,errors},null,2));
      console.log(`PASS: species ${species}, motions ${[...seen]}, ${frames.size} frame combinations, feed/sleep/pause/reduced motion`);
    } finally { await context.close(); server.kill(); await new Promise(resolve=>server.exitCode!==null?resolve():server.once('exit',resolve)); }
  }
} finally { await browser.close(); }
