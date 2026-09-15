import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'output','reset');await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true});
try {
  for(const enabled of [false,true]) {
    const fixture=await fs.mkdtemp(path.join(output,'fixture-'));
    const save=path.join(fixture,'pet.json');
    const port=8891,url=`http://127.0.0.1:${port}`;
    const server=spawn(process.env.PYTHON||'python',['desktop/server.py','--manual-clock','--port',String(port),'--save',save,...(enabled?['--test-controls']:[])],{cwd:root,windowsHide:true});
    let logs='';server.stderr.on('data',s=>logs+=s);
    const page=await browser.newPage({viewport:{width:1100,height:900}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    try {
      let ready=false;
      for(let i=0;i<100;i++) {
        if(server.exitCode!==null)throw new Error(logs);
        try{ready=(await fetch(url+'/api/state')).ok;}catch{}
        if(ready)break;await new Promise(r=>setTimeout(r,50));
      }
      assert(ready);
      await page.goto(url);await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
      const state=()=>page.evaluate(()=>JSON.parse(window.render_game_to_text()));
      const post=(data)=>fetch(url+'/api/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
      if(!enabled) {
        assert(await page.locator('#test-controls').isHidden());
        assert.equal((await post({confirm:true})).status,404);
      } else {
        assert(await page.locator('#test-reset').isVisible());
        assert.equal((await post({confirm:1})).status,400);
        await page.keyboard.press('Enter');await page.evaluate(()=>window.advanceTime(0));
        await page.locator('#skip').click();await page.evaluate(()=>window.advanceTime(0));
        assert.equal((await state()).species,1);
        await page.locator('#save').click();await page.evaluate(()=>window.advanceTime(0));
        const before=await fs.readFile(save);
        await page.locator('#test-reset').click();
        await page.keyboard.press('ArrowRight');
        await page.locator('#reset-dialog').screenshot({path:path.join(output,'confirmation.png')});
        await page.getByRole('button',{name:'Abbrechen',exact:true}).click();
        assert.equal((await state()).species,1);
        assert(before.equals(await fs.readFile(save)));
        await page.locator('#test-reset').click();await page.locator('#reset-confirm').click();
        await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).screen===5);
        assert.equal((await state()).age_minutes,0);
        assert.equal((await state()).species,0);
        const backups=(await fs.readdir(fixture)).filter(n=>n.endsWith('.bak'));
        assert.equal(backups.length,1);assert(before.equals(await fs.readFile(path.join(fixture,backups[0]))));
        await page.reload();await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
        assert.equal((await state()).screen,5);
        await page.setViewportSize({width:390,height:844});
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        await page.screenshot({path:path.join(output,'reset-mobile.png'),fullPage:true});
        await page.keyboard.press('ArrowRight');await page.evaluate(()=>window.advanceTime(0));
        await page.keyboard.press('Enter');await page.evaluate(()=>window.advanceTime(0));
        await page.locator('#skip').click();await page.evaluate(()=>window.advanceTime(0));
        assert.equal((await state()).species,4,'new companion playable after reset');
      }
      assert.deepEqual(errors,[]);
    } finally {await page.close();server.kill();await new Promise(resolve=>server.once('exit',resolve));}
  }
  console.log('PASS: reset opt-in, disabled endpoint, confirmation/cancel, backup, fresh selection, reload, mobile and new pet');
} finally {await browser.close();}
