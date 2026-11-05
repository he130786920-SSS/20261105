/* PIXEL RIFT — p5.js / JavaScript arcade.
   Original image files and reproducible image-cutting script are included.
   Combined sheets: crop frame index * frameWidth, width=frameWidth.
   Controls: arrows/A-D move, up/W jump, Z punch, X kick, Space energy,
             Shift sprint, 1/2 switch fighter, P pause, R restart, M music. */
const WORLD = { width: 1280, height: 680, floor: 543, gravity: 0.86 };
const META = {"monkey_walk":{"source":"1_all.png","frameWidth":72,"frameHeight":76,"frames":8,"width":576,"height":76},"ninja_attack":{"source":"2_all.png","frameWidth":72,"frameHeight":76,"frames":8,"width":576,"height":76},"lee_idle":{"source":"Lee Jinkang (1).png","frameWidth":150,"frameHeight":124,"frames":3,"width":450,"height":124},"lee_walk":{"source":"Lee Jinkang (1).png","frameWidth":150,"frameHeight":124,"frames":6,"width":900,"height":124},"lee_jump":{"source":"Lee Jinkang (1).png","frameWidth":150,"frameHeight":132,"frames":6,"width":900,"height":132},"lee_punch":{"source":"Lee Jinkang (1).png","frameWidth":150,"frameHeight":124,"frames":7,"width":1050,"height":124},"lee_kick":{"source":"Lee Jinkang (1).png","frameWidth":150,"frameHeight":124,"frames":6,"width":900,"height":124},"lee_hurt":{"source":"Lee Jinkang (1).png","frameWidth":150,"frameHeight":124,"frames":2,"width":300,"height":124},"chun_idle":{"source":"Chun-Li(1).png","frameWidth":52,"frameHeight":56,"frames":10,"width":520,"height":56},"chun_walk":{"source":"Chun-Li(1).png","frameWidth":52,"frameHeight":56,"frames":8,"width":416,"height":56},"chun_jump":{"source":"Chun-Li(1).png","frameWidth":52,"frameHeight":56,"frames":6,"width":312,"height":56},"chun_punch":{"source":"Chun-Li(1).png","frameWidth":52,"frameHeight":56,"frames":6,"width":312,"height":56},"chun_kick":{"source":"Chun-Li(1).png","frameWidth":52,"frameHeight":56,"frames":6,"width":312,"height":56},"chun_hurt":{"source":"Chun-Li(1).png","frameWidth":52,"frameHeight":56,"frames":2,"width":104,"height":56},"robot_walk":{"source":"CM_Enemies.png","frameWidth":76,"frameHeight":76,"frames":8,"width":608,"height":76},"robot_idle":{"source":"CM_Enemies.png","frameWidth":76,"frameHeight":76,"frames":8,"width":608,"height":76},"energy_blast":{"source":"原創程式繪製特效","frameWidth":64,"frameHeight":64,"frames":6,"width":384,"height":64}};
const SHEET_NAMES = Object.keys(META);
const FIGHTERS = {
  lee: { name: 'LEE JINKANG', label: '李振康', prefix:'lee', scale:1.56, speed:5.4, jump:17.1, damage:1.08 },
  chun:{ name: 'CHUN-LI',label:'春麗', prefix:'chun',scale:3.03,speed:6.1,jump:18.2,damage:.92 }
};
const ENEMY_KIND = {
  monkey: {strip:'monkey_walk',scale:1.43,health:3,speed:1.55,points:100,hue:'#fabe76'},
  ninja:  {strip:'ninja_attack',scale:1.50,health:3,speed:2.12,points:140,hue:'#aff287'},
  robot:  {strip:'robot_walk',scale:1.48,health:4,speed:1.4,points:180,hue:'#8bdcfd'}
};
let sheets={}, state='ready', fighter='lee', hero, enemies=[], bolts=[], particles=[], texts=[], score=0,wave=1, clock=0,ambientTime=0,shake=0,combo=0,comboClock=0,keys={},soundEnabled=false,bgm=null,audioCtx=null,enemySerial=0;
let canvasReady=false, currentMessage='ready';

function preload(){
  for(const name of SHEET_NAMES){ sheets[name]=loadImage('assets/sheets/'+name+'.png'); }
}
function setup(){
  const canvas=createCanvas(WORLD.width,WORLD.height);
  canvas.parent('canvas-holder');
  pixelDensity(1);
  noSmooth();
  hero=makeHero();
  enemies=[makeEnemy('monkey',960),makeEnemy('ninja',1080)];
  bgm=new Audio('assets/audio/dojo-loop.wav'); bgm.loop=true; bgm.volume=.32;
  bindUI();
  canvasReady=true;
  document.getElementById('loadingMessage').classList.add('hidden');
  paintHUD();
}
function makeHero(){return {x:290,y:WORLD.floor,vy:0,face:1,health:100,energy:100,grounded:true,action:'idle',actionAge:0,actionLen:0,invuln:0,speedF:0};}
function makeEnemy(type,x){const k=ENEMY_KIND[type];return {id:enemySerial++,type,x,y:WORLD.floor,hp:k.health,maxHp:k.health,face:-1,anim:Math.random()*30,hitAge:0,attackCD:80+Math.random()*90,dead:false,deathAge:0};}
function beginGame(){
  state='playing';hero=makeHero();score=0;wave=1;clock=0;combo=0;comboClock=0;enemySerial=0;enemies=[];bolts=[];particles=[];texts=[];
  spawnWave();hideMessage();updateStatus();beep('start');
}
function spawnWave(){
  const kinds=['monkey','ninja','robot'];
  const count=Math.min(2+Math.floor(wave/2),5);
  for(let i=0;i<count;i++){
    const type=kinds[(wave+i-1)%3];
    enemies.push(makeEnemy(type,900+i*115+Math.random()*45));
  }
  popText(WORLD.width/2,205,'WAVE '+String(wave).padStart(2,'0'),'#b9fc8b',75);
}
function draw(){
  const dt=Math.min(2.1,Math.max(.35,(typeof deltaTime==='number'?deltaTime:16.7)/16.67));
  ambientTime+=dt;
  if(state==='playing'){updateGame(dt);} 
  backgroundScene();
  drawObjects();
  paintHUD();
}
function updateGame(dt){
  clock+=dt;
  const c=FIGHTERS[fighter],left=keys.ArrowLeft||keys.KeyA||keys.btnLeft,right=keys.ArrowRight||keys.KeyD||keys.btnRight;
  const dir=(right?1:0)-(left?1:0);
  const sprint=(keys.ShiftLeft||keys.ShiftRight)?1.45:1;
  if(dir){hero.x+=dir*c.speed*dt*sprint;hero.face=dir;}
  hero.x=Math.max(68,Math.min(WORLD.width-65,hero.x));
  hero.y+=hero.vy*dt;hero.vy+=WORLD.gravity*dt;
  if(hero.y>=WORLD.floor){hero.y=WORLD.floor;hero.vy=0;hero.grounded=true;}
  hero.actionAge+=dt;
  if(hero.actionLen>0 && hero.actionAge>=hero.actionLen){hero.actionLen=0;hero.actionAge=0;}
  if(hero.actionLen<=0){hero.action=hero.grounded?(dir?'walk':'idle'):'jump';}
  hero.energy=Math.min(100,hero.energy+.078*dt);
  if(hero.invuln>0)hero.invuln-=dt;
  if(comboClock>0)comboClock-=dt;else combo=0;
  for(const enemy of enemies){
    enemy.anim+=dt;enemy.attackCD-=dt;
    if(enemy.dead){enemy.deathAge+=dt;continue;}
    const k=ENEMY_KIND[enemy.type];
    const distance=hero.x-enemy.x;
    enemy.face=Math.sign(distance)||-1;
    if(Math.abs(distance)>79){enemy.x+=Math.sign(distance)*k.speed*(1+.085*(wave-1))*dt;}
    if(Math.abs(distance)<85 && enemy.attackCD<=0 && hero.invuln<=0){
      hero.health=Math.max(0,hero.health-(enemy.type==='robot'?12:9));
      hero.invuln=46;hero.x=Math.max(70,Math.min(WORLD.width-70,hero.x-Math.sign(distance)*24));
      particlesAt(hero.x,hero.y-75,'#ffc0d2',15,4.5);
      popText(hero.x,hero.y-157,'-'+(enemy.type==='robot'?12:9),'#ff9eb9',48);
      enemy.attackCD=105;shake=8;beep('hurt');
    }
  }
  for(const b of bolts){
    b.x+=b.vx*dt;b.life-=dt;
    for(const e of enemies){if(e.dead||b.hitIds.has(e.id))continue;
      if(Math.abs(e.x-b.x)<65 && Math.abs((e.y-72)-b.y)<72){
        b.hitIds.add(e.id);damageEnemy(e,2.4,b.x,b.y);b.life=0;break;
      }
    }
  }
  bolts=bolts.filter(b=>b.life>0 && b.x>-40 && b.x<1320);
  enemies=enemies.filter(e=>!e.dead || e.deathAge<27);
  for(const p of particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=.11*dt;p.life-=dt;}
  particles=particles.filter(p=>p.life>0);
  for(const t of texts){t.y-=.73*dt;t.life-=dt;}
  texts=texts.filter(t=>t.life>0);
  if(shake>0)shake-=dt;
  if(enemies.length===0 && clock>100){wave++;clock=0;hero.energy=Math.min(100,hero.energy+22);spawnWave();}
  if(hero.health<=0){state='over';showMessage('GAME OVER','再試一次，重返道場。','重新挑戰');beep('over');updateStatus();}
}
function jump(){if(state!=='playing'||!hero.grounded)return;hero.vy=-FIGHTERS[fighter].jump;hero.grounded=false;hero.action='jump';hero.actionAge=0;hero.actionLen=0;particlesAt(hero.x,hero.y-4,'#c9e8ed',9,2);beep('jump');}
function attack(type){
  if(state!=='playing')return;
  if(hero.actionLen>4)return;
  if(type==='special'){
    if(hero.energy<22){popText(hero.x,hero.y-130,'NEED ENERGY','#fbe1a0',35);return;}
    hero.energy-=22;hero.action='kick';hero.actionAge=0;hero.actionLen=24;
    bolts.push({x:hero.x+hero.face*61,y:hero.y-87,vx:hero.face*12.5,life:85,hitIds:new Set(),phase:Math.random()*10});
    particlesAt(hero.x+hero.face*50,hero.y-90,'#88eaf8',18,6);beep('special');shake=6;
    return;
  }
  hero.action=type;hero.actionAge=0;hero.actionLen=type==='punch'?14:21;
  const range=type==='punch'?123:157;
  let hit=false;
  for(const enemy of enemies){
    if(enemy.dead)continue;
    const dx=enemy.x-hero.x;
    if(Math.abs(dx)<range && dx*hero.face>-19 && Math.abs(enemy.y-hero.y)<100){
      damageEnemy(enemy,(type==='kick'?2:1.35)*FIGHTERS[fighter].damage,enemy.x,enemy.y-85);hit=true;
    }
  }
  if(hit){shake=type==='kick'?8:4;}beep(type);
}
function damageEnemy(enemy,amount,x,y){
  if(enemy.dead)return;
  enemy.hp-=amount;enemy.hitAge=13;enemy.x+=hero.face*22;
  particlesAt(x,y,ENEMY_KIND[enemy.type].hue,15,4.8);
  popText(x,y-42,enemy.hp>0?'HIT!':'K.O.!',enemy.hp>0?'#fff9c5':'#b9ff85',38);
  if(enemy.hp<=0){enemy.dead=true;enemy.deathAge=0;combo++;comboClock=130;const value=ENEMY_KIND[enemy.type].points*Math.min(combo,5);score+=value;hero.energy=Math.min(100,hero.energy+8);popText(x,y-88,'+'+value,'#bbfa89',70);beep('ko');}
}
function particlesAt(x,y,color,count,power){for(let i=0;i<count;i++){const a=Math.random()*Math.PI*2,r=Math.random()*power+1;particles.push({x,y,vx:Math.cos(a)*r,vy:Math.sin(a)*r-1,life:24+Math.random()*22,maxLife:48,size:2+Math.random()*6,color});}}
function popText(x,y,label,color,life){texts.push({x,y,label,color,life,max:life});}
function backgroundScene(){
  const ctx=drawingContext, W=WORLD.width,H=WORLD.height;
  ctx.save();ctx.clearRect(0,0,W,H);
  let g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#14183c');g.addColorStop(.47,'#473357');g.addColorStop(1,'#75516c');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  // A pale planet and atmospheric arcs.
  ctx.globalAlpha=.22;ctx.fillStyle='#c2ddf9';ctx.beginPath();ctx.arc(920,215,145,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
  ctx.fillStyle='#e8d6d9';ctx.beginPath();ctx.arc(920,202,95,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#d1b4d6';ctx.fillRect(850,185,170,8);ctx.fillRect(827,215,193,7);ctx.fillRect(854,255,170,7);
  for(let i=0;i<80;i++){let sx=(i*223)%W,sy=((i*91)%300)+25;ctx.fillStyle=i%4===0?'#8ce4ff':'#d6add6';ctx.globalAlpha=.2+(Math.sin(ambientTime*.028+i)*.1+.1);ctx.fillRect(sx,sy,1.5,1.5);}ctx.globalAlpha=1;
  // Mountains: polygon layers add parallax.
  ctx.fillStyle='#36324e';ctx.beginPath();ctx.moveTo(0,410);for(let x=0;x<=W;x+=50){ctx.lineTo(x,395+Math.sin(x*.01+1)*45+Math.cos(x*.029)*27);}ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fill();
  ctx.fillStyle='#232944';ctx.beginPath();ctx.moveTo(0,445);for(let x=0;x<=W;x+=35){ctx.lineTo(x,442+Math.sin(x*.014)*21+Math.cos(x*.027)*10);}ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fill();
  for(let i=0;i<43;i++){const x=i*34-15+((i%3)*9),w=26+(i%3)*12,h=58+(i*37)%89;ctx.fillStyle=i%3===0?'#1a2744':'#1e2e47';ctx.fillRect(x,470-h,w,h+38);
    for(let r=0;r<4;r++)for(let c=0;c<3;c++){if((i+r+c)%3===0){ctx.globalAlpha=.36;ctx.fillStyle='#fbaea9';ctx.fillRect(x+5+c*8,479-h+r*16,3,5);ctx.globalAlpha=1;}}
  }
  // Neon gate and lanterns, made from canvas vector shapes.
  ctx.fillStyle='#131a36';ctx.fillRect(70,350,24,191);ctx.fillRect(300,350,24,191);ctx.fillRect(43,332,312,22);ctx.fillRect(68,303,264,21);ctx.fillStyle='#f28eae';ctx.fillRect(80,346,230,4);ctx.fillStyle='#a6e5e2';ctx.fillRect(75,312,257,3);
  for(let i=0;i<6;i++){const lx=392+i*145+Math.sin(i)*18;ctx.strokeStyle='#59536b';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(lx,345);ctx.lineTo(lx,410);ctx.stroke();ctx.fillStyle=i%2?'#f7ae9c':'#eac7ab';ctx.shadowBlur=14;ctx.shadowColor='#f7ae9c';ctx.fillRect(lx-9,410,18,27);ctx.shadowBlur=0;ctx.fillStyle='#593d59';ctx.fillRect(lx-10,414,20,3);}
  // Floor gradient and perspective stripes.
  g=ctx.createLinearGradient(0,WORLD.floor,0,H);g.addColorStop(0,'#39334a');g.addColorStop(1,'#1a203a');ctx.fillStyle=g;ctx.fillRect(0,WORLD.floor,W,H-WORLD.floor);
  ctx.fillStyle='#a7e9d2';ctx.fillRect(0,WORLD.floor-3,W,4);ctx.fillStyle='#ff97ae';ctx.globalAlpha=.45;ctx.fillRect(0,WORLD.floor+9,W,2);ctx.globalAlpha=1;
  ctx.strokeStyle='rgba(138,220,229,.17)';ctx.lineWidth=1;for(let i=0;i<=20;i++){let x=i*80;ctx.beginPath();ctx.moveTo(x,WORLD.floor);ctx.lineTo(640+(x-640)*1.7,H);ctx.stroke();}
  for(const y of [576,614,658]){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
  // Stage name above floor.
  ctx.fillStyle='rgba(213,247,250,.25)';ctx.font='800 16px monospace';ctx.fillText('SECTOR 07 / NEON DOJO',35,502);
  ctx.restore();
}
function drawObjects(){
  const ctx=drawingContext;ctx.save();
  if(shake>0 && state==='playing')ctx.translate((Math.random()-.5)*shake*1.4,(Math.random()-.5)*shake*.9);
  for(const b of bolts){
    ctx.save();ctx.shadowBlur=24;ctx.shadowColor='#86e6fb';
    const rad=15+Math.sin(ambientTime*.3+b.phase)*3;let grad=ctx.createRadialGradient(b.x,b.y,2,b.x,b.y,rad);grad.addColorStop(0,'#ffffff');grad.addColorStop(.35,'#a4efff');grad.addColorStop(.72,'#59b5f6');grad.addColorStop(1,'rgba(100,195,250,0)');ctx.fillStyle=grad;ctx.beginPath();ctx.arc(b.x,b.y,rad,0,7);ctx.fill();ctx.globalAlpha=.6;ctx.fillStyle='#7cdaec';ctx.fillRect(b.x-b.vx*1.6,b.y-4,Math.abs(b.vx*1.8),8);ctx.restore();
    paintSheet('energy_blast',Math.floor(ambientTime/4)%6,b.x,b.y+40,1.10,1);
  }
  // Ground shadows and sprites.
  for(const enemy of enemies){
    if(enemy.dead && enemy.deathAge>=22)continue;
    let a=enemy.dead?1-enemy.deathAge/27:1;
    if(enemy.hitAge>0)enemy.hitAge-=state==='playing'?1:0;
    shadow(enemy.x,enemy.y,37);
    ctx.globalAlpha=Math.max(0,a);
    const config=ENEMY_KIND[enemy.type],m=META[config.strip];
    let frame=Math.floor(enemy.anim/(enemy.type==='robot'?9:7))%m.frames;
    if(enemy.dead)frame=0;
    paintSheet(config.strip,frame,enemy.x,enemy.y+ (enemy.dead?enemy.deathAge*1.1:0),config.scale,enemy.face);
    ctx.globalAlpha=1;
    if(enemy.hitAge>0 && !enemy.dead){ctx.fillStyle='#fff';ctx.globalAlpha=.3;ctx.fillRect(enemy.x-21,enemy.y-105,42,5);ctx.globalAlpha=1;}
    if(enemy.hp<enemy.maxHp && !enemy.dead){ctx.fillStyle='#18233c';ctx.fillRect(enemy.x-33,enemy.y-117,66,5);ctx.fillStyle='#a7f5ac';ctx.fillRect(enemy.x-32,enemy.y-116,64*(enemy.hp/enemy.maxHp),3);}
  }
  shadow(hero.x,hero.y,56);
  if(hero.invuln<=0 || Math.floor(ambientTime/4)%2===0){
    const f=FIGHTERS[fighter],action=hero.action,tag=f.prefix+'_'+action;
    const sheet=META[tag]?tag:f.prefix+'_idle';const m=META[sheet];let i;
    if(hero.actionLen>0){i=Math.min(m.frames-1,Math.floor(hero.actionAge/Math.max(1,hero.actionLen/m.frames)));}
    else{i=Math.floor(ambientTime/(action==='walk'?5:11))%m.frames;}
    paintSheet(sheet,i,hero.x,hero.y,f.scale,hero.face);
  }
  ctx.restore();
  if(state==='playing')drawAttackTrails();
}
function shadow(x,y,r){const ctx=drawingContext;ctx.save();ctx.globalAlpha=.27;ctx.fillStyle='#070b20';ctx.beginPath();ctx.ellipse(x,y+2,r,10,0,0,Math.PI*2);ctx.fill();ctx.restore();}
function paintSheet(name,frame,x,feet,s,face){
  const m=META[name],img=sheets[name];if(!img||!m)return;
  push();translate(x,feet);scale(s*face,s);
  image(img,-m.frameWidth/2,-m.frameHeight,m.frameWidth,m.frameHeight,frame*m.frameWidth,0,m.frameWidth,m.frameHeight);
  pop();
}
function drawAttackTrails(){
  const ctx=drawingContext;
  if((hero.action==='kick'||hero.action==='punch') && hero.actionLen>0){
    const s=hero.actionAge/hero.actionLen;
    if(s<.82){ctx.save();ctx.globalAlpha=(1-s)*.8;ctx.lineWidth=hero.action==='kick'?11:7;ctx.strokeStyle=hero.action==='kick'?'#f6c0f1':'#a3eeef';ctx.shadowBlur=20;ctx.shadowColor=ctx.strokeStyle;ctx.beginPath();ctx.arc(hero.x+hero.face*35,hero.y-101,hero.action==='kick'?75:57,hero.face===1?-.9:Math.PI-.1,hero.face===1?.7:Math.PI+1.7,hero.face!==1);ctx.stroke();ctx.restore();}
  }
  for(const p of particles){ctx.save();ctx.globalAlpha=Math.min(.95,Math.max(0,p.life/p.maxLife));ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y,p.size,p.size);ctx.restore();}
  for(const t of texts){ctx.save();ctx.globalAlpha=Math.max(0,Math.min(1,t.life/17));ctx.font='900 27px "Barlow Condensed", sans-serif';ctx.textAlign='center';ctx.lineWidth=4;ctx.strokeStyle='#1e2647';ctx.strokeText(t.label,t.x,t.y);ctx.fillStyle=t.color;ctx.fillText(t.label,t.x,t.y);ctx.restore();}
  if(combo>1){ctx.save();ctx.font='900 45px "Barlow Condensed"';ctx.textAlign='right';ctx.fillStyle='#befb91';ctx.fillText('×'+combo+' COMBO',1190,210);ctx.restore();}
}
function paintHUD(){
  document.getElementById('healthMeter').style.width=hero.health+'%';
  document.getElementById('hpText').textContent=Math.round(hero.health)+' / 100';
  document.getElementById('energyMeter').style.width=hero.energy+'%';
  document.getElementById('energyText').textContent=Math.round(hero.energy)+'%';
  document.getElementById('scoreText').textContent=String(score).padStart(6,'0');
  document.getElementById('waveText').textContent=String(wave).padStart(2,'0');
  document.getElementById('heroTitle').textContent=FIGHTERS[fighter].name;
}
function updateStatus(){document.getElementById('statusLabel').textContent=state==='playing'?'LIVE / FIGHT':state==='paused'?'GAME PAUSED':state==='over'?'GAME OVER':'READY TO PLAY';document.getElementById('pauseButton').textContent=state==='paused'?'▶ 繼續':'Ⅱ 暫停';}
function showMessage(title,description,button){let m=document.getElementById('centerMessage');m.classList.remove('is-hidden');m.querySelector('h2').innerHTML=title==='GAME OVER'?'GAME <em>OVER</em>':title==='PAUSED'?'GAME <em>PAUSED</em>':'READY, <em>FIGHT!</em>';m.querySelector('p').textContent=description;m.querySelector('button').innerHTML=button+' <span>↗</span>';currentMessage=title;}
function hideMessage(){document.getElementById('centerMessage').classList.add('is-hidden');currentMessage='';}
function pauseToggle(){if(state==='playing'){state='paused';showMessage('PAUSED','按 P 或點擊按鈕繼續遊戲。','繼續遊戲');}else if(state==='paused'){state='playing';hideMessage();}updateStatus();}
function chooseFighter(name){if(!FIGHTERS[name])return;fighter=name;document.querySelectorAll('.fighter').forEach(el=>{const chosen=el.dataset.fighter===name;el.classList.toggle('selected',chosen);el.setAttribute('aria-pressed',String(chosen));});hero.action='idle';hero.actionAge=0;hero.actionLen=0;paintHUD();}
function commandStart(){if(state==='paused'){pauseToggle();return;}beginGame();}
function handleAction(code){
  if(code==='Enter'){if(state!=='playing')commandStart();return;}
  if(code==='KeyP'){pauseToggle();return;}
  if(code==='KeyR'){beginGame();return;}
  if(code==='KeyM'){toggleSound();return;}
  if(code==='Digit1'){chooseFighter('lee');return;}
  if(code==='Digit2'){chooseFighter('chun');return;}
  if(code==='ArrowUp'||code==='KeyW')jump();
  if(code==='KeyZ')attack('punch');
  if(code==='KeyX')attack('kick');
  if(code==='Space')attack('special');
}
function bindUI(){
  window.addEventListener('keydown',e=>{
    const blocked=['ArrowLeft','ArrowRight','ArrowUp','Space','ArrowDown'];if(blocked.includes(e.code))e.preventDefault();
    if(!keys[e.code])handleAction(e.code);
    keys[e.code]=true;
  },{passive:false});
  window.addEventListener('keyup',e=>{keys[e.code]=false;});
  window.addEventListener('blur',()=>{keys={};});
  document.getElementById('startButton').addEventListener('click',commandStart);
  document.getElementById('pauseButton').addEventListener('click',pauseToggle);
  document.getElementById('soundButton').addEventListener('click',toggleSound);
  document.getElementById('helpButton').addEventListener('click',()=>document.getElementById('controls').scrollIntoView({behavior:'smooth'}));
  document.querySelectorAll('.fighter').forEach(el=>el.addEventListener('click',()=>chooseFighter(el.dataset.fighter)));
  const touchMap=[['btnLeft','ArrowLeft'],['btnRight','ArrowRight'],['btnJump','ArrowUp'],['btnPunch','KeyZ'],['btnKick','KeyX'],['btnSpecial','Space']];
  for(const [id,code] of touchMap){const el=document.getElementById(id);
    el.addEventListener('pointerdown',e=>{e.preventDefault();el.setPointerCapture(e.pointerId);keys[code]=true;handleAction(code);el.classList.add('pressed');});
    const stop=e=>{e.preventDefault();keys[code]=false;el.classList.remove('pressed');};el.addEventListener('pointerup',stop);el.addEventListener('pointercancel',stop);
  }
}
function toggleSound(){soundEnabled=!soundEnabled;document.getElementById('soundButton').textContent=soundEnabled?'♫ 音樂：開':'♫ 音樂：關';document.getElementById('soundButton').setAttribute('aria-pressed',String(soundEnabled));if(bgm){if(soundEnabled){bgm.play().catch(()=>{soundEnabled=false;document.getElementById('soundButton').textContent='♫ 音樂：關';});}else{bgm.pause();}}}
function beep(type){if(!soundEnabled)return;try{
  audioCtx=audioCtx||new(window.AudioContext||window.webkitAudioContext)();if(audioCtx.state==='suspended')audioCtx.resume();const o=audioCtx.createOscillator(),v=audioCtx.createGain(),now=audioCtx.currentTime;
  const tones={start:[420,680,.18],jump:[340,490,.13],punch:[185,95,.09],kick:[220,88,.15],special:[680,120,.22],hurt:[150,70,.2],ko:[580,890,.2],over:[320,70,.4]};let a=tones[type]||tones.punch;
  o.type=type==='special'?'sawtooth':'triangle';o.frequency.setValueAtTime(a[0],now);o.frequency.exponentialRampToValueAtTime(a[1],now+a[2]);v.gain.setValueAtTime(.1,now);v.gain.exponentialRampToValueAtTime(.001,now+a[2]);o.connect(v).connect(audioCtx.destination);o.start(now);o.stop(now+a[2]);
}catch(err){console.warn('Sound disabled:',err);}}
