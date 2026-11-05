"""Generate explanatory diagrams from real image files (not screenshots of ASU/SpriteTracer GUIs)."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
P=Path(__file__).resolve().parents[1];OUT=P/'docs'/'screenshots'; OUT.mkdir(exist_ok=True)
D=json.loads((P/'assets'/'sprite-data.json').read_text())
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try:
 f12=ImageFont.truetype(font,16);f22=ImageFont.truetype(font,24)
except: f12=ImageFont.load_default();f22=f12

def draw_checker(img,at=(0,0),tile=12):
 for x in range(0,img.width,tile):
  for y in range(0,img.height,tile):
   c=(53,61,79) if (x//tile+y//tile)%2 else (78,89,106)
   ImageDraw.Draw(img).rectangle((x,y,x+tile-1,y+tile-1),fill=c)

# Original image overview with dimensions and honest file origin.
canvas=Image.new('RGB',(1260,950),(19,24,42));dr=ImageDraw.Draw(canvas)
dr.text((35,22),'UPLOADED SOURCE SPRITES  /  ORIGINAL MATERIALS',font=f22,fill=(185,250,158))
orig=['1_all.png','2_all.png','Lee Jinkang (1).png','Chun-Li(1).png','CM_Enemies.png']
for i,n in enumerate(orig):
 img=Image.open(P/'assets/originals'/n).convert('RGBA');x=35+(i%2)*620;y=85+(i//2)*285
 thumb=img.copy();thumb.thumbnail((560,210),Image.Resampling.NEAREST)
 box=Image.new('RGB',(575,218),(45,52,76));box.paste(thumb,((575-thumb.width)//2,(218-thumb.height)//2),thumb)
 canvas.paste(box,(x,y));dr.text((x,y+225),f'{n}   [{img.width} x {img.height}]',font=f12,fill=(232,236,246))
canvas.save(OUT/'originals-overview.png')

# Red outlines are a visualization of the algorithmic frame bounds; not ASU UI.
lee=Image.open(P/'assets/originals'/'Lee Jinkang (1).png').convert('RGBA')
panel=Image.new('RGB',(960,390),(26,32,48));d=ImageDraw.Draw(panel)
d.text((20,15),'ILLUSTRATED SOURCE FRAME SELECTION  /  NOT AN ASU SCREENSHOT',font=f12,fill=(201,237,168))
region=lee.crop((0,107,390,206));region=region.resize((780,198),Image.Resampling.NEAREST)
panel.paste(region,(55,65))
xs=[(4,57),(67,119),(126,179),(184,237),(242,305),(309,372)]
for i,(x0,x1) in enumerate(xs):
 d.rectangle((55+x0*2,65,55+x1*2,262),outline=(255,92,103),width=3)
 d.text((56+x0*2,271),str(i),font=f12,fill='white')
d.text((22,325),'6 source regions  ->  trim opaque pixels  ->  center/bottom align',font=f12,fill=(218,223,237))
panel.save(OUT/'cut-regions-illustration.png')

# Balance & combine visuals from the actual resulting sprites.
NAMES=['lee_idle','lee_walk','lee_jump','lee_punch','lee_kick','chun_idle','monkey_walk','ninja_attack','robot_walk']
out=Image.new('RGB',(1280,len(NAMES)*126+70),(23,28,46));d=ImageDraw.Draw(out)
d.text((20,17),'COMBINED HORIZONTAL SPRITESHEETS  /  FIXED FRAME WIDTH',font=f22,fill=(193,253,153))
for r,name in enumerate(NAMES):
 meta=D[name];strip=Image.open(P/'assets/sheets'/f'{name}.png').convert('RGBA')
 h=85; scale=min(100/(meta['frameWidth']),h/(meta['frameHeight']))
 d.text((20,r*126+70),name,font=f12,fill=(235,239,255))
 d.text((20,r*126+95),f"{meta['frames']} frames  {meta['width']} x {meta['height']}",font=f12,fill=(142,170,201))
 for i in range(min(meta['frames'],8)):
  img=strip.crop((i*meta['frameWidth'],0,(i+1)*meta['frameWidth'],meta['frameHeight']))
  img=img.resize((max(1,int(img.width*scale)),max(1,int(img.height*scale))),Image.Resampling.NEAREST)
  x=295+i*120; y=r*126+62
  d.rectangle((x-2,y-2,x+105,y+96),fill=(46,56,75),outline=(77,90,111),width=1)
  out.paste(img,(x+(100-img.width)//2,y),img)
  d.text((x+5,y+82),f'#{i}',font=f12,fill=(212,221,238))
out.save(OUT/'combine-results.png')

# Transparency example from a real output frame.
strip=Image.open(P/'assets/sheets/lee_idle.png').convert('RGBA');m=D['lee_idle']
frame=strip.crop((0,0,m['frameWidth'],m['frameHeight'])).resize((300,248),Image.Resampling.NEAREST)
transparent=Image.new('RGB',(650,310));draw_checker(transparent,tile=20)
transparent.paste(frame,(30,32),frame);dt=ImageDraw.Draw(transparent)
dt.text((366,95),'ALPHA = 0',font=f22,fill=(207,248,165));dt.text((366,135),'RGBA / PNG',font=f22,fill=(232,239,255));dt.text((366,177),'No magenta matte',font=f12,fill=(200,207,222))
transparent.save(OUT/'transparent-result.png')

# Actual folder tree textual schematic, drawn by code, not falsely described as a VS Code screenshot.
tree='''pixel-rift-dojo/
  index.html
  sketch.js
  style.css
  assets/
    originals/  (five uploaded PNG files)
    sheets/     (16 combined sprite strips)
    portraits/  (two profile PNG files)
    audio/dojo-loop.wav
    sprite-data.json
  docs/
    *.md   + screenshots/
  tools/
    prepare_sprites.py
    make_documentation_images.py
  vendor/p5-local.js
  .vscode/settings.json
  README.md  /  .nojekyll'''
lines=tree.split('\n');out=Image.new('RGB',(920,700),(20,28,45));dr=ImageDraw.Draw(out)
dr.text((33,18),'PROJECT DIRECTORY SCHEMATIC  /  GENERATED FROM PROJECT STRUCTURE',font=f12,fill=(195,250,160))
for i,line in enumerate(lines):dr.text((52,66+i*34),line,font=f12,fill=(221,230,248))
out.save(OUT/'project-tree.png')
print('Created documentation illustrations')
