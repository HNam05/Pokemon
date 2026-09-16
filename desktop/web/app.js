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
const needFields=['fullness','happiness','energy','hygiene','health','friendship'];
const needLabels=['Satt','Froh','Energie','Sauber','Gesund','Bindung'];
function needBar(x,y,width,value,low) {
  rect(x,y,width,8,'#c8cbb5');
  rect(x,y,Math.round(width*value/100),8,value<low?'#a14131':'#516c49');
  for(let i=1;i<5;i++) rect(x+Math.floor(width*i/5),y,1,8,'#e8e5cf');
}
function meter(label,value,y,index) {
  text(label,14,y,11);
  const low=assets.need_low[index];
  text(value<low?'BRAUCHT PFLEGE':value===100?'VOLL':'',154,y,8,value<low?'#a14131':'#59614f','right');
  text(`${value}/100`,226,y,10,'#313a32','right');
  needBar(14,y+7,212,value,low);
}
function changeText() {
  const f=state.feedback;
  return [...needFields.map((field,i)=>[needLabels[i],f[field]]),['EP',f.experience]]
    .filter(([,value])=>value!==0).map(([label,value])=>`${label} ${value>0?'+':''}${value}`).join('  ');
}
function smallPet(y,species,height) {
  ctx.save();ctx.beginPath();ctx.rect(0,y,240,height);ctx.clip();
  ctx.drawImage(assets.scenes[0].bitmap,0,60,240,height,0,y,240,height);
  centeredPet(y,species,height);ctx.restore();
}
function berry(x,y) {
  rect(x-7,y-5,14,12,'#653d2d');rect(x-9,y-2,18,7,'#653d2d');
  rect(x-6,y-4,12,10,'#b44a39');rect(x-4,y-3,4,3,'#f2bb81');
  rect(x-2,y-9,3,5,'#49693c');rect(x+1,y-9,5,3,'#7c9450');
}
function gameIntro() {
  const memory=state.mini.memory;
  text(memory?'ENTONS DENKPAUSE':'BEERENFANG',120,54,13,'#313a32','center');
  smallPet(66,memory?4:state.species,80);
  text(memory?'HINSEHEN. MERKEN. NACHSPIELEN.':'DREI SPUREN. FUENF BEEREN.',120,164,10,'#313a32','center');
  lines(memory?'Die Folge waechst: 2, 3, dann 4 Zeichen.':'Links / Rechts bewegt den Korb.',185);
  lines(memory?'Spiele sie mit Links, OK und Rechts nach.':'Druecke OK, wenn die Beere im Fangfeld ist.',216);
  rect(8,242,224,1,'#c3c7b0');
  text('START: -5 SATT  /  -8 ENERGIE',120,259,10,'#8c4433','center');
  text(memory?'Pro Runde: bis +4 froh, +2 Bindung':'Pro Fang: bis +4 froh, +2 Bindung',120,278,9,'#59614f','center');
  text('Dazu je +3 EP. Abbruch ohne Gewinn.',120,292,8,'#59614f','center');
}
function catchGame() {
  const m=state.mini;
  text('BEERENFANG',12,53,12);text(`${m.phase===4?m.round:Math.min(5,m.round+1)}/5`,228,53,12,'#313a32','right');
  text(`${m.score} gefangen`,12,70,10,'#59614f');
  ctx.drawImage(assets.scenes[0].bitmap,0,79);
  const zoneY=Math.floor(92+130*m.catch_open_ms/m.fall_ms);
  rect(8,zoneY,224,230-zoneY,'#c4d1a2');
  for(let lane=0;lane<3;lane++) {
    const x=40+lane*80;
    rect(x-30,zoneY,60,2,'#5c7849');
    rect(x-30,230,60,2,'#5c7849');
    rect(x,103,1,zoneY-108,'#91a076');
  }
  text('FANGFELD',120,zoneY-7,9,'#304536','center');
  const x=40+m.lane*80;
  rect(x-26,239,52,17,'#6a4d31');rect(x-22,240,44,13,'#ba8950');
  rect(x-30,235,60,5,'#513e2d');rect(x-19,245,38,2,'#805c35');
  for(let i=-14;i<=14;i+=14)rect(x+i,240,2,13,'#805c35');
  if(m.phase===1)berry(40+m.target*80,Math.floor(92+130*m.elapsed_ms/m.fall_ms));
  if(m.phase===0 || m.phase===4) {
    rect(12,122,216,47,'#e8e5cf');
    text(m.phase===0?'BEREIT?':m.success?'GEFANGEN!':'KNAPP DANEBEN',120,142,13,'#313a32','center');
    text(m.phase===0?'Gleich faellt die erste Beere.':state.message,120,158,9,'#59614f','center');
  }
  rect(0,258,240,42,'#e8e5cf');
  text(m.phase===1 && m.elapsed_ms>=m.catch_open_ms?'JETZT OK!':m.phase===1?'Korb unter die Beere bewegen':m.phase===0?'Tasten gleich aktiv':m.round===5?'Ergebnis folgt ...':'Naechste Beere kommt ...',120,277,10,'#313a32','center');
  text('OK halten: Spiel verlassen',120,292,8,'#59614f','center');
}
function memoryGame() {
  const m=state.mini;
  text('ENTONS DENKPAUSE',120,53,12,'#313a32','center');
  text(`Runde ${Math.min(3,m.phase===4 && m.success?m.round:m.round+1)} / 3`,120,70,10,'#59614f','center');
  smallPet(80,4,68);
  const phaseText=m.phase===0?'BEREIT?':m.phase===2?'NUR ANSEHEN':m.phase===3?'JETZT DU':m.success?'GUT GEMERKT!':'NOCHMAL UEBEN';
  text(phaseText,120,165,12,'#313a32','center');
  const active=m.phase===2?m.cue:m.phase===3 && m.input_ms>0?m.last_button:-1;
  ['<','OK','>'].forEach((label,i)=>{
    const lit=i===active;
    rect(12+i*76,179,64,46,lit?'#3d5940':'#ced2b9');
    text(label,44+i*76,208,20,lit?'#f5efd5':'#536047','center');
    text(['LINKS','MITTE','RECHTS'][i],44+i*76,239,8,'#59614f','center');
  });
  for(let i=0;i<m.length;i++) {
    const x=120-m.length*12+i*24;
    rect(x,252,16,9,i<m.entered?'#48653f':'#c3c9ad');
  }
  if(m.phase===3) {
    rect(12,274,216,3,'#c3c9ad');
    rect(12,274,Math.round(216*(1-m.elapsed_ms/m.duration_ms)),3,'#596f48');
    text(`${m.entered} / ${m.length} Zeichen   ${Math.ceil((m.duration_ms-m.elapsed_ms)/1000)} s`,120,292,9,'#313a32','center');
  } else text(m.phase===4?state.message:m.phase===0?'Gleich beginnt die Folge.':`${m.length} Zeichen merken. Dann bist du dran.`,120,287,9,'#59614f','center');
}
function gameResult() {
  const m=state.mini,f=state.feedback;
  text(m.score?'GUT ZUSAMMEN GESPIELT':'WEITER UEBEN',120,54,12,'#313a32','center');
  smallPet(67,m.memory?4:state.species,88);
  text(`${m.score} / ${m.memory?3:5} ${m.memory?'Runden':'Beeren'}`,120,178,16,'#313a32','center');
  [['Froh',f.happiness],['Bindung',f.friendship],['Erfahrung',f.experience]].forEach(([label,value],i)=>{
    text(label,20,206+i*25,11);text(`+${value}${i===2?' EP':''}`,220,206+i*25,12,'#48653f','right');
    rect(20,213+i*25,200,1,'#c6cbb4');
  });
  text('Dein tatsaechlich erhaltener Zuwachs.',120,284,9,'#59614f','center');
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
    const current=state.menu[state.selection];
    text(current.section,12,53,11);text(`${state.selection+1} / ${state.menu.length}`,228,53,10,'#59614f','right');
    state.menu.slice(state.menu_start,state.menu_start+5).forEach((item,row)=>{
      const selected=state.selection===state.menu_start+row,y=66+row*31;
      if(selected)rect(8,y,218,29,'#3d5940');
      else rect(12,y+29,210,1,'#c8cbb8');
      text(selected?'>':item.enabled?'':'-',17,y+19,11,selected?'#f3edd5':'#737760');
      const label=item.label==='Schlafen / Wecken'?(state.sleeping?'Aufwecken':'Schlafen'):item.label;
      text(label,32,y+19,11,selected?'#f3edd5':item.enabled?'#313a32':'#737760');
    });
    rect(232,66,2,153,'#c2c7ad');rect(231,66+state.menu_start*15.3,4,76,'#657756');
    text(current.enabled?'OK: AUSWAEHLEN':'GERADE NICHT MOEGLICH',12,242,9,current.enabled?'#48653f':'#974734');
    lines(current.hint,261);
    text('Seitentasten: blaettern / OK halten: zurueck',120,291,8,'#59614f','center');
  } else if (state.screen === 6) {
    text('WAS BRAUCHE ICH?',120,57,12,'#313a32','center');
    lines(state.care_hint,89);
    const tips = [['HUNGER','Beere im Menue: Fuettern'],['MUEDIGKEIT','Schlafen lassen, dann wecken'],['LANGEWEILE','Kurz zusammen spielen'],['UNORDNUNG / KRANK','Saubermachen oder Medizin']];
    tips.forEach(([heading,detail],i)=>{text(heading,14,132+i*41,10);text(detail,14,148+i*41,9,'#59614f');});
  } else if (state.screen === 8) {
    gameIntro();
  } else if (state.screen === 7) {
    memoryGame();
  } else if (state.screen === 2) {
    text('SO GEHT ES MIR',14,55,12);
    needFields.forEach((field,i)=>meter(needLabels[i],state[field],79+i*29,i));
    text(`ERFAHRUNG ${state.experience} EP`,14,266,10);
    text(state.can_evolve?'Bereit zur Entwicklung!':state.starter===1 && state.species===1?'Entwicklung: 1 Tag, Bindung 70, EP 60':'Pflegehilfe findest du im Menue.',14,285,9,'#59614f');
  } else if (state.screen === 3) {
    catchGame();
  } else if (state.screen === 4) {
    gameResult();
  } else {
    scene();
    if (state.species === 0) {
      text('Ein neuer Freund wartet.',120,241,11,'#313a32','center');
      text(`Schluepft in ${10-state.age_minutes} Min.`,120,263,10,'#59614f','center');
    } else {
      needFields.slice(0,3).forEach((field,i)=>{
        const x=8+i*78,value=state[field],low=assets.need_low[i];
        text(needLabels[i].toUpperCase(),x,228,8);
        text(String(value),x+68,228,11,value<low?'#a14131':'#313a32','right');
        needBar(x,237,68,value,low);
      });
      if(state.feedback.remaining_ms>0)text(changeText(),120,260,10,'#48653f','center');
      else text(state.sleeping?'ERHOLT SICH':state.attention?'ZEIT FUER PFLEGE':'FUEHLT SICH WOHL',120,261,9,state.attention?'#a14131':'#59614f','center');
      lines(state.attention?state.care_hint:state.message,280);
    }
  }
  rect(0,301,240,19,'#d4d6bd');
  const footer = state.screen === 0 ? 'STATUS     OK: MENUE     STATUS' : state.screen === 1 ? 'HOCH       OK: WAHL      RUNTER' : state.screen === 3 ? 'LINKS      OK: FANGEN    RECHTS' : state.screen === 5 ? 'VORHER     OK: WAHL      WEITER' : state.screen === 8 ? 'ZURUECK     OK: START     ZURUECK' : state.screen === 7 ? 'LINKS        OK        RECHTS' : 'BELIEBIGE TASTE: ZURUECK';
  text(footer,120,314,8,'#374735','center');
}

function update(next) {
  state = next;
  $('#test-controls').hidden = !state.test_controls;
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
  needFields.slice(0,3).forEach((field,i)=>{
    const meter=$(`#need-${field}`);
    meter.value=state[field];meter.low=assets.need_low[i];
    $(`#value-${field}`).textContent=`${state[field]} / 100`;
  });
  $('#care-receipt').textContent=state.feedback.remaining_ms>0?changeText():'';
  $('#age').textContent = `${Math.floor(state.age_minutes/60)} h ${state.age_minutes%60} min`;
  $('#bond').textContent = `${state.friendship} / 100`; $('#xp').textContent = `${state.experience} EP`;
  $('#speed').value = String(state.speed);
  $('#skip').disabled = [3,5,7,8].includes(state.screen);
  $('#error').hidden = !state.storage_error;
  $('#error').textContent = state.storage_error || '';
  const gameHelp=[3,7,8,4].includes(state.screen)?` ${state.mini.memory?'Entons Denkpause':'Beerenfang'}. ${state.screen===8?'OK startet. Kosten: 5 Satt und 8 Energie.':state.screen===4?`Erhalten: ${changeText()||'keine Punkte'}.`:state.mini.phase===3?`Eingabe ${state.mini.entered} von ${state.mini.length}.`:state.mini.phase===2 && state.mini.cue>=0?`Merken: ${['Links','OK','Rechts'][state.mini.cue]}.`:state.message}`:'';
  $('#accessible-state').textContent = `${state.name}. ${state.message} Satt ${state.fullness}, froh ${state.happiness}, Energie ${state.energy}, Sauberkeit ${state.hygiene}, Gesundheit ${state.health}. ${state.screen === 1 ? `Menü: ${state.menu[state.selection].label}.` : state.screen===5 ? `Auswahl: ${state.starter_name} ${state.starter_form}.` : ''}`;
  $('#accessible-state').textContent+=gameHelp;
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
$('#test-reset').addEventListener('click',()=>{
  stopNavigation();releaseConfirm(true);$('#reset-dialog').showModal();
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
document.addEventListener('keydown',event=>{
  const onDevice = event.target.closest('.buttons');
  if (event.repeat || document.querySelector('dialog[open]') || (!onDevice && event.target.closest('select,button,a,summary'))) return;
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
