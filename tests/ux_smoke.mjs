import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output=path.join(root,'output','ux');
await fs.mkdir(output,{recursive:true});
const fixture=await fs.mkdtemp(path.join(output,'fixture-'));
const url='http://127.0.0.1:8876';
const server=spawn(process.env.PYTHON||'python',['desktop/server.py','--manual-clock','--port','8876',
  '--save',path.join(fixture,'pet.json')],{cwd:root,windowsHide:true});
let logs='';server.stderr.on('data',chunk=>logs+=chunk);
const browser=await chromium.launch({headless:true});
try {
  let ready=false;
  for(let attempt=0;attempt<100;attempt++) {
    if(server.exitCode!==null)throw new Error(logs);
    try {ready=(await fetch(`${url}/api/state`)).ok;} catch { /* Startup. */ }
    if(ready)break;
    await new Promise(resolve=>setTimeout(resolve,50));
  }
  assert(ready);
  const page=await browser.newPage({viewport:{width:1280,height:920}});
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text());});
  await page.goto(url);
  await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).connected);
  const state=()=>page.evaluate(()=>JSON.parse(window.render_game_to_text()));
  const advance=ms=>page.evaluate(ms=>window.advanceTime(ms),ms);
  // Raw levels pass the C++ decoder in real time: 30 ms debounce, 80 ms minimum press.
  async function key(name) {await page.keyboard.press(name);await page.waitForTimeout(250);await advance(0);}
  // Count care ticks in (from, to]: the rules decay on age multiples.
  const ticks=(from,to,every)=>Math.floor(to/every)-Math.floor(from/every);
  // The device frame is RGB565; expand like the simulator does.
  const rgb565=([r,g,b])=>[Math.round((r>>3)*255/31),Math.round((g>>2)*255/63),Math.round((b>>3)*255/31),255];
  async function menu(index) {
    if((await state()).screen===0)await key('Enter');
    for(let i=0;(await state()).selection!==index && i<14;i++)await key('ArrowDown');
    assert.equal((await state()).selection,index);
    await key('Enter');
  }
  const shot=name=>page.screenshot({path:path.join(output,`${name}.png`),fullPage:true});
  await key('ArrowRight');await key('Enter');
  await page.locator('#skip').click();await advance(0);await page.locator('#screen').focus();
  assert.equal((await state()).species,4);
  assert.equal(await page.locator('#left span').textContent(),'\u25c0');
  assert.equal(await page.locator('#status-label').textContent(),'F\u00fchlt sich wohl');
  await menu(6);assert.equal((await state()).screen,8);
  await shot('01-memory-instructions');
  await key('Enter');await advance(900);
  const pattern=(await state()).mini.pattern;
  assert.equal((await state()).mini.cue,pattern[0]);
  await advance(650);
  assert.equal((await state()).mini.cue,-1,'visible separation between symbols');
  await key('Enter');assert.equal((await state()).mini.entered,0,'watch phase ignores presses');
  await advance(1150);
  for(const symbol of pattern.slice(0,2))await key(['ArrowLeft','Enter','ArrowRight'][symbol]);
  assert.equal((await state()).mini.phase,4);
  await shot('02-memory-correct');
  await advance(900);
  assert.deepEqual((await state()).mini.pattern,pattern,'same sequence grows');
  assert.equal((await state()).mini.length,3);
  await advance(2700);
  await key(['ArrowLeft','Enter','ArrowRight'][pattern[0]]);
  assert.equal((await state()).mini.last_button,pattern[0]);
  assert.equal((await state()).mini.entered,1);
  await shot('03-memory-input');
  await key(['ArrowLeft','Enter','ArrowRight'][(pattern[1]+1)%3]);
  await shot('04-memory-mistake');
  await advance(900);
  const partial=await state();
  assert.equal(partial.screen,4);
  assert.equal(partial.mini.score,1);
  assert.deepEqual([partial.feedback.happiness,partial.feedback.friendship,partial.feedback.experience],[4,2,3]);
  assert.equal(partial.energy,77);
  assert.equal(partial.fullness,70);
  assert.equal(await page.locator('#care-receipt').textContent(),'Froh +4  Bindung +2  EP +3');
  await shot('05-memory-partial-result');
  await key('Enter');
  await menu(6);await key('Enter');await advance(900+1800+9999);
  assert.equal((await state()).mini.phase,3);
  await advance(1);assert.equal((await state()).mini.phase,4);
  await advance(900);assert.equal((await state()).mini.score,0);
  assert.equal((await state()).experience,3,'timeout adds no reward');
  await key('Enter');
  const beforeSleep=await state();
  await menu(3);
  await page.locator('#speed').selectOption('60');await advance(60000);
  const asleep=await state();
  assert.equal(asleep.energy,beforeSleep.energy+30);
  assert.equal(asleep.fullness,beforeSleep.fullness-ticks(beforeSleep.age_minutes,asleep.age_minutes,20),'sleep slows hunger');
  assert.equal(asleep.happiness,beforeSleep.happiness);
  assert.equal(await page.locator('#need-energy').evaluate(el=>el.value),asleep.energy);
  await shot('06-sleep-recovery');
  await page.locator('#screen').focus();await menu(3);
  const awake=await state();
  for(let hour=0;hour<5;hour++)await advance(60000);
  const tired=await state();
  assert.equal(tired.energy,awake.energy-ticks(awake.age_minutes,tired.age_minutes,9));
  assert.equal(tired.fullness,awake.fullness-ticks(awake.age_minutes,tired.age_minutes,6));
  assert(tired.happiness<=awake.happiness-ticks(awake.age_minutes,tired.age_minutes,12),'boredom grows while awake');
  const pixels=await page.locator('#screen').evaluate(canvas=>{
    const context=canvas.getContext('2d');
    return [10,23].map(x=>Array.from(context.getImageData(x,238,1,1).data));
  });
  assert(tired.fullness<20,'fixture reaches a short low fill');
  assert.deepEqual(pixels,[rgb565([161,65,49]),rgb565([200,203,181])],'device frame shows low fullness and correct fill length');
  await shot('07-low-needs');
  // Low needs prevent spending resources on games and explain how to recover.
  await page.locator('#screen').focus();await key('Enter');
  while((await state()).selection!==5)await key('ArrowDown');
  assert.equal((await state()).menu[5].enabled,false);
  await shot('08-blocked-game');
  await key('Enter');assert.equal((await state()).energy,tired.energy);
  await page.setViewportSize({width:390,height:844});
  await shot('09-mobile-care');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(output,'report.json'),JSON.stringify({status:'passed',errors,state:await state()},null,2));
  console.log('PASS: growing memory cues, input, partial reward, timeout, sleep recovery, decay, blocked games, text and mobile');
} finally {await browser.close();server.kill();}
