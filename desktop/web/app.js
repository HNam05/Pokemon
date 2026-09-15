'use strict';
const canvas = document.querySelector('#screen');
const ctx = canvas.getContext('2d');
const $ = (selector) => document.querySelector(selector);
let assets = null;
const loadedSpecies = new Map();
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

function centeredPet(y, species = state.species, height = 96) {
  const sprite = assets?.animations[species]?.[0]?.[0] || assets?.sprites[species];
  if (!sprite) return;
  const info=assets.catalog.find(p=>p.species===species);
  const scale=Math.max(1,Math.min(info?.scale||4,Math.floor(height/sprite.height),Math.floor(184/sprite.width)));
  ctx.drawImage(sprite.bitmap,Math.floor((240-sprite.width*scale)/2),Math.floor(y+(height-sprite.height*scale)/2),sprite.width*scale,sprite.height*scale);
}
function animatedPet() {
  const a = state.animation;
  const clip = reducedMotion ? ([4,6,7].includes(a.clip) ? a.clip : 0) : a.clip;
  const sprite = assets.animations[state.species][clip][reducedMotion ? 0 : a.frame];
  const scale = reducedMotion ? sprite.scale : a.scale;
  const x = reducedMotion ? sprite.draw_x : a.draw_x;
  const y = reducedMotion ? sprite.draw_y : a.draw_y;
  const flip = !reducedMotion && a.flip;
  ctx.save();
  ctx.beginPath(); ctx.rect(0,34,240,178); ctx.clip();
  ctx.translate(x+(flip?sprite.width*scale:0),y);
  ctx.scale(flip ? -scale : scale,scale);
  ctx.drawImage(sprite.bitmap,0,0);
  ctx.restore();
}
function meter(label, value, y) {
  text(label, 14, y, 10); text(`${value}`, 226, y, 10, '#313a32', 'right');
  rect(14, y + 6, 212, 5, '#cccbb5'); rect(14, y + 6, Math.round(value * 2.12), 5, value < 25 ? '#a14131' : '#586e47');
}
function scene() {
  const night = state.sleeping || state.minute_of_day < 360 || state.minute_of_day >= 1200;
  ctx.drawImage(assets.scenes[night?1:0].bitmap,0,34);
  if (state.species === 0) centeredPet(115);
  else animatedPet();
  if (state.trainer_name) {
    const greeting=`Hallo, ${state.trainer_name}!`;
    rect(8,36,Math.min(224,greeting.length*6+8),17,'#384738');
    text(greeting,12,49,10,'#f8efd2');
  }
  if (state.sleeping) text('Z z', 175, 109, 14, '#f8efd2');
  for (let i = 0; i < state.waste; i++) {
    rect(15 + i * 13, 196, 9, 5, '#665337'); rect(18 + i * 13, 193, 4, 4, '#665337');
  }
  if (state.sick) { rect(17,52,8,22,'#a14131'); rect(10,59,22,8,'#a14131'); }
}
function draw() {
  ctx.imageSmoothingEnabled = false;
  rect(0, 0, 240, 320, '#e8e5cf');
  if (!state || !assets) { text('Verbinde Spielkern ...', 120, 160, 10, '#313a32', 'center'); return; }
  const clock = `${String(Math.floor(state.minute_of_day / 60)).padStart(2,'0')}:${String(state.minute_of_day % 60).padStart(2,'0')}`;
  rect(0,0,240,33,'#384738'); text(state.name.toUpperCase(),12,21,12,'#f1ecd4');text(clock,228,21,11,'#f1ecd4','right');
  if (state.screen === 5) {
    const index=assets.catalog.findIndex(p=>p.species===state.starter);
    text('DEIN ERSTER BEGLEITER',120,54,11,'#313a32','center');
    text(`${index+1} / ${assets.catalog.length}`,120,72,10,'#59614f','center');
    ctx.drawImage(assets.scenes[0].bitmap,0,32,240,128,0,78,240,128);
    centeredPet(78,state.starter,128);
    text('<',20,155,18); text('>',220,155,18,'#313a32','right');
    text(state.starter_name.toUpperCase(),120,221,Math.min(16,Math.floor(280/state.starter_name.length)),'#313a32','center');
    lines(state.starter_form || 'Neugierig auf dein Abenteuer.',242);
    text('Seitentaste halten: blaettern',120,264,9,'#59614f','center');
    text('OK: Dieses Ei waehlen',120,281,10,'#313a32','center');
  } else if (state.screen === 1) {
    text('WAS MACHEN WIR?',14,56,11);
    text(`${state.selection+1}/${state.menu.length}`,226,56,10,'#59614f','right');
    state.menu.slice(state.menu_start,state.menu_start+5).forEach((item,row) => {
      const selected = state.selection === state.menu_start+row;
      if (selected) rect(8,70+row*32,217,29,'#465b40');
      text(item.label,16,89+row*32,11,selected?'#f6efd5':item.enabled?'#313a32':'#6c6d5c');
    });
    rect(232,70,2,157,'#bcc0a9');
    rect(231,70+state.menu_start*15.7,4,78,'#657756');
    lines(state.menu[state.selection].hint,253);
    text('OK halten: zurueck',120,287,9,'#59614f','center');
  } else if (state.screen === 6) {
    text('WAS BRAUCHE ICH?',120,57,12,'#313a32','center');
    lines(state.care_hint,89);
    const tips = [['HUNGER','Beere im Menue: Fuettern'],['MUEDIGKEIT','Schlafen lassen, dann wecken'],['LANGEWEILE','Kurz zusammen spielen'],['UNORDNUNG / KRANK','Saubermachen oder Medizin']];
    tips.forEach(([heading,detail],i)=>{text(heading,14,132+i*41,10);text(detail,14,148+i*41,9,'#59614f');});
  } else if (state.screen === 7) {
    text('ENTONS DENKPAUSE',120,57,12,'#313a32','center');
    text(`Runde ${state.mini.round+1}/3`,120,77,10,'#59614f','center');
    centeredPet(90,4);
    text(state.mini.recalling ? 'JETZT DU!' : 'MERKEN ...',120,206,11,'#313a32','center');
    const active = Math.floor(state.mini.elapsed_ms/800);
    const symbol = !state.mini.recalling && state.mini.elapsed_ms%800<600 ? state.mini.pattern[active] : -1;
    ['<','OK','>'].forEach((label,i)=>{
      rect(16+i*76,222,56,34,i===symbol?'#465b40':'#d2d6bd');
      text(label,44+i*76,244,13,i===symbol?'#f6efd5':'#313a32','center');
    });
    text(state.mini.recalling ? `${state.mini.entered}/3 eingegeben` : 'Links, OK, Rechts merken',120,281,10,'#313a32','center');
  } else if (state.screen === 2) {
    text('SO GEHT ES MIR',14,57,11);
    [['Satt',state.fullness],['Froh',state.happiness],['Energie',state.energy],['Sauber',state.hygiene],['Gesund',state.health],['Bindung',state.friendship]].forEach(([l,v],i) => meter(l,v,81+i*30));
    text(`EP ${state.experience}`,14,266,10);
    text(state.species !== 1 ? 'Entwicklung folgt.' : state.can_evolve ? 'Bereit zur Entwicklung!' : 'Ab 1 Tag + 70 Bindung +60 EP',14,283,10);
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
    centeredPet(72,state.mini.memory?4:state.species);text('GUT GESPIELT',120,193,15,'#313a32','center');
    text(state.mini.memory ? (state.mini.score ? 'Alle Zeichen gemerkt!' : 'Enton hat es vergessen.') : `${state.mini.score} von 5 Beeren`,120,219,11,'#313a32','center');
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
      lines(state.attention ? state.care_hint : state.message,275);
    }
  }
  rect(0,301,240,19,'#d4d6bd');
  const footer = state.screen === 0 ? 'STATUS     OK: MENUE     STATUS' : state.screen === 1 ? 'HOCH       OK: WAHL      RUNTER' : state.screen === 3 ? 'LINKS      OK: FANGEN    RECHTS' : state.screen === 5 ? 'VORHER     OK: WAHL      WEITER' : state.screen === 7 ? 'LINKS        OK        RECHTS' : 'BELIEBIGE TASTE: ZURUECK';
  text(footer,120,314,8,'#374735','center');
}

function update(next) {
  state = next;
  const credit=assets.catalog.find(p=>p.species===(state.screen===5?state.starter:state.species))?.credit;
  $('#art-credit').textContent = credit ? `Grafik: ${credit}` : 'Pocket Pet Prototypgrafik';
  $('#pet-name').textContent = state.trainer_name ? `${state.trainer_name}.` : state.species === 0 ? 'kleines Ei.' : `${state.name}.`;
  const list = state.screen === 1;
  $('#left span').textContent = list ? '▲' : '◀';
  $('#right span').textContent = list ? '▼' : '▶';
  $('#left-label').textContent = list ? 'HOCH' : 'LINKS';
  $('#right-label').textContent = list ? 'RUNTER' : 'RECHTS';
  $('#left').setAttribute('aria-label',list?'Vorheriger Eintrag, hoch':'Links');
  $('#right').setAttribute('aria-label',list?'Nächster Eintrag, runter':'Rechts');
  $('#game-clock').textContent = `${String(Math.floor(state.minute_of_day / 60)).padStart(2,'0')}:${String(state.minute_of_day % 60).padStart(2,'0')}`;
  $('#status-label').textContent = state.screen === 5 ? 'Wähle deinen Begleiter' : state.speed === 0 ? 'Spiel pausiert' : state.species === 0 ? 'Wartet aufs Schlüpfen' : state.health === 0 ? 'Braucht Medizin' : state.sleeping ? 'Schläft gerade' : state.attention ? 'Braucht deine Pflege' : 'Fühlt sich wohl';
  $('#message').textContent = state.screen === 1 ? state.menu[state.selection].hint : state.message;
  $('#care-hint').textContent = state.care_hint;
  $('#age').textContent = `${Math.floor(state.age_minutes/60)} h ${state.age_minutes%60} min`;
  $('#bond').textContent = `${state.friendship} / 100`; $('#xp').textContent = `${state.experience} EP`;
  $('#speed').value = String(state.speed);
  $('#skip').disabled = [3,5,7].includes(state.screen);
  $('#error').hidden = !state.storage_error;
  $('#error').textContent = state.storage_error || '';
  $('#accessible-state').textContent = `${state.name}. ${state.message} Satt ${state.fullness}, froh ${state.happiness}, Energie ${state.energy}, Sauberkeit ${state.hygiene}, Gesundheit ${state.health}. ${state.screen === 1 ? `Menü: ${state.menu[state.selection].label}.` : state.screen===5 ? `Auswahl: ${state.starter_name} ${state.starter_form}.` : ''}`;
  canvas.setAttribute('aria-label', $('#accessible-state').textContent);
  draw();
}
async function request(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Verbindung fehlgeschlagen.');
  await ensureSpecies(result.species);
  await ensureSpecies(result.starter);
  connected = true; update(result); return result;
}
function decodeSprite(sprite) {
  const bitmap=document.createElement('canvas');bitmap.width=sprite.width;bitmap.height=sprite.height;
  const context=bitmap.getContext('2d');const image=context.createImageData(sprite.width,sprite.height);
  sprite.pixels.forEach((pixel,i)=>{
    if(pixel!==65536) image.data.set([Math.round(((pixel>>11)&31)*255/31),Math.round(((pixel>>5)&63)*255/63),Math.round((pixel&31)*255/31),255],i*4);
  });
  context.putImageData(image,0,0);sprite.bitmap=bitmap;
  delete sprite.pixels;
}
async function ensureSpecies(species) {
  if(assets.animations[species]) return;
  const response=await fetch(`/api/assets/${species}`);
  if(!response.ok) throw new Error('Pokemon-Grafik konnte nicht geladen werden.');
  const data=await response.json();
  for(const sprite of [...data.sprites,...data.animations.flat(2)]) decodeSprite(sprite);
  assets.sprites[species]=data.sprites[0];assets.animations[species]=data.animations[0];
  loadedSpecies.set(species,true);
  while(loadedSpecies.size>4) {
    const old=loadedSpecies.keys().next().value;loadedSpecies.delete(old);
    delete assets.sprites[old];delete assets.animations[old];
  }
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
let navDelay=null,navInterval=null,navBusy=false,navButton=null;
function stopNavigation() {
  clearTimeout(navDelay);clearInterval(navInterval);navButton=null;
}
function startNavigation(button) {
  if(navButton===button) return;
  stopNavigation();navButton=button;
  const step=()=>{
    if(navBusy) return;
    navBusy=true;press(button).catch(()=>{}).finally(()=>{navBusy=false;});
  };
  step();
  navDelay=setTimeout(()=>{navInterval=setInterval(()=>{
    if([1,5].includes(state?.screen)) step();
  },160);},450);
}
for(const [id,button] of [['left',0],['right',2]]) {
  const element=$(`#${id}`);
  element.addEventListener('pointerdown',event=>{
    if(event.button!==0)return;element.setPointerCapture(event.pointerId);startNavigation(button);
  });
  element.addEventListener('pointerup',stopNavigation);
  element.addEventListener('pointercancel',stopNavigation);
  element.addEventListener('lostpointercapture',stopNavigation);
  element.addEventListener('click',event=>{if(event.detail===0)press(button).catch(()=>{});});
}
let holdTimer = null;
let holding = false;
let holdConsumed = false;
function startConfirm() {
  if (holding) return;
  holding = true;
  holdConsumed = false;
  holdTimer = setTimeout(()=>{
    holdConsumed = true;
    enqueue('/api/back',{}).catch(()=>{});
  },700);
}
function releaseConfirm(cancel = false) {
  if (!holding) return;
  clearTimeout(holdTimer);
  holding = false;
  if (!cancel && !holdConsumed) press(1).catch(()=>{});
}
$('#confirm').addEventListener('pointerdown',event=>{
  if (event.button !== 0) return;
  $('#confirm').setPointerCapture(event.pointerId);
  startConfirm();
});
$('#confirm').addEventListener('pointerup',event=>{
  const box = $('#confirm').getBoundingClientRect();
  releaseConfirm(event.clientX<box.left || event.clientX>box.right || event.clientY<box.top || event.clientY>box.bottom);
});
$('#confirm').addEventListener('pointercancel',()=>releaseConfirm(true));
$('#confirm').addEventListener('click',event=>{if(event.detail===0) press(1).catch(()=>{});});
window.addEventListener('blur',()=>{releaseConfirm(true);stopNavigation();});
$('#speed').addEventListener('change',event=>{enqueue('/api/speed',{speed:Number(event.target.value)}).catch(()=>{});});
$('#skip').addEventListener('click',()=>{enqueue('/api/skip',{minutes:10}).catch(()=>{});});
$('#save').addEventListener('click',()=>{enqueue('/api/save',{}).then(result=>{
  if (!result.storage_error) $('#save-status').textContent = `Gespeichert um ${new Date().toLocaleTimeString('de-DE')}.`;
}).catch(()=>{});});
$('#about-link').addEventListener('click',event=>{event.preventDefault();$('#about').showModal();});
document.addEventListener('keydown',event=>{
  const onDevice = event.target.closest('.buttons');
  if (event.repeat || $('#about').open || (!onDevice && event.target.closest('select,button,a,summary'))) return;
  if (event.key === 'Enter' || (event.key === ' ' && event.target.id === 'confirm')) {event.preventDefault();startConfirm();return;}
  const button = {ArrowLeft:0,ArrowUp:0,ArrowRight:2,ArrowDown:2}[event.key];
  if (button !== undefined) { event.preventDefault(); startNavigation(button); }
  if (event.key === 'f') {
    const operation = document.fullscreenElement ? document.exitFullscreen() : $('.device').requestFullscreen();
    operation.catch(report);
  }
});
document.addEventListener('keyup',event=>{
  if(['ArrowLeft','ArrowUp','ArrowRight','ArrowDown'].includes(event.key)) stopNavigation();
  if ((event.key==='Enter' || event.key===' ') && holding) {event.preventDefault();releaseConfirm();}
});
window.render_game_to_text = () => JSON.stringify({coordinate_system:'240x320, origin top-left; x right, y down',connected,...state,selected_action:state?.screen===1?state.menu[state.selection].label:null});
window.advanceTime = async (ms) => {
  await pending;
  if (state?.manual_clock) await enqueue('/api/advance',{ms:Math.min(60000,Math.round(ms))});
  else await new Promise(resolve=>setTimeout(resolve,ms));
};
async function poll() {
  try { await enqueue('/api/state'); } catch { /* report() already presents failure. */ }
  setTimeout(poll,state?.speed!==0 && [0,3,7].includes(state?.screen)?60:400);
}
async function start() {
  draw();
  try {
    const response = await fetch('/api/assets');
    if (!response.ok) throw new Error('Grafiken konnten nicht geladen werden.');
    assets = await response.json();
    for (const sprite of [...assets.sprites,...assets.animations.flat(2),...assets.scenes]) decodeSprite(sprite);
    poll();
  } catch (error) { report(error); }
}
start();
