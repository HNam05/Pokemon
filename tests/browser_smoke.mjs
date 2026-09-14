import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'output', 'browser');
await fs.mkdir(output, { recursive: true });
const fixture = await fs.mkdtemp(path.join(output, 'fixture-'));
const port = Number(process.env.PET_TEST_PORT || 8877);
const url = `http://127.0.0.1:${port}`;
const processHandle = spawn(process.env.PYTHON || 'python', ['desktop/server.py', '--manual-clock',
  '--port', String(port), '--save', path.join(fixture, 'pet.json')], { cwd: root, windowsHide: true });
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
  async function key(name) {
    await page.keyboard.press(name);
    await page.evaluate(() => window.advanceTime(0));
  }
  async function menu(index) {
    const current = await state();
    if (current.screen === 2 || current.screen === 4) await key('Enter');
    if ((await state()).screen === 0) await key('Enter');
    for (let attempt=0; (await state()).selection !== index && attempt < 8; attempt++) await key('ArrowRight');
    assert.equal((await state()).selection, index);
    await key('Enter');
  }
  await page.screenshot({ path: path.join(output, '01-egg-desktop.png'), fullPage: true });
  await page.locator('#skip').click();
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).species === 1);
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
  await menu(0);
  assert.equal((await state()).fullness, 100);
  await key('Enter');
  await page.screenshot({ path: path.join(output, '03-menu.png'), fullPage: true });
  await key('ArrowLeft');
  assert.equal((await state()).selection, 7, 'menu wraps left');
  await key('Enter'); await waitFor(0);
  await key('ArrowRight'); await waitFor(2);
  await page.screenshot({ path: path.join(output, '04-stats.png'), fullPage: true });
  await key('Enter');
  await menu(2);
  assert.equal((await state()).sleeping, true);
  await menu(0);
  assert.equal((await state()).fullness, 100, 'sleeping blocks feed');
  await menu(2);
  assert.equal((await state()).sleeping, false);
  await menu(4); await waitFor(3);
  for (let round=0; round<5; round++) {
    let s = await state();
    while (s.mini.lane !== s.mini.target) {
      await key(s.mini.lane < s.mini.target ? 'ArrowRight' : 'ArrowLeft');
      s = await state();
    }
    await page.evaluate(() => window.advanceTime(1000));
    if (round === 0) await page.screenshot({ path: path.join(output, '05-catch.png'), fullPage: true });
    await key('Enter');
  }
  await waitFor(4);
  assert.equal((await state()).mini.score, 5);
  assert.equal((await state()).experience, 15);
  assert.equal((await state()).friendship, 30);
  await page.screenshot({ path: path.join(output, '06-result.png'), fullPage: true });
  await key('Enter');
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
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).species === 1);
  assert.equal((await state()).experience, 15);
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(output,'07-mobile.png'),fullPage:true});
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'no mobile overflow');
  await page.locator('#confirm').click();
  await waitFor(1);
  // Keyboard navigation continues after clicking a device button.
  await key('ArrowRight');
  assert.equal((await state()).selection, 5);
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
