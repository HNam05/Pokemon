'use strict';
// The browser is only a display and a set of buttons. Every device pixel comes from the
// shared C++ renderer; every button goes through the C++ decoder used by the firmware.
const canvas = document.querySelector('#screen');
const ctx = canvas.getContext('2d');
const image = ctx.createImageData(240, 320);
const $ = (selector) => document.querySelector(selector);
let info = null;
let state = null;
let pending = Promise.resolve();
let connected = false;
let pressed = 0;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const needFields = ['fullness','happiness','energy','hygiene','health','friendship'];
const needLabels = ['Satt','Froh','Energie','Sauber','Gesund','Bindung'];

function changeText() {
  const f = state.feedback;
  return [...needFields.map((field,i)=>[needLabels[i],f[field]]),['EP',f.experience]]
    .filter(([,value])=>value!==0).map(([label,value])=>`${label} ${value>0?'+':''}${value}`).join('  ');
}
function clockText(minutes) {
  return `${String(Math.floor(minutes / 60)).padStart(2,'0')}:${String(minutes % 60).padStart(2,'0')}`;
}
function paint(buffer) {
  const pixels = new Uint16Array(buffer);
  const data = image.data;
  for (let i = 0; i < pixels.length; i++) {
    const p = pixels[i], o = i * 4;
    data[o] = ((p >> 11) & 31) * 255 / 31; data[o+1] = ((p >> 5) & 63) * 255 / 63;
    data[o+2] = (p & 31) * 255 / 31; data[o+3] = 255;
  }
  ctx.putImageData(image, 0, 0);
}
function placeholder(message) {
  ctx.fillStyle = '#e8e5cf'; ctx.fillRect(0, 0, 240, 320);
  ctx.fillStyle = '#313a32'; ctx.font = 'bold 10px monospace'; ctx.textAlign = 'center';
  ctx.fillText(message, 120, 160);
}

function update(next) {
  state = next;
  $('#test-controls').hidden = !state.test_controls;
  $('#art-credit').textContent = state.credit ? `Grafik: ${state.credit}` : 'Pocket Pet Prototypgrafik';
  $('#pet-name').textContent = state.trainer_name ? `${state.trainer_name}.` : state.species === 0 ? 'kleines Ei.' : `${state.name}.`;
  const list = state.screen === 1;
  $('#left span').textContent = list ? '▲' : '◀';
  $('#right span').textContent = list ? '▼' : '▶';
  $('#left-label').textContent = list ? 'HOCH' : 'LINKS';
  $('#right-label').textContent = list ? 'RUNTER' : 'RECHTS';
  $('#left').setAttribute('aria-label',list?'Vorheriger Eintrag, hoch':'Links');
  $('#right').setAttribute('aria-label',list?'Nächster Eintrag, runter':'Rechts');
  $('#game-clock').textContent = clockText(state.minute_of_day);
  $('#status-label').textContent = state.screen === 5 ? 'Wähle deinen Begleiter' : state.speed === 0 ? 'Spiel pausiert' :
    state.species === 0 ? 'Wartet aufs Schlüpfen' : state.health === 0 ? 'Braucht Medizin' :
    state.calling ? 'Ruft dich!' : state.sleeping ? 'Schläft gerade' : state.attention ? 'Braucht deine Pflege' : 'Fühlt sich wohl';
  $('#message').textContent = state.screen === 1 ? state.menu[state.selection].hint : state.message;
  $('#care-hint').textContent = state.care_hint;
  needFields.slice(0,3).forEach((field,i)=>{
    const meter=$(`#need-${field}`);
    meter.value=state[field];meter.low=info.need_low[i];
    $(`#value-${field}`).textContent=`${state[field]} / 100`;
  });
  $('#care-receipt').textContent=state.feedback.remaining_ms>0?changeText():'';
  const days = Math.floor(Math.max(0, state.age_minutes - 10) / 1440) + 1;
  $('#age').textContent = state.species === 0 ? 'Ei' : `Tag ${days} · ${state.stage_name}`;
  $('#level').textContent = state.species === 0 ? '–' : `Lv ${state.level}`;
  $('#bond').textContent = `${state.friendship} / 100`; $('#xp').textContent = `${state.experience} EP`;
  $('#mistakes').textContent = String(state.care_mistakes);
  $('#evolution').textContent = state.evolves_to_name ? (state.can_evolve ? `Bereit: ${state.evolves_to_name}` : `Später: ${state.evolves_to_name}`) : 'Keine';
  $('#speed').value = String(state.speed);
  $('#skip').disabled = [3,5,7,8].includes(state.screen);
  $('#error').hidden = !state.storage_error;
  $('#error').textContent = state.storage_error || '';
  const gameHelp=[3,7,8,4].includes(state.screen)?` ${state.mini.memory?'Entons Denkpause':'Beerenfang'}. ${state.screen===8?'OK startet. Kosten: 5 Satt und 8 Energie.':state.screen===4?`Erhalten: ${changeText()||'keine Punkte'}.`:state.mini.phase===3?`Eingabe ${state.mini.entered} von ${state.mini.length}.`:state.mini.phase===2 && state.mini.cue>=0?`Merken: ${['Links','OK','Rechts'][state.mini.cue]}.`:state.message}`:'';
  const described = `${state.name}. ${state.calling ? 'Ruft nach dir. ' : ''}${state.message} Satt ${state.fullness}, froh ${state.happiness}, Energie ${state.energy}, Sauberkeit ${state.hygiene}, Gesundheit ${state.health}. ${state.screen === 1 ? `Menü: ${state.menu[state.selection].label}.` : state.screen===5 ? `Auswahl: ${state.starter_name} ${state.starter_form}.` : state.screen===9 ? `Uhr: ${clockText(state.clock_edit)}.` : ''}${gameHelp}`;
  $('#accessible-state').textContent = described;
  canvas.setAttribute('aria-label', described);
}
async function request(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Verbindung fehlgeschlagen.');
  connected = true; update(result); return result;
}
async function refreshFrame() {
  const response = await fetch(reducedMotion ? '/api/frame?reduced=1' : '/api/frame');
  if (!response.ok) throw new Error('Bildschirm konnte nicht geladen werden.');
  paint(await response.arrayBuffer());
}
function report(error) {
  connected = false; $('#error').hidden = false;
  $('#error').textContent = `${error.message} Läuft der lokale Server noch?`;
}
function enqueue(path, data) {
  const operation = pending.then(() => request(path, data)).then(async result => { await refreshFrame(); return result; });
  pending = operation.catch(report);
  return operation;
}
// Raw button levels: bit 0 left, bit 1 OK, bit 2 right. Timing lives in the C++ decoder.
// A finger cannot press or release faster than a key travels, but clicks and scripts can.
// Every level is therefore held at least 80 ms, in order, so the 30 ms debounce sees each
// tap exactly as a sampled hardware button would.
const levels = {};
function setButton(bit, down) {
  const level = levels[bit] ??= {down: false, at: -1e9, queue: [], timer: null};
  level.queue.push(down);
  replay(bit);
}
function replay(bit) {
  const level = levels[bit];
  if (level.timer) return;
  while (level.queue.length) {
    const down = level.queue[0];
    if (down === level.down) { level.queue.shift(); continue; }
    const wait = 80 - (performance.now() - level.at);
    if (wait > 0) { level.timer = setTimeout(() => { level.timer = null; replay(bit); }, wait); return; }
    level.queue.shift(); level.down = down; level.at = performance.now();
    applyButton(bit, down);
  }
}
function releaseAll() { for (const bit of [1,2,4]) setButton(bit, false); }
function applyButton(bit, down) {
  const next = down ? pressed | bit : pressed & ~bit;
  if (next === pressed) return;
  pressed = next;
  for (const [id,mask] of [['left',1],['confirm',2],['right',4]]) $(`#${id}`).classList.toggle('pressed', Boolean(pressed & mask));
  enqueue('/api/input',{pressed}).catch(()=>{});
}
for (const [id,bit] of [['left',1],['confirm',2],['right',4]]) {
  const element=$(`#${id}`);
  element.addEventListener('pointerdown',event=>{
    if(event.button!==0)return;element.setPointerCapture(event.pointerId);setButton(bit,true);
  });
  element.addEventListener('pointerup',()=>setButton(bit,false));
  element.addEventListener('pointercancel',()=>setButton(bit,false));
  element.addEventListener('lostpointercapture',()=>setButton(bit,false));
  // Keyboard activation of a focused button has no hold; send one decoded press.
  element.addEventListener('click',event=>{if(event.detail===0) enqueue('/api/button',{button:[1,2,4].indexOf(bit)}).catch(()=>{});});
}
window.addEventListener('blur',releaseAll);
$('#speed').addEventListener('change',event=>{enqueue('/api/speed',{speed:Number(event.target.value)}).catch(()=>{});});
$('#skip').addEventListener('click',()=>{enqueue('/api/skip',{minutes:10}).catch(()=>{});});
$('#save').addEventListener('click',()=>{enqueue('/api/save',{}).then(result=>{
  if (!result.storage_error) $('#save-status').textContent = `Gespeichert um ${new Date().toLocaleTimeString('de-DE')}.`;
}).catch(()=>{});});
$('#about-link').addEventListener('click',event=>{event.preventDefault();$('#about').showModal();});
$('#test-reset').addEventListener('click',()=>{
  releaseAll();
  $('#reset-dialog').showModal();
});
$('#reset-confirm').addEventListener('click',async()=>{
  const button=$('#reset-confirm');button.disabled=true;
  try {
    await enqueue('/api/reset',{confirm:true});
    $('#reset-dialog').close();
    $('#save-status').textContent='Testspielstand zurückgesetzt. Wähle deinen Begleiter.';
  } catch { $('#reset-dialog').close(); /* enqueue presents the error. */ }
  finally { button.disabled=false; }
});
const keyBits = {ArrowLeft:1,ArrowUp:1,Enter:2,' ':2,ArrowRight:4,ArrowDown:4};
document.addEventListener('keydown',event=>{
  const target = event.target instanceof Element ? event.target : document.body;
  const onDevice = target.closest('.buttons');
  if (document.querySelector('dialog[open]') || (!onDevice && target.closest('select,button,a,summary'))) return;
  if (event.key === ' ' && !onDevice) return;
  const bit = keyBits[event.key];
  if (bit !== undefined) { event.preventDefault(); if (!event.repeat) setButton(bit,true); return; }
  if (event.key === 'f') {
    const operation = document.fullscreenElement ? document.exitFullscreen() : $('.device').requestFullscreen();
    operation.catch(report);
  }
});
document.addEventListener('keyup',event=>{
  const bit = keyBits[event.key];
  if (bit !== undefined && levels[bit]) { event.preventDefault(); setButton(bit,false); }
});
window.render_game_to_text = () => JSON.stringify({coordinate_system:'240x320, origin top-left; x right, y down',connected,...state,selected_action:state?.screen===1?state.menu[state.selection].label:null});
window.advanceTime = async (ms) => {
  await pending;
  if (state?.manual_clock) await enqueue('/api/advance',{ms:Math.min(60000,Math.round(ms))});
  else await new Promise(resolve=>setTimeout(resolve,ms));
};
async function poll() {
  try { await enqueue('/api/state'); } catch { /* report() already presents failure. */ }
  const animated = state?.speed !== 0 && [0,3,7,10].includes(state?.screen);
  setTimeout(poll, animated || pressed ? 70 : 300);
}
async function start() {
  placeholder('Verbinde Spielkern ...');
  try {
    const response = await fetch('/api/info');
    if (!response.ok) throw new Error('Gerätedaten konnten nicht geladen werden.');
    info = await response.json();
    poll();
  } catch (error) { report(error); }
}
start();
