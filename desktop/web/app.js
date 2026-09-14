'use strict';
const canvas = document.querySelector('#screen');
const ctx = canvas.getContext('2d');
const $ = (selector) => document.querySelector(selector);
const actions = ['Füttern', 'Saubermachen', 'Schlafen / Wecken', 'Medizin', 'Beeren fangen', 'Status', 'Entwickeln', 'Zurück'];
let state = null;
let pending = Promise.resolve();
let connected = false;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

function rect(x, y, w, h, color) { ctx.fillStyle = color; ctx.fillRect(x, y, w, h); }
function text(value, x, y, size = 10, color = '#313a32', align = 'left') {
  ctx.fillStyle = color; ctx.font = `bold ${size}px monospace`; ctx.textAlign = align; ctx.fillText(value, x, y);
}
function lines(value, y) {
  const words = value.split(' '); let line = '';
  for (const word of words) {
    if ((line + word).length > 30) { text(line, 120, y, 10, '#313a32', 'center'); y += 14; line = ''; }
    line += `${word} `;
  }
  text(line.trim(), 120, y, 10, '#313a32', 'center');
}

// Original, hand-authored pixel placeholder. Palette and ear/tail marks vary by species.
const sprite = [
  '...oo.............oo....',
  '...oco...........oco....',
  '...occo.........occo....',
  '....occco......occo.....',
  '....occco.....occco.....',
  '.....occco...occco......',
  '......ocoooooocco.......',
  '......occccccccco.......',
  '.....occccccccccco......',
  '.....ocwwccccwwcco......',
  '.....ocobccccobcco......',
  '.....ocobccccobcco......',
  '......occcbbcccco....oo.',
  '.......occcccco....occo.',
  '......offfffffo..occcfo.',
  '.....offfffffffoocccffo.',
  '.....ocffffffccoocfffo..',
  '.....occccccccccoofoo...',
  '.....occccccccccooo.....',
  '......occcccccco........',
  '......occo...occo.......',
  '......ooo.....ooo.......',
];
function pet(x, y, scale = 3) {
  if (state.species === 0) {
    const egg = ['....oooo....','...offffo...','..offffffo..','.offffffffo.','.offfccfffo.','offfccfffffo','offfffffccfo','offffffcccfo','offfcffffffo','.offccffffo.','..offffffo..','...oooooo...'];
    egg.forEach((row, j) => [...row].forEach((p, i) => {
      if (p !== '.') rect(x + i * scale, y + j * scale, scale, scale, {o:'#374735',f:'#f4edcf',c:'#ad844a'}[p]);
    }));
    return;
  }
  const palette = {o:'#463b2a',c:'#b88742',f:'#f1d69a',w:'#f9f1d7',b:'#282c2a'};
  if (state.species === 2) { palette.c = '#a77d88'; palette.f = '#d9b2ad'; }
  if (state.species === 3) { palette.c = '#4a5050'; palette.f = '#c7a348'; palette.o = '#252f30'; }
  sprite.forEach((row, j) => [...row].forEach((p, i) => {
    if (p !== '.') rect(x + i * scale, y + j * scale, scale, scale, palette[p]);
  }));
  if (state.sleeping) {
    rect(x + 8 * scale, y + 9 * scale, scale * 2, scale * 3, palette.c);
    rect(x + 14 * scale, y + 9 * scale, scale * 2, scale * 3, palette.c);
    rect(x + 8 * scale, y + 11 * scale, scale * 2, scale, palette.o);
    rect(x + 14 * scale, y + 11 * scale, scale * 2, scale, palette.o);
  }
}
function meter(label, value, y) {
  text(label, 14, y, 10); text(`${value}`, 226, y, 10, '#313a32', 'right');
  rect(14, y + 6, 212, 5, '#cccbb5'); rect(14, y + 6, Math.round(value * 2.12), 5, value < 25 ? '#a14131' : '#586e47');
}
function scene() {
  const night = state.sleeping || state.minute_of_day < 360 || state.minute_of_day >= 1200;
  rect(0, 33, 240, 180, night ? '#697b78' : '#cad4b6');
  rect(173, 49, 18, 18, '#eee1a1');
  if (night) rect(179, 46, 15, 15, '#697b78');
  rect(0, 145, 240, 68, '#a5b389');
  rect(0, 173, 240, 40, '#889765');
  for (const [x, y] of [[13,175],[35,161],[189,171],[211,190],[56,197]]) {
    rect(x, y, 2, 5, '#617953'); rect(x+3, y-2, 2, 7, '#617953');
  }
  const bob = reducedMotion || state.sleeping ? 0 : Math.floor(Date.now() / 600) % 2;
  if (state.species === 0) pet(95, 115 + bob, 4);
  else pet(70, 102 + bob, 4);
  if (state.sleeping) text('Z z', 175, 109, 14, '#f8efd2');
  for (let i = 0; i < state.waste; i++) {
    rect(15 + i * 13, 196, 9, 5, '#665337'); rect(18 + i * 13, 193, 4, 4, '#665337');
  }
  if (state.sick) { rect(17,52,8,22,'#a14131'); rect(10,59,22,8,'#a14131'); }
}
function draw() {
  ctx.imageSmoothingEnabled = false;
  rect(0, 0, 240, 320, '#e8e5cf');
  if (!state) { text('Verbinde Spielkern ...', 120, 160, 10, '#313a32', 'center'); return; }
  const clock = `${String(Math.floor(state.minute_of_day / 60)).padStart(2,'0')}:${String(state.minute_of_day % 60).padStart(2,'0')}`;
  rect(0,0,240,33,'#384738'); text(state.name.toUpperCase(),12,21,12,'#f1ecd4');text(clock,228,21,11,'#f1ecd4','right');
  if (state.screen === 1) {
    text('WAS MACHEN WIR?', 14, 56, 11);
    actions.forEach((action, index) => {
      const selected = state.selection === index;
      if (selected) rect(8, 69 + index * 26, 224, 24, '#465b40');
      text(action, 16, 85 + index * 26, 11, selected ? '#f6efd5' : '#313a32');
    });
  } else if (state.screen === 2) {
    text('SO GEHT ES MIR',14,57,11);
    [['Satt',state.fullness],['Froh',state.happiness],['Energie',state.energy],['Sauber',state.hygiene],['Gesund',state.health],['Bindung',state.friendship]].forEach(([l,v],i) => meter(l,v,81+i*30));
    text(`EP ${state.experience} / Entwicklung: 60`,14,266,10);
    text(state.can_evolve ? 'Bereit zur Entwicklung!' : 'Ab 1 Tag + 70 Bindung',14,283,10);
  } else if (state.screen === 3) {
    text(`BEERENFANG ${state.mini.round+1}/5`,12,56,11);
    text(`${state.mini.score} Treffer`,12,73,10);
    rect(8,160,224,82,'#bbcaa1');
    text('FANGBEREICH',120,235,9,'#49623c','center');
    for (let lane=0;lane<3;lane++) { rect(38+lane*80,89,1,129,'#c3c7b0'); rect(10+lane*80,247,60,2,'#9da78a'); }
    const berryX = 40 + state.mini.target * 80;
    const berryY = 95 + state.mini.elapsed_ms / 1800 * 130;
    rect(berryX-7,berryY,14,13,'#a4412d');rect(berryX-3,berryY-5,8,5,'#4b6640');
    rect(14+state.mini.lane*80,250,52,18,'#957148'); rect(10+state.mini.lane*80,247,60,5,'#553f2d');
    text(state.mini.elapsed_ms >= 900 ? 'JETZT: OK!' : 'Unter die Beere bewegen',120,291,10,'#313a32','center');
  } else if (state.screen === 4) {
    pet(72,72,4);text('GUT GESPIELT',120,193,15,'#313a32','center');
    text(`${state.mini.score} von 5 Beeren`,120,219,12,'#313a32','center');
    text(`+${state.mini.score*2} Bindung  +${state.mini.score*3} EP`,120,249,10,'#313a32','center');
  } else {
    scene();
    if (state.species === 0) {
      text('Ein neuer Freund wartet.',120,241,11,'#313a32','center');
      text(`Schluepft in ${10-state.age_minutes} Min.`,120,263,10,'#59614f','center');
    } else {
      for (const [i,label,value] of [[0,'SATT',state.fullness],[1,'FROH',state.happiness],[2,'ENERGIE',state.energy]]) {
        const x = 12 + i * 78;
        text(label,x,235,9); rect(x,244,60,6,'#cccbb5'); rect(x,244,Math.round(value*.6),6,value<25?'#a14131':'#586e47');
      }
      lines(state.message,275);
    }
  }
  rect(0,301,240,19,'#d4d6bd');
  const footer = state.screen === 0 ? 'STATUS     OK: MENUE     STATUS' : state.screen === 1 ? 'ZURUECK    OK: WAHL     WEITER' : state.screen === 3 ? 'LINKS      OK: FANGEN    RECHTS' : 'BELIEBIGE TASTE: ZURUECK';
  text(footer,120,314,8,'#374735','center');
}

function update(next) {
  state = next;
  $('#pet-name').textContent = state.species === 0 ? 'kleines Ei.' : `${state.name}.`;
  $('#game-clock').textContent = `${String(Math.floor(state.minute_of_day / 60)).padStart(2,'0')}:${String(state.minute_of_day % 60).padStart(2,'0')}`;
  $('#status-label').textContent = state.speed === 0 ? 'Spiel pausiert' : state.species === 0 ? 'Wartet aufs Schlüpfen' : state.health === 0 ? 'Braucht Medizin' : state.sleeping ? 'Schläft gerade' : state.attention ? 'Braucht deine Pflege' : 'Fühlt sich wohl';
  $('#message').textContent = state.message;
  $('#age').textContent = `${Math.floor(state.age_minutes/60)} h ${state.age_minutes%60} min`;
  $('#bond').textContent = `${state.friendship} / 100`; $('#xp').textContent = `${state.experience} EP`;
  $('#speed').value = String(state.speed);
  $('#skip').disabled = state.screen === 3;
  $('#error').hidden = !state.storage_error;
  $('#error').textContent = state.storage_error || '';
  $('#accessible-state').textContent = `${state.name}. ${state.message} Satt ${state.fullness}, froh ${state.happiness}, Energie ${state.energy}, Sauberkeit ${state.hygiene}, Gesundheit ${state.health}. ${state.screen === 1 ? `Menü: ${actions[state.selection]}.` : ''}`;
  canvas.setAttribute('aria-label', $('#accessible-state').textContent);
  draw();
}
async function request(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Verbindung fehlgeschlagen.');
  connected = true; update(result); return result;
}
function report(error) {
  connected = false; $('#error').hidden = false;
  $('#error').textContent = `${error.message} Läuft der lokale Server noch?`;
}
function enqueue(path, data) {
  const operation = pending.then(() => request(path, data));
  pending = operation.catch(report);
  return operation;
}
function press(button) { return enqueue('/api/button',{button}); }
$('#left').addEventListener('click',()=>{press(0).catch(()=>{});});
$('#confirm').addEventListener('click',()=>{press(1).catch(()=>{});});
$('#right').addEventListener('click',()=>{press(2).catch(()=>{});});
$('#speed').addEventListener('change',event=>{enqueue('/api/speed',{speed:Number(event.target.value)}).catch(()=>{});});
$('#skip').addEventListener('click',()=>{enqueue('/api/skip',{minutes:10}).catch(()=>{});});
$('#save').addEventListener('click',()=>{enqueue('/api/save',{}).then(result=>{
  if (!result.storage_error) $('#save-status').textContent = `Gespeichert um ${new Date().toLocaleTimeString('de-DE')}.`;
}).catch(()=>{});});
$('#about-link').addEventListener('click',event=>{event.preventDefault();$('#about').showModal();});
document.addEventListener('keydown',event=>{
  const onDevice = event.target.closest('.buttons');
  if (event.repeat || $('#about').open || (!onDevice && event.target.closest('select,button,a,summary'))) return;
  const button = {ArrowLeft:0,Enter:1,ArrowRight:2}[event.key];
  if (button !== undefined) { event.preventDefault(); press(button).catch(()=>{}); }
  if (event.key === 'f') {
    const operation = document.fullscreenElement ? document.exitFullscreen() : $('.device').requestFullscreen();
    operation.catch(report);
  }
});
window.render_game_to_text = () => JSON.stringify({coordinate_system:'240x320, origin top-left; x right, y down',connected,...state,selected_action:state?.screen===1?actions[state.selection]:null});
window.advanceTime = async (ms) => {
  await pending;
  if (state?.manual_clock) await enqueue('/api/advance',{ms:Math.min(60000,Math.round(ms))});
  else await new Promise(resolve=>setTimeout(resolve,ms));
};
async function poll() {
  try { await enqueue('/api/state'); } catch { /* report() already presents failure. */ }
  setTimeout(poll,state?.screen===3?60:400);
}
draw(); poll();
