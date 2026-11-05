"""Regenerate the two assignment Markdown documents from the built project.
Honesty requirements: do not invent names, original source URLs, tool GUI screenshots,
user-operated VS Code actions, or GitHub deployment links.
"""
from pathlib import Path
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'assets/sprite-data.json').read_text())
DOC=ROOT/'docs';DOC.mkdir(exist_ok=True)
ORIGINALS=['1_all.png','2_all.png','Chun-Li(1).png','CM_Enemies.png','Lee Jinkang (1).png']
sourceinfo=[]
for file in ORIGINALS:
    im=Image.open(ROOT/'assets/originals'/file)
    sourceinfo.append((file,im.width,im.height))

# The first provided MD is an explanatory handout, not a worksheet.
# Preserve it and append factual evidence of implementation.
source_handout=Path('/mnt/data/ASU與SpriteTracer_切圖合併_完整教材.md.md')
if source_handout.exists():
    handout=source_handout.read_text(encoding='utf8').rstrip()
else:
    handout='# ASU 與 SpriteTracer 切圖合併：完整教材\n\n原始講義未在重新產生文件時找到，請以課堂上傳檔案為準。'

handout_extra='''

---

# 附錄 A｜本次角色動畫作業實作結果（2026-11-05）

> **重要誠實註記：**本附錄是此次上傳素材的實際處理紀錄。ASU_19.zip 與 SpriteTracer6.zip 為 Windows `.exe` 程式，本次執行環境無法操作其 GUI，因此**沒有聲稱使用 ASU 的 Export Selected 或 SpriteTracer 的 Balance／Combine 按鈕**，也沒有偽造這兩套軟體的畫面。實作使用 Pillow 依相同原理「去背→分格→置中／腳底對齊→橫向合併」，由 `tools/prepare_sprites.py` 可重現。到 Windows 電腦操作後可補上真正的 GUI 截圖。

## A-1. 作品介紹

作品：**PIXEL RIFT｜像素時空道場**。以 `Lee Jinkang (1).png` 為主角一、`Chun-Li(1).png` 為主角二，`1_all.png`、`2_all.png`、`CM_Enemies.png` 為敵方角色；程式化產生的 `energy_blast.png` 是空白鍵施放的特效。使用 p5.js 精靈圖切格、原創 16 秒 WAV 循環配樂、鍵盤控制、碰撞與計分。

![五張來源圖的概覽](screenshots/originals-overview.png)

**素材來源：**由作業提出者在本次對話直接提供，原始下載網址及授權資訊未提供；公開網站前應確認素材可公開使用。

| 上傳素材 | 原圖寬 × 高 | 背景處理 |
|---|---:|---|
'''
for fn,w,h in sourceinfo:
    color='已透明，利用 alpha 分割' if fn in ('1_all.png','2_all.png') else ('純洋紅色 #FF00FF → 透明' if fn.startswith('Lee ') else ('粉紅色 #FFAEC9 → 透明' if fn.startswith('Chun-') else '藍灰色 #6890A8 → 透明'))
    handout_extra+=f'| `{fn}` | {w} × {h} | {color} |\n'
handout_extra+='''
## A-2. 與教材對照：ASU 切圖

- 教材的 **依序選取→匯出 0.png、1.png…**：本次由 `prepare_sprites.py` 依來源圖上的實際動作區塊，依序輸出 `1/stop/0.png`、`1/stop/1.png` 等。
- 教材的 **Split／Cut Mode**：本次沒有在 ASU 視窗手動操作；程式以來源座標指定每格範圍，避免相鄰影格混在一起。
- 教材的 **一個動作一個資料夾**：已建立 `1/stop`、`1/walk`、`1/run`、`1/jump`、`1/push`、`1/punch`、`1/to`；另外有 `2/`（春麗）、`3/`（猴）、`4/`（綠猴）、`5/`（藍猴）。`1/run` 目前沿用 `1/walk` 影格，**不是聲稱另外取得跑步原圖**。

![來源影格選取說明圖，非 ASU 視窗截圖](screenshots/cut-regions-illustration.png)

## A-3. 與教材對照：SpriteTracer 合併

- **Settings→Transparent** 的等效結果：所有輸出 PNG 背景 alpha=0，沒有色底。
- **Balance→center** 的等效結果：每格置中、腳底對齊，使用固定畫格寬高。
- **Combine** 的等效結果：同一動作的小圖從左至右排列成長條圖。合併後存於 `assets/sheets/` 和課堂習慣的 `1/stop/stop.png` 等路徑。

![透明 PNG 範例（不是軟體視窗）](screenshots/transparent-result.png)

![各種動作合併後的長條圖](screenshots/combine-results.png)

## A-4. 最重要的結果：實際寬、高與張數

| 角色／動作 | p5.js 讀圖路徑 | 總寬 | 高 | 張數 | 單格寬 |
|---|---|---:|---:|---:|---:|
'''
for name,m in D.items():
    handout_extra+=f'| {name} | `assets/sheets/{name}.png` | {m["width"]} | {m["height"]} | {m["frames"]} | {m["frameWidth"]} |\n'
handout_extra+='''
全部長條圖符合 `總寬 = 單格寬 × 張數`，且單格寬均為整數。程式使用 `image(img, dx, dy, dw, dh, index*frameWidth, 0, frameWidth, frameHeight)` 擷取影格；詳細設定請見 `assets/sprite-data.json`。

## A-5. 程式與測試摘要

- 檔案：`index.html`、`style.css`、`sketch.js`，圖片及聲音在 `assets/`。
- 功能：左右移動、跳躍、Z 拳擊、X 踢擊、空白鍵遠距離特效、Shift 衝刺、1/2 切換主角、P 暫停、R 重來、M 音樂開關、敵人生命值與波次計分。
- 配樂：`assets/audio/dojo-loop.wav`（本專案以程式合成之原創旋律）；瀏覽器要求使用者點擊後才播放。
- 在隔離式 Chromium 測試環境使用 **相同 sketch.js 及真實圖片素材、以本地相容渲染器替代無法連線的外部 p5.js CDN** 進行操作測試；啟動、移動、攻擊、換角、暫停均通過，未發現 JavaScript 執行錯誤。**線上正式 p5.js CDN 版本及 GitHub Pages 尚未部署測試。**

![網站首頁實測畫面](screenshots/actual-home.png)

![遊戲站立／待機](screenshots/final-stand.png)
![遊戲移動](screenshots/final-walk.png)
![遊戲能量攻擊](screenshots/final-attack.png)

## A-6. 尚需自行完成或確認的事項

1. 依學校要求，在 Windows 電腦實際打開 ASU 與 SpriteTracer，補上工具內的切圖紅框、透明設定、Balance 前後等**真實操作畫面**；目前文件使用的是明確標示的演算法示意與實際輸出圖，不能取代 GUI 操作證明。
2. 補上姓名、學號、素材原始網址及授權資訊；由使用者確認 Windows 的 VS Code 安裝情形。
3. 使用自己的 GitHub 帳號建立 Repository、上傳本專案並在 Settings → Pages 啟用 `main / (root)`，才能得到**真實可開啟的** GitHub 與 GitHub Pages 網址；本附錄沒有預先填入虛構連結。
'''
(DOC/'ASU與SpriteTracer_切圖合併_完整教材.md.md').write_text(handout+'\n'+handout_extra,encoding='utf8')

readme='''# PIXEL RIFT｜像素時空道場

使用五張上傳的角色素材、p5.js 動畫與原創音樂製作的單頁街機格鬥網頁。手機可用畫面底部觸控鍵，桌面用鍵盤。

![首頁預覽](docs/screenshots/actual-home.png)

## 啟動方式（VS Code）

1. 解壓縮後，開啟 VS Code → **檔案 → 開啟資料夾** → 選擇 `pixel-rift-dojo`。
2. 建議安裝 **Live Server** 擴充功能；對 `index.html` 按右鍵 → **Open with Live Server**。
3. 開啟瀏覽器看遊戲。如果沒有網路，本專案 `vendor/p5-local.js` 可在官方 p5.js CDN 無法載入時，提供本作品需要的簡化繪圖介面；正常上線則優先使用官方 p5.js 1.9.0。
4. 按「開始遊戲」或 Enter。按「♫ 音樂」啟動原創配樂。

> 雙擊 HTML 開啟可能受到瀏覽器本機圖片權限限制，請使用 Live Server 或 `python -m http.server 5500`。

## 遊戲按鍵

| 按鍵 | 功能 |
|---|---|
| ← / →、A / D | 左右移動 |
| ↑ / W | 跳躍 |
| Z | 拳擊 |
| X | 踢擊 |
| Space | 能量波（消耗 22 能量） |
| Shift | 衝刺 |
| 1 / 2 | 切換李振康／春麗 |
| P | 暫停／恢復 |
| R | 重新開始 |
| M | 開關背景音樂 |

## 資料夾

- `assets/originals/`：五張用戶提供的來源圖片。
- `assets/sheets/`：17 張含透明背景的橫向精靈圖。
- `1/`～`5/`：老師教材風格的角色／動作資料夾，每個動作有 `0.png` 開始的分格，以及同名合併長條圖。
- `assets/sprite-data.json`：每個動作的長條總寬、高、影格數、單格寬。
- `assets/audio/dojo-loop.wav`：自行程式合成的 16 秒循環音樂。
- `docs/`：**兩份已處理 MD**、切圖成果說明圖、實際網頁測試截圖。
- `tools/prepare_sprites.py`：用 Pillow 重現本次切圖合併流程；**不是 ASU 或 SpriteTracer 本身**。
- `vendor/p5-local.js`：離線簡化相容繪圖器；正式有網路時優先使用 CDN 的 p5.js。

## 發布到 GitHub Pages

**目前還未使用你的帳號建立 Repository，也尚未取得公開網址。**

1. 登入 GitHub，點右上角 **+ → New repository**，例如設定 `pixel-rift-dojo`，設為 Public（公開前確認素材授權）。
2. 將專案**資料夾內所有檔案**上傳至該 Repository 根目錄，包括 `.nojekyll`。不要把整份 ZIP 當成唯一檔案上傳。
3. 到 Repository → **Settings → Pages**，在 **Build and deployment** 選 **Deploy from a branch**，Branch 設為 `main`、資料夾為 `/(root)`，按 Save。
4. 等 GitHub Pages 顯示正式網址，再把它填進 `docs/學生版_角色動畫製作紀錄_已填寫.md` 的基本資料欄及繳交確認欄。
5. 常見網址格式：`https://你的帳號.github.io/pixel-rift-dojo/`（**這只是格式示例，不是已發布的真實網址**）。

## 作業、授權與實作證明

五張角色圖是課堂作業參與者提供，下載來源／使用權利尚待確認；公開前請確認作者、授權與標示方式。原始素材的部分圖片包含遊戲作品／擷取者名稱，不代表擁有公開再利用授權。音樂與新畫面佈景為本次專案原創。

這個製作環境無法操作 `ASU_19.exe`、`SpriteTracer.exe` 的 Windows 介面。本專案用 Pillow 處理實際素材，MD 裡把**工具 GUI 螢幕截圖列為待補**，沒有冒充使用老師的工具。程式功能已於隔離 Chromium 透過離線相容渲染器測試；公開網站的官方 p5.js 版本，仍需要 GitHub Pages 上線後確認。
'''
(ROOT/'README.md').write_text(readme,encoding='utf8')

source_rows='\n'.join('| `{}` | {} × {} | 由使用者於本對話上傳（原始網址未提供） |'.format(f,w,h) for f,w,h in sourceinfo)
main_rows='\n'.join(f'| {name} | `assets/sheets/{name}.png` | {v["width"]} | {v["height"]} | {v["frames"]} | {v["frameWidth"]} |' for name,v in D.items())
source_code=(ROOT/'sketch.js').read_text(encoding='utf8').rstrip()

student=f'''# 角色動畫製作紀錄（學生版・已依實際製作填寫）

> 對應課堂五部影片：找精靈圖 → ASU 切圖 → SpriteTracer 合併 → AI／VS Code 製作 p5.js 動畫 → 加入音樂。\
> **資料真實性說明：**以下填入已製作及已驗證的內容；若為來源不明、姓名學號、Windows 工具 GUI 截圖、GitHub 真實公開網址，保留「待補／待確認」，不虛構。此次使用 Python／Pillow 依教材原理完成切圖，**不是在 Windows ASU／SpriteTracer 視窗點擊完成**。

---

## 0. 基本資料

| 項目 | 填寫 |
|---|---|
| 姓名 | **待本人填寫**（未提供） |
| 學號 | **待本人填寫**（未提供） |
| 日期 | 2026-11-05 |
| 我的角色名稱／來源網站 | 李振康（Lee Jinkang）、春麗（Chun-Li）、褐猴／綠猴／藍猴敵人；五張素材均由本人提供，原始下載網址**待補** |
| 使用的 AI 工具 | ChatGPT（GPT-6）；未宣稱使用 Gemini／Copilot |
| GitHub Repository 網址 | **尚未建立／待本人授權發布後填寫** |
| GitHub Pages 網址 | **尚未發布／待本人授權發布後填寫** |
| 專案名稱 | **PIXEL RIFT｜像素時空道場** |

## 1. 我選的精靈圖

![五張原圖概覽](screenshots/originals-overview.png)

**為什麼選這些角色？** 李振康有待機、移動、跳躍、拳擊與踢擊的連續影格，可作為主角；春麗可做第二位可切換角色；褐猴、綠猴及藍猴有連續動作，適合作為對戰敵人，能在同一個網站呈現多角色互動。

| 原始素材 | 原圖尺寸 | 圖片來源 |
|---|---|---|
{source_rows}

**來源說明：**這些圖像是本次作業提供的檔案，未提供來源網站 URL，無法負責任地填成某一個網址。部分原圖右下角或圖面內有來源文字，公開網站前仍應另行確認原作者與授權。

## 2. ASU 切圖紀錄

### 2-1 資料夾結構

依課堂概念建立角色／動作資料夾；`0.png`、`1.png` 代表每個動作的連續格，`stop.png` 等代表合併長條圖。

```text
pixel-rift-dojo/
├─ 1/                        李振康
│  ├─ stop/   0.png 1.png 2.png stop.png
│  ├─ walk/   0.png ... 5.png walk.png
│  ├─ run/    與 walk 共用相同來源影格（不是新跑步原圖）
│  ├─ jump/   0.png ... 5.png jump.png
│  ├─ punch/  0.png ... 6.png punch.png
│  ├─ push/   0.png ... 5.png push.png
│  └─ to/     0.png ... 5.png to.png（原創能量波）
├─ 2/                        春麗：stop / walk / jump / punch / push
├─ 3/walk/                   褐猴（8 格）
├─ 4/push/                   綠猴（8 格）
├─ 5/stop/、5/walk/           藍猴（各 8 格）
├─ assets/originals/         五張原圖
├─ assets/sheets/            網頁使用的 17 張長條圖
└─ assets/sprite-data.json   實際尺寸及影格數
```

![實際專案資料結構示意圖（不是 VS Code 截圖）](screenshots/project-tree.png)

### 2-2 ASU 畫面／切圖方法

**實際執行情形：**有提供 `ASU_19.zip`，但此次環境無法執行 Windows GUI，故沒有 ASU 自動紅框、Split 按鈕或 Export Selected 的真實截圖。本次以 `tools/prepare_sprites.py` 讀取原圖、辨識透明／純色背景、按照來源動作座標選取各格、依序輸出每個動作的 `0.png ... n.png`。

**Split（剪刀）有沒有使用？** 沒有在 ASU 操作。改用程式手動設定分割範圍，特別處理 `Lee Jinkang (1).png` 的不等寬格子及小圖與大圖混排情況；避免人物左右相黏。

![原圖上標示分格範圍的說明圖，非 ASU GUI 截圖](screenshots/cut-regions-illustration.png)

> 若老師要求 ASU 工具視窗截圖：**待在 Windows 真的操作後補上**，目前這張只是依源圖畫出的切割示意。

### 2-3 每個動作切了幾張

| 角色／動作 | 資料夾 | 張數 | 順序 |
|---|---|---:|---|
| 李振康 stop | `1/stop/` | 3 | ✓ 由左至右 |
| 李振康 walk | `1/walk/` | 6 | ✓ 由左至右 |
| 李振康 run | `1/run/` | 6 | ✓ 沿用 walk，非獨立跑步素材 |
| 李振康 jump | `1/jump/` | 6 | ✓ 由左至右 |
| 李振康 punch | `1/punch/` | 7 | ✓ 由左至右 |
| 李振康 push／踢擊 | `1/push/` | 6 | ✓ 由左至右 |
| 能量特效 to | `1/to/` | 6 | ✓ 程式原創特效 |
| 春麗 stop／walk／jump／punch／push | `2/` 各動作資料夾 | 10／8／6／6／6 | ✓ 依來源圖片排序 |
| 褐猴／綠猴／藍猴 | `3/`、`4/`、`5/` | 8／8／8 | ✓ 依來源圖片排序 |

![合併結果，顯示按動作排列的影格](screenshots/combine-results.png)

## 3. SpriteTracer 合併紀錄

> 教材要求 **Transparent → Open → Balance → Combine → Save**；本次以 Pillow 做出等效產物，不冒充 SpriteTracer UI 操作。

### 3-1 每個動作的合併過程

**設定透明：** `1_all.png` 和 `2_all.png` 原本已是 RGBA 透明；李振康 `#FF00FF`、春麗 `#FFAEC9`、敵人圖 `#6890A8` 的純色背景設為 Alpha=0。結果下方以棋盤背景展示透明效果，**不是 Settings 勾選 Transparent 的截圖**。

![去背後的 RGBA 透明效果](screenshots/transparent-result.png)

**Balance 前：**源圖不同動作人物大小不一致、每格寬度不等；實作讀取每格非透明範圍。**Balance 後：**自動裁出非透明外接矩形後，將其置中、腳底對齊到指定的固定畫格。最後水平 Combine 合成長條圖。下圖顯示真實輸出結果。

![實際生成的動作長條圖](screenshots/combine-results.png)

**各動作對照：** `stop` → `lee_idle.png`；`walk` → `lee_walk.png`；`jump` → `lee_jump.png`；`push` → `lee_kick.png`；`to` → `energy_blast.png`。中途的小圖保留在 `1/`～`5/` 各動作資料夾。

### 3-2 ⭐ 合併後的實際尺寸表

**下表的路徑全部以 `sketch.js` 所在根目錄為基準，且數字由 PNG 實測取得，不是老師範例數字。**

| 動作 | 圖檔路徑 | 總寬 | 高 | 張數 | 單格寬（總寬 ÷ 張數） |
|---|---|---:|---:|---:|---:|
{main_rows}

檢查結果：**全部單格寬均為整數**。`assets/sprite-data.json` 保存以上完整機器可讀資料。

## 4. 與 AI 對話紀錄

> **說明：**本次是以使用者「依照五部教材與上傳素材製作成果、填寫兩份 MD、提供 VS Code 專案和 GitHub 網站」的指示開始協作。下面「指令」整理為本次程式的**實際開發規格**，並非假稱使用者逐字輸入過每個範例提問。程式碼引用為此次產出的 `sketch.js`。

### 4-1 開發環境

| 項目 | 狀況 |
|---|---|
| VS Code 中文介面 | 由使用者的 Windows 電腦自行確認；本端無法查驗 |
| p5.js 擴充套件 | 由使用者自行確認（網站直接引用官方 p5.js 1.9.0 CDN） |
| Gemini／Copilot 登入 | 未使用；本次是與 ChatGPT 協作 |
| 專案資料夾 | `pixel-rift-dojo`，附 `.vscode/settings.json` |
| 檔案預覽 | 已在隔離式 Chromium 用同一份程式和實際圖像進行互動測試；因外部 CDN 無法存取，測試時使用本地相容渲染器 |

### 4-2 指令①：全視窗畫布與背景色

**開發規格：**「建立可在 VS Code Live Server 與 GitHub Pages 使用的 p5.js 單頁網頁，畫布固定 1280×680 並以 CSS 自適應縮放；背景為霓虹夜景，含山、城市、月亮、地板與 HUD。」

**結果：**首頁及遊戲背景已完成；利用 CSS 讓畫布隨容器寬度縮放，仍保留 p5.js 的固定設計座標。

![首頁實際測試畫面](screenshots/actual-home.png)

```javascript
const WORLD = {{ width: 1280, height: 680, floor: 543, gravity: 0.86 }};
function setup() {{
  const canvas = createCanvas(WORLD.width, WORLD.height);
  canvas.parent('canvas-holder');
  pixelDensity(1); noSmooth();
  // 其餘初始化詳見下方完整 sketch.js
}}
function draw() {{
  backgroundScene();
  drawObjects();
  paintHUD();
}}
```

### 4-3 指令②：中間產生角色（stop 動畫）

**開發規格：**「從 `assets/sheets/lee_idle.png` 載入橫向精靈圖，共 **3 張**、**總寬 450、高 124**；以單格寬 150 擷取，主角起始 x=290，站在地面 y=543，沒有按鍵時循環播放待機。」

**結果：**李振康可站立待機，主角圖像使用透明背景且角色不會被切到另一格。

![站立與待機動畫測試畫面](screenshots/final-stand.png)

```javascript
const m = META['lee_idle']; // frameWidth=150, frameHeight=124, frames=3
const frameIndex = Math.floor(ambientTime / 11) % m.frames;
image(sheets['lee_idle'], -m.frameWidth/2, -m.frameHeight,
      m.frameWidth, m.frameHeight, frameIndex*m.frameWidth, 0,
      m.frameWidth, m.frameHeight);
```

### 4-4 指令③：往右鍵／往左鍵（走路、轉向）

**開發規格：**「按左右方向鍵（或 A/D）移動，切換 `lee_walk.png` 六格動畫；往左時以 `scale(-1,1)` 水平翻轉，放開回到 stop。」

**結果：**角色可左右移動，方向朝向與按鍵相同，放開能回到待機。Shift 能衝刺。

![左右移動測試](screenshots/final-walk.png)

```javascript
const dir = (keys.ArrowRight || keys.KeyD ? 1 : 0) -
            (keys.ArrowLeft || keys.KeyA ? 1 : 0);
if (dir) {{ hero.x += dir * FIGHTERS[fighter].speed * dt; hero.face = dir; }}
// draw 時：translate(hero.x, hero.y); scale(scaleFactor*hero.face, scaleFactor);
```

### 4-5 指令④：往上鍵（跳起來）

**開發規格：**「使用 `lee_jump.png`（6 格、總寬 900、高 132），按 ↑/W 跳躍，加入重力與落地判定，避免重複無限跳躍。」

**結果：**`hero.vy=-17.1`，每幀增加重力 `0.86`；當 y 達地板 543 時重設速度、恢復地面狀態，不會穿過地板。

```javascript
function jump() {{
  if (state !== 'playing' || !hero.grounded) return;
  hero.vy = -FIGHTERS[fighter].jump;
  hero.grounded = false;
  hero.action = 'jump';
}}
// updateGame: hero.y += hero.vy*dt; hero.vy += WORLD.gravity*dt;
// if(hero.y >= WORLD.floor) {{ hero.y=WORLD.floor; hero.vy=0; hero.grounded=true; }}
```

### 4-6 指令⑤：空白鍵（發功＋特效）

**開發規格：**「空白鍵使用 22 能量，施放左右方向的發光能量波；波會向角色面向方向移動，命中敵人扣血並出現擊中特效，另外支援 Z 拳擊、X 踢擊。」

**結果：**能量會減少，空白鍵產生遠距離投射物，命中敵人後顯示 HIT 與粒子；Z/X 可近身攻擊。

![能量波／攻擊測試畫面](screenshots/final-attack.png)

```javascript
if (hero.energy >= 22) {{
  hero.energy -= 22;
  bolts.push({{x:hero.x+hero.face*61, y:hero.y-87,
              vx:hero.face*12.5,life:85,hitIds:new Set()}});
}}
// updateGame 中 b.x += b.vx*dt；與敵人距離小於門檻時 damageEnemy(...)
```

### 4-7 進階：第二位角色與敵人互動

| 項目 | 成果 |
|---|---|
| 角色二素材 | `Chun-Li(1).png`，從 `2/` 讀取春麗動畫 |
| 角色二動作 | stop 10 格；walk 8 格；jump／punch／kick 各 6 格；hurt 2 格 |
| 第三位角色／敵方 | 褐猴、綠猴（各 8 格）；另有 CM 的藍猴 8 格 |
| 角色二是否放大 | 春麗依原始小圖放大約 3.03 倍；李振康約 1.56 倍 |
| 靠近互動 | 怪物靠近主角會攻擊；玩家可以拳、腳或能量波打退敵人 |
| 文字對話框／倒下 | 使用 HIT／K.O.／COMBO 浮字與敵人淡出；未製作口語對話框或完整倒地影格，沒有聲稱已完成 |

![春麗角色切換測試](screenshots/final-chun.png)

### 4-8 其他指令：配樂與介面

**開發規格：**「依第 5 部影片增加背景音樂和音效，避免自動播放被瀏覽器阻擋；加入開始畫面、暫停、重新挑戰、計分及手機可用的按鈕。」

**結果：**自製 `assets/audio/dojo-loop.wav`（16 秒可循環），按「♫ 音樂」或 M 開關；拳擊、踢擊、跳躍、命中、遊戲結束的音效以 Web Audio 合成。聲音需使用者點擊才能播放。畫面含開始、角色選擇、操作說明、血量／能量條與波次分數。

## 5. 遇到的問題與解決

| # | 問題（實際發現或測試訊息） | 解法 | 是否用 AI 協作 |
|---|---|---|---|
| 1 | 角色原圖背景有洋紅、粉紅、藍灰三色，直接使用會保留大色塊。 | 依原圖背景鍵色轉 RGBA 透明，並保留五份原始檔方便重做。 | 是，產生 `tools/prepare_sprites.py` |
| 2 | 大圖多個動作混排、寬高不一，等寬切圖會切到隔壁人物。 | 依來源動作區塊逐格裁切，再對齊固定格尺寸並水平合併。 | 是，先檢查尺寸並人工確認分格配置 |
| 3 | 測試程式出現 `drawCombatFX is not defined` 的 JavaScript 執行錯誤。 | 移除重複、無定義的呼叫，粒子與攻擊軌跡在 `drawAttackTrails()` 正常繪製；之後測試無執行錯誤。 | 是，修正 `sketch.js` |
| 4 | 測試用瀏覽器的外部網頁與 p5.js CDN 連線受到隔離限制。 | 保留**正式官方 p5.js CDN 優先**，加入 `vendor/p5-local.js` 作為本作品限定的離線相容備援；用同份 sketch.js、實際 PNG 測試互動。 | 是，增加離線測試機制 |
| 5 | 瀏覽器限制未互動前播放聲音。 | 需點擊音樂按鈕或按 M 才開始播放 WAV。 | 是，加入音樂開關與例外處理 |

**Console 實際測試情形：**最終隔離式 Chromium 測試顯示開始遊戲、移動、空白鍵攻擊、切換角色、暫停與繼續均可執行，無 JavaScript 執行錯誤。由於隔離工具無法訪問外部 CDN，尚需於真實 GitHub Pages 上測試官方 p5.js 正式版本。

**被我 Reject 的修改：**此次沒有真實的「拒絕 AI 建議」操作紀錄，故不虛構拒絕歷程；但已明確拒絕以自製示意圖冒充 ASU／SpriteTracer 軟體畫面。

## 6. 最終成果

### 6-1 完整程式碼（sketch.js）

以下是作品根目錄 `sketch.js` 的完整程式碼。HTML／CSS、音樂及圖片也同時包含在 ZIP 專案內。

```javascript
{source_code}
```

### 6-2 成果畫面（至少三張）

**圖一：主角站立／待機**

![待機](screenshots/final-stand.png)

**圖二：左右移動**

![移動](screenshots/final-walk.png)

**圖三：空白鍵能量波／踢擊**

![攻擊](screenshots/final-attack.png)

**圖四：切換春麗**

![切換角色](screenshots/final-chun.png)

### 6-3 專案資料夾

![實際檔案結構示意圖（自動產生，非 VS Code 視窗截圖）](screenshots/project-tree.png)

**資料夾檔案已經實際建立**：`index.html`、`sketch.js`、`style.css`、`assets/`、`1/`～`5/`、`docs/`、`.vscode/` 等。若需 VS Code 檔案總管截圖，請於你的電腦開啟專案後補拍。

### 6-4 上傳確認

| 項目 | 完成狀況 |
|---|---|
| GitHub Repository 建立 | ☐ **尚未**；等待使用者授權／操作 |
| 合併後長條圖已放入專案 | ☑ **已完成** |
| 資料夾結構正確（如 `1/run`） | ☑ **已完成**（`1/run` 以 walk 素材衍生） |
| GitHub Pages 開啟及網址可執行 | ☐ **尚未**；公開部署後再驗證 |
| ZIP 壓縮檔 | ☑ 已整理為可開啟的 VS Code 專案 |
| 預覽測試 | ☑ Chromium 隔離環境、離線相容渲染器；☐ 正式 GitHub Pages |

## 7. 心得與反思

> 下列為依這次**實際製作過程整理的心得草稿**，提交前可改成自己的用語；不是假稱學生親筆寫過。

1. **最難的是什麼？** 角色原始圖不是規則排列，而且背景色與尺寸不同；必須辨認連續動作，再做好透明背景、同大小對齊，否則人物會抖動或切錯位置。
2. **哪個 AI 指令最有效？** 明確交代「圖檔路徑、總寬、高、張數、每格寬」最有效，程式才能正確抓到精靈圖位置；如果只要求「讓人物動起來」，很容易漏掉切格細節。
3. **如果重做會怎麼改？** 先把所有動作影格及尺寸表完成，再一次設計角色切換、敵人互動與背景音樂；同時在 Windows 留下 ASU 和 SpriteTracer 真實操作截圖，避免成果有圖但缺少製作過程證明。
4. **下一步想增加什麼？** 更多角色技能、勝利／倒地動作、分數排行榜、完整手機版搖桿、角色對話，以及 GitHub Pages 的正式上線測試。

## 8. 繳交前自我檢查

- [x] 五份原始精靈圖有保留，原圖尺寸已列出
- [ ] **素材原始下載網址／授權**：待使用者補充
- [ ] **ASU 與 SpriteTracer 真的操作截圖**：本端不能執行 Windows GUI，待補
- [x] 每個實際動作的 **總寬 × 高 × 張數 × 單格寬** 已填
- [x] AI 開發規格、程式碼及代表性操作結果已記錄
- [x] 遇到的問題、解法與可檢驗的測試情形已填
- [x] 至少 3 張最終網頁測試畫面
- [x] VS Code 專案及壓縮檔已產生
- [ ] **姓名、學號**：未提供，待補
- [ ] **GitHub Repository 網址及 GitHub Pages 網址**：尚待帳號授權發布後填寫
- [x] 專案介面、角色安排與同學的範例使用不同的畫面、玩法與佈景

> 發布方法詳見專案根目錄的 `README.md`。**注意：不要將本次 Pillow 切圖的說明圖視為 ASU／SpriteTracer GUI 截圖。**
'''
(DOC/'學生版_角色動畫製作紀錄_已填寫.md').write_text(student,encoding='utf8')
print('Wrote docs:',(DOC/'ASU與SpriteTracer_切圖合併_完整教材.md.md').stat().st_size,(DOC/'學生版_角色動畫製作紀錄_已填寫.md').stat().st_size)
