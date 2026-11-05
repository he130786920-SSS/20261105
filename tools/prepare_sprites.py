"""Reproduce sprite preprocessing with Pillow (not an ASU/SpriteTracer GUI export).
Run: python tools/prepare_sprites.py
User-provided originals must remain in assets/originals/.
All combined strips have fixed frame dimensions and transparent backgrounds.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets'/'originals'
DEST=ROOT/'assets'/'sheets'
DEST.mkdir(parents=True,exist_ok=True)

# (filename, transparent key, source y interval, explicit x-intervals, frame width/height)
LEE='Lee Jinkang (1).png'
CHUN='Chun-Li(1).png'
CM='CM_Enemies.png'
ASSETS = {
  'lee_idle':     (LEE, (255,0,255), (9,98),   [(6,68),(80,141),(150,207)], (150,124)),
  'lee_walk':     (LEE, (255,0,255), (107,206),[(4,57),(67,119),(126,179),(184,237),(242,305),(309,372)], (150,124)),
  'lee_jump':     (LEE, (255,0,255), (208,332),[(4,57),(64,116),(122,175),(211,267),(273,324),(330,384)], (150,132)),
  'lee_punch':    (LEE, (255,0,255), (356,452),[(10,65),(72,159),(166,223),(265,332),(337,389),(396,506),(515,567)], (150,124)),
  'lee_kick':     (LEE, (255,0,255), (666,757),[(2,54),(57,149),(153,240),(249,340),(344,458),(462,580)], (150,124)),
  'lee_hurt':     (LEE, (255,0,255), (1488,1578),[(5,70),(71,148)], (150,124)),
  'chun_idle':    (CHUN,(255,174,201), (4,40), [(3,22),(21,40),(39,59),(58,78),(77,97),(97,116),(117,136),(137,156),(155,175),(174,194)], (52,56)),
  'chun_walk':    (CHUN,(255,174,201), (43,80),[(5,25),(24,44),(44,64),(65,84),(86,105),(107,126),(127,146),(146,166)], (52,56)),
  'chun_jump':    (CHUN,(255,174,201), (84,118),[(7,35),(36,64),(65,95),(96,124),(126,156),(158,187)], (52,56)),
  'chun_punch':   (CHUN,(255,174,201), (162,195),[(5,35),(35,64),(66,94),(93,122),(121,150),(151,180)], (52,56)),
  'chun_kick':    (CHUN,(255,174,201), (200,232),[(8,37),(38,66),(67,96),(97,124),(127,155),(155,183)], (52,56)),
  'chun_hurt':    (CHUN,(255,174,201), (1622,1653),[(4,35),(36,67)], (52,56)),
  'robot_walk':  (CM,  (104,144,168),(72,129),[(665,719),(744,800),(821,879),(890,950),(977,1030),(1055,1110),(1134,1192),(1222,1285)], (76,76)),
  'robot_idle':  (CM,  (104,144,168),(191,254),[(665,719),(744,800),(821,879),(890,950),(977,1030),(1055,1110),(1134,1192),(1222,1285)], (76,76)),
}

def cut_rgba(source, region, bg):
    im=source.crop(region).convert('RGBA')
    px=im.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=px[x,y]
            if (r,g,b)==bg:
                px[x,y]=(0,0,0,0)
    bb=im.getbbox()
    return im.crop(bb) if bb else Image.new('RGBA',(1,1))

def fit_tile(im,size, foot_pad=3):
    w,h=size
    allowed_w=w-6; allowed_h=h-7
    if im.width>allowed_w or im.height>allowed_h:
        ratio=min(allowed_w/im.width,allowed_h/im.height)
        im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio))),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',size,(0,0,0,0))
    tile.alpha_composite(im,((w-im.width)//2,h-foot_pad-im.height))
    return tile

def col_runs(image):
    active=[]; inside=False
    for x in range(image.width):
        if image.crop((x,0,x+1,image.height)).getbbox() is not None:
            if not inside: start=x;inside=True
        elif inside:
            active.append((start,x));inside=False
    if inside:active.append((start,image.width))
    return active

# PNGs with transparent BG already consist of exactly 8 separate horizontal sprites.
for name,key in [('monkey_walk','1_all.png'),('ninja_attack','2_all.png')]:
    im=Image.open(SRC/key).convert('RGBA')
    runs=col_runs(im)
    if len(runs)!=8:raise ValueError(f'{key} expected 8 alpha-separated sprites, got {runs}')
    frames=[]
    for x0,x1 in runs:
        crop=im.crop((x0,0,x1,im.height))
        bb=crop.getbbox()
        crop=crop.crop(bb) if bb else crop
        frames.append(fit_tile(crop,(72,76)))
    out=Image.new('RGBA',(72*8,76))
    for i,tile in enumerate(frames):out.alpha_composite(tile,(i*72,0))
    out.save(DEST/f'{name}.png',optimize=True)

result={'monkey_walk':{'source':'1_all.png','frameWidth':72,'frameHeight':76,'frames':8,'width':576,'height':76},'ninja_attack':{'source':'2_all.png','frameWidth':72,'frameHeight':76,'frames':8,'width':576,'height':76}}

for name,(file,bg,(y0,y1),xs,size) in ASSETS.items():
    im=Image.open(SRC/file).convert('RGBA')
    frames=[]
    for x0,x1 in xs:
        extracted=cut_rgba(im,(x0,y0,x1,y1),bg)
        frames.append(fit_tile(extracted,size))
    width=size[0]*len(frames)
    combined=Image.new('RGBA',(width,size[1]))
    for i,frame in enumerate(frames):combined.alpha_composite(frame,(i*size[0],0))
    combined.save(DEST/f'{name}.png',optimize=True)
    result[name]={'source':file,'frameWidth':size[0],'frameHeight':size[1],'frames':len(frames),'width':width,'height':size[1]}

# Original six-frame glowing orb animation for the Space-key special move.
from PIL import ImageDraw
orbw,orbh,orbn=64,64,6
orb_strip=Image.new('RGBA',(orbw*orbn,orbh),(0,0,0,0))
for i in range(orbn):
    frame=Image.new('RGBA',(orbw,orbh),(0,0,0,0)); dr=ImageDraw.Draw(frame,'RGBA')
    r=14+(i%3)*3
    dr.ellipse((32-r-7,32-r-7,32+r+7,32+r+7),fill=(74,166,242,38))
    dr.ellipse((32-r-3,32-r-3,32+r+3,32+r+3),fill=(73,204,249,105))
    dr.ellipse((32-r,32-r,32+r,32+r),fill=(106,221,250,225))
    dr.ellipse((26,26,38,38),fill=(241,253,255,255))
    for a,b in [(32,2),(2,32),(62,32),(32,62)]:
        dr.line((32,32,a,b),fill=(147,239,252,170),width=2)
    orb_strip.alpha_composite(frame,(i*orbw,0))
orb_strip.save(DEST/'energy_blast.png',optimize=True)
result['energy_blast']={'source':'原創程式繪製特效','frameWidth':64,'frameHeight':64,'frames':6,'width':384,'height':64}

# Assignment-style folders in addition to the web-runtime sprite inventory.
# Each action folder retains 0.png..n.png and one merged action strip.
import shutil
FOLDERS={
 '1':{'stop':'lee_idle','walk':'lee_walk','run':'lee_walk','jump':'lee_jump','push':'lee_kick','punch':'lee_punch','hurt':'lee_hurt','to':'energy_blast'},
 '2':{'stop':'chun_idle','walk':'chun_walk','jump':'chun_jump','push':'chun_kick','punch':'chun_punch','hurt':'chun_hurt'},
 '3':{'walk':'monkey_walk'},'4':{'push':'ninja_attack'},'5':{'walk':'robot_walk','stop':'robot_idle'}
}
for role,actions in FOLDERS.items():
    for action,sprite in actions.items():
        m=result[sprite];outdir=ROOT/role/action;outdir.mkdir(parents=True,exist_ok=True)
        sheet=Image.open(DEST/f'{sprite}.png').convert('RGBA')
        sheet.save(outdir/f'{action}.png',optimize=True)
        for i in range(m['frames']):
            sheet.crop((m['frameWidth']*i,0,m['frameWidth']*(i+1),m['frameHeight'])).save(outdir/f'{i}.png',optimize=True)

(ROOT/'assets'/'sprite-data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('Output',len(result),'sprite strips')
for k,v in result.items():print(k,v['width'],v['height'],v['frames'])
