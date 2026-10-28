import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const starter = Number(process.env.PET_TEST_STARTER || 1);
const output = path.join(root, 'output', starter === 4 ? 'browser-enton' : 'browser');
await fs.mkdir(output, { recursive: true });
const fixture = await fs.mkdtemp(path.join(output, 'fixture-'));
const profile = path.join(fixture,'profile.json');
await fs.writeFile(profile,JSON.stringify({trainer_name:'Ada'}));
const port = Number(process.env.PET_TEST_PORT || 8877);
const url = `http://127.0.0.1:${port}`;
const processHandle = spawn(process.env.PYTHON || 'python', ['desktop/server.py', '--manual-clock',
  '--port', String(port), '--save', path.join(fixture, 'pet.json'), '--profile', profile], { cwd: root, windowsHide: true });
let logs = '';
processHandle.stderr.on('data', chunk => { logs += chunk; });
const browser = await chromium.launch({ headless: true });
try {
  let ready = false;
  for (let attempt = 0; attempt < 100; attempt++) {
    if (processHandle.exitCode !== null) throw new Error(`Server exited: ${logs}`);
    try { ready = (await fetch(`${url}/api/state`)).ok; } catch { /* Server startup. */ }
    if (ready) break;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  assert(ready, 'server started');
  const page = await browser.newPage({ viewport: { width: 1280, height: 920 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(url);
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).connected);
  const state = () => page.evaluate(() => JSON.parse(window.render_game_to_text()));
  async function waitFor(screen) { await page.waitForFunction(s => JSON.parse(window.render_game_to_text()).screen === s, screen); }
  // Raw levels pass the C++ decoder in real time: 30 ms debounce, 80 ms minimum press.
  async function key(name) {
    await page.keyboard.press(name);
    await page.waitForTimeout(250);
    await page.evaluate(() => window.advanceTime(0));
  }
  async function menu(index, start = true) {
    const current = await state();
    if (current.screen === 2 || current.screen === 4) await key('Enter');
    if ((await state()).screen === 0) await key('Enter');
    for (let attempt=0; (await state()).selection !== index && attempt < 14; attempt++) await key('ArrowDown');
    assert.equal((await state()).selection, index);
    await key('Enter');
    if (start && (await state()).screen === 8) {
      await key('Enter');
      await page.evaluate(() => window.advanceTime(900));
    }
  }
  async function checkNeeds() {
    const current = await state();
    for (const field of ['fullness', 'happiness', 'energy']) {
      assert.equal(await page.locator(`#need-${field}`).evaluate(el => el.value), current[field]);
      assert.equal(await page.locator(`#value-${field}`).textContent(), `${current[field]} / 100`);
    }
  }
  assert.equal((await state()).screen,5);
  if (starter === 4) await key('ArrowRight');
  await page.screenshot({path:path.join(output,'00-starter.png'),fullPage:true});
  assert.equal((await state()).starter,starter);
  assert.equal((await page.locator('#pet-name').textContent()),'Ada.');
  await key('Enter');
  await page.screenshot({ path: path.join(output, '01-egg-desktop.png'), fullPage: true });
  await page.locator('#skip').click();
  await page.waitForFunction(expected => JSON.parse(window.render_game_to_text()).species === expected,starter);
  await page.locator('#screen').focus();
  assert.equal((await state()).age_minutes, 10);
  await page.screenshot({ path: path.join(output, '02-evoli-desktop.png'), fullPage: true });
  await key('f');
  await page.waitForFunction(() => document.fullscreenElement !== null);
  assert(await page.locator('.button-legend').evaluate(element=>element.getBoundingClientRect().bottom <= innerHeight),'fullscreen controls visible');
  await page.screenshot({path:path.join(output,'08-fullscreen.png')});
  await page.keyboard.press('Escape');
  // Some headless browser builds do not map Escape to fullscreen exit.
  if (await page.evaluate(() => document.fullscreenElement !== null)) await key('f');
  await page.waitForFunction(() => document.fullscreenElement === null);
  const beforeFeed = await state();
  await menu(0);
  assert.equal((await state()).fullness, 100);
  await checkNeeds();
  assert.equal((await state()).feedback.fullness, 100-beforeFeed.fullness, 'feeding displays actual gain');
  await key('Enter');
  await page.screenshot({ path: path.join(output, '03-menu.png'), fullPage: true });
  await key('ArrowLeft');
  assert.equal((await state()).selection, 11, 'menu wraps left');
  assert.equal((await state()).menu_start,7,'menu scrolls to last entry');
  await page.screenshot({path:path.join(output,'09-menu-scrolled.png'),fullPage:true});
  await key('Enter'); await waitFor(0);
  await key('ArrowRight'); await waitFor(2);
  await page.screenshot({ path: path.join(output, '04-stats.png'), fullPage: true });
  await key('Enter');
  await menu(3);
  assert.equal((await state()).sleeping, true);
  await menu(0);
  assert.equal((await state()).fullness, 100, 'sleeping blocks feed');
  await menu(3);
  assert.equal((await state()).sleeping, false);
  const beforePlay = await state();
  await menu(5, false); await waitFor(8);
  assert.equal((await state()).energy, beforePlay.energy, 'instructions are free');
  await page.screenshot({path:path.join(output,'13-game-intro.png'),fullPage:true});
  await key('ArrowLeft'); await waitFor(1);
  assert.equal((await state()).energy, beforePlay.energy, 'cancel instructions is free');
  await key('Enter'); await waitFor(8);
  await key('Enter'); await waitFor(3);
  assert.equal((await state()).energy, beforePlay.energy - 8);
  assert.equal((await state()).fullness, beforePlay.fullness - 5);
  await checkNeeds();
  await key('Enter');
  assert.equal((await state()).mini.round, 0, 'ready phase ignores extra confirm');
  await page.evaluate(() => window.advanceTime(900));
  for (let round=0; round<5; round++) {
    let s = await state();
    while (s.mini.lane !== s.mini.target) {
      await key(s.mini.lane < s.mini.target ? 'ArrowRight' : 'ArrowLeft');
      s = await state();
    }
    await page.evaluate(() => window.advanceTime(1300));
    if (round === 0) await page.screenshot({ path: path.join(output, '05-catch.png'), fullPage: true });
    await key('Enter');
    await page.evaluate(() => window.advanceTime(450));
  }
  await waitFor(4);
  assert.equal((await state()).mini.score, 5);
  assert.equal((await state()).experience, 15);
  assert.equal((await state()).friendship, 30);
  await checkNeeds();
  assert.equal((await state()).feedback.happiness, 20, 'five catches earn 20 happiness');
  await page.screenshot({ path: path.join(output, '06-result.png'), fullPage: true });
  await key('Enter');
  await menu(6); await waitFor(7);
  await page.screenshot({path:path.join(output,'10-memory-playback.png'),fullPage:true});
  for (let round=0;round<3;round++) {
    await page.evaluate(()=>window.advanceTime(JSON.parse(window.render_game_to_text()).mini.duration_ms));
    const s = await state();
    assert.equal(s.mini.recalling,true);
    if (round===0) await page.screenshot({path:path.join(output,'11-memory-recall.png'),fullPage:true});
    assert.equal(s.mini.length, round+2);
    for (const symbol of s.mini.pattern.slice(0,s.mini.length)) await key(['ArrowLeft','Enter','ArrowRight'][symbol]);
    await page.evaluate(()=>window.advanceTime(900));
  }
  await waitFor(4);
  assert.equal((await state()).experience,24);
  assert.equal((await state()).friendship,36);
  assert.equal((await state()).feedback.happiness,7,'memory reward is capped at 100 happiness');
  await checkNeeds();
  await key('Enter');
  await menu(9); await waitFor(6);
  await page.screenshot({path:path.join(output,'12-care-guide.png'),fullPage:true});
  async function holdOK() {
    await page.keyboard.down('Enter');
    await page.waitForTimeout(800);
    await page.keyboard.up('Enter');
    await page.waitForTimeout(150);
    await page.evaluate(()=>window.advanceTime(0));
  }
  await holdOK(); await waitFor(1);
  assert.equal((await state()).selection,9,'long OK preserves parent menu selection');
  await holdOK(); await waitFor(0);
  await menu(6); await waitFor(7);
  const experience = (await state()).experience;
  await holdOK(); await waitFor(0);
  assert.equal((await state()).experience,experience,'cancel grants no reward');
  await page.locator('#speed').selectOption('0');
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).speed === 0);
  const age = (await state()).age_minutes;
  await page.evaluate(() => window.advanceTime(60000));
  assert.equal((await state()).age_minutes, age);
  await page.locator('#speed').selectOption('60');
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).speed === 60);
  await page.evaluate(() => window.advanceTime(1000));
  assert.equal((await state()).age_minutes, age+1);
  await page.locator('#save').click();
  await page.waitForFunction(() => document.querySelector('#save-status').textContent.startsWith('Gespeichert'));
  await page.reload();
  await page.waitForFunction(expected => JSON.parse(window.render_game_to_text()).species === expected,starter);
  assert.equal((await state()).experience, 24);
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(output,'07-mobile.png'),fullPage:true});
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'no mobile overflow');
  await page.locator('#confirm').click();
  await page.waitForTimeout(250); await page.evaluate(() => window.advanceTime(0));
  await waitFor(1);
  // Keyboard navigation continues after clicking a device button.
  await key('ArrowRight');
  assert.equal((await state()).selection, 7);
  const box = await page.locator('#confirm').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
  await page.mouse.down();
  await page.waitForTimeout(800);
  await page.mouse.up();
  await page.waitForTimeout(150);
  await page.evaluate(()=>window.advanceTime(0));
  assert.equal((await state()).screen,0,'pointer long OK does not also send a short OK');
  await page.locator('#about-link').click();
  assert.equal(await page.locator('#about').evaluate(dialog=>dialog.open),true);
  await page.getByRole('button',{name:'Schließen'}).click();
  assert.equal(await page.locator('#about').evaluate(dialog=>dialog.open),false);
  // HTTP boundaries and no cross-origin writes.
  const badButton = await fetch(`${url}/api/button`,{method:'POST',headers:{'Content-Type':'application/json'},body:'{"button":true}'});
  assert.equal(badButton.status,400);
  const foreign = await fetch(`${url}/api/button`,{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://example.com'},body:'{"button":1}'});
  assert.equal(foreign.status,403);
  const traversal = await fetch(`${url}/../README.md`);
  assert.equal(traversal.status,404);
  const beforeTabs = (await state()).age_minutes;
  const second = await browser.newPage(); await second.goto(url);
  await second.waitForFunction(() => JSON.parse(window.render_game_to_text()).connected);
  assert.equal((await state()).age_minutes,beforeTabs,'second tab does not tick manual clock');
  await second.close();
  assert.deepEqual(errors,[],'no browser errors');
  await fs.writeFile(path.join(output,'report.json'),JSON.stringify({status:'passed',errors,state:await state()},null,2));
  console.log('PASS: browser care, keyboard, minigame, save, clocks, mobile, HTTP boundaries');
} finally {
  await browser.close();
  processHandle.kill();
}
