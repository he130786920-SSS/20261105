"""Generate a single-file, double-clickable playable preview.
The submission's index.html still runs actual p5.js from CDN. This offline preview
uses the included limited compatible renderer and embeds user-supplied sprites.
"""
from pathlib import Path
import base64,json
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text(encoding='utf8')
css=(root/'style.css').read_text(encoding='utf8')
css=css.replace("@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=Noto+Sans+TC:wght@400;500;600;700;800;900&display=swap');",'')
shim=(root/'vendor/p5-local.js').read_text(encoding='utf8')
sketch=(root/'sketch.js').read_text(encoding='utf8')
assets={}
for p in list((root/'assets/sheets').glob('*.png'))+list((root/'assets/portraits').glob('*.png')):
 assets[str(p.relative_to(root)).replace('\\','/')]='data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
for path,uri in assets.items():
 if path.startswith('assets/portraits/'):
  html=html.replace('src="'+path+'"','src="'+uri+'"')
sketch=sketch.replace("loadImage('assets/sheets/'+name+'.png')","loadImage(window.__sprites['assets/sheets/'+name+'.png'])")
sketch=sketch.replace("new Audio('assets/audio/dojo-loop.wav')","new Audio(window.__offlineAudio)")
audio='data:audio/wav;base64,'+base64.b64encode((root/'assets/audio/dojo-loop.wav').read_bytes()).decode('ascii')
inject='<script>window.__sprites='+json.dumps({k:v for k,v in assets.items() if 'sheets/' in k})+';window.__offlineAudio='+json.dumps(audio)+';</script>'
html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
html=html.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>','')
html=html.replace('<script src="vendor/p5-local.js"></script>',inject+'<script>'+shim+'</script>')
html=html.replace('<script src="sketch.js"></script>','<script>'+sketch+'</script>')
html=html.replace('</footer>', '</footer>')
html=html.replace('© 2026</span></footer>', '離線預覽版 · 正式版使用 p5.js CDN</span></footer>')
html=html.replace('<title>PIXEL RIFT｜像素時空道場</title>', '<title>PIXEL RIFT｜離線可玩預覽</title>')
(root/'offline-preview.html').write_text(html,encoding='utf8')
print('single-file offline preview size',len(html),'characters')
