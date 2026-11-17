# 把每張鳥照裁成「整隻鳥（含頭）置中」的正方形，給圓形框用。
# BOX 是鳥在原圖中的範圍（以 0–10 格表示：x0,y0,x1,y1），手動看過每張照片定的。
# 用法：python3 -I tools/make_square.py   → assets/img/sq/<key>.jpg
import os, math
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

BOX = {
 'barbet':(2,2.3,9,9.2), 'blackbulbul':(0.8,2.2,6.8,6.2), 'bulbul':(2.3,1.2,7.8,9.5), 'bushrobin':(1.5,0.8,7,8),
 'buzzard':(2,1,8.5,9), 'cattleegret':(2.5,0.5,9,8), 'cormorant':(1.8,1,9,9.5), 'dove':(1,1.5,9.6,8.5),
 'drongo':(1.3,2,8,8), 'egret':(0.9,2.7,9.2,8.3), 'goshawk':(2,0.8,9,9.5), 'greyheron':(1.2,1,7,9),
 'jacana':(1,0.5,8.5,9), 'kingfisher':(1,1.5,9,10), 'kite':(2,0.3,7.5,9.5), 'magpie':(2.5,2,9.3,8),
 'magpie_tw':(0.8,2.8,7.6,8), 'mikado':(0.3,1.6,9.2,8.4), 'monarch':(2.8,2,9.3,7.5), 'moorhen':(0.6,1.5,7.5,9.5),
 'myna':(2.5,1,9.2,9), 'nightheron':(1.5,1,9,9), 'nightheron_mal':(3.8,1.8,8,7.8), 'owl':(2.2,2,6.5,7.5),
 'partridge':(3,2,6.2,8.5), 'pigeon':(3,2.5,9.8,8), 'reddove':(1,3.3,7.5,9), 'serpenteagle':(2.8,0.5,8.3,8.5),
 'sparrow':(0.8,1,7.5,8), 'spoonbill':(2,0.5,8.6,8.5), 'stilt':(3.3,1,8.5,10), 'stylesbulbul':(1.5,1.5,7,9),
 'swallow':(1.5,1.5,9,8), 'swinhoe':(1.2,1.2,9.8,8.4), 'treepie':(1.5,1.5,8,9), 'wagtail':(1,3.5,7.4,8.5),
 'whistlingthrush':(1.3,1.5,6.6,10), 'whiteeye':(1,2,8.5,8), 'yellowtit':(1.5,0.3,8,8.5), 'yuhina':(1.5,2.5,6.5,9),
}
ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'img')
OUT = os.path.join(ROOT, 'sq'); os.makedirs(OUT, exist_ok=True)
SIZE = 900
# 身體長、頭在邊邊的鳥多留邊，讓頭離圓框遠一點
PAD = {'swinhoe':1.22, 'mikado':1.22, 'magpie_tw':1.18, 'magpie':1.15, 'dove':1.15, 'greyheron':1.12, 'egret':1.12, 'wagtail':1.15, 'drongo':1.12, 'sparrow':1.1}

for k, (x0, y0, x1, y1) in BOX.items():
    im = Image.open(os.path.join(ROOT, k + '.jpg')).convert('RGB'); W, H = im.size
    bx0, by0, bx1, by1 = x0*W/10, y0*H/10, x1*W/10, y1*H/10
    bw, bh = bx1-bx0, by1-by0
    # 圓形會切掉四角：正方形邊長要讓鳥的框大致落在內切圓裡
    side = max(1.1*max(bw, bh), 0.92*math.hypot(bw, bh)) * PAD.get(k, 1.0)
    cx, cy = (bx0+bx1)/2, (by0+by1)/2
    # 能留在原圖內就平移，不夠才補模糊背景
    if side <= W: cx = min(max(cx, side/2), W-side/2)
    if side <= H: cy = min(max(cy, side/2), H-side/2)
    L, T = cx-side/2, cy-side/2
    s = int(round(side))
    canvas = Image.new('RGB', (s, s))
    ox, oy = int(round(-L)), int(round(-T))
    if L < 0 or T < 0 or L+side > W or T+side > H:
        # 超出原圖的部分：鏡射延伸＋模糊，接縫用漸層融合
        pl, pt = max(0, ox), max(0, oy)
        pr, pb = max(0, s-(ox+W)), max(0, s-(oy+H))
        arr = np.asarray(im)
        pad = np.pad(arr, ((pt, pb), (pl, pr), (0, 0)), mode='symmetric')
        bg = Image.fromarray(pad).filter(ImageFilter.GaussianBlur(18))
        canvas.paste(bg, (min(0, ox) + 0 if ox < 0 else 0, min(0, oy) if oy < 0 else 0))
        f = max(6, int(0.035*s))
        m = Image.new('L', (W, H), 255); md = ImageDraw.Draw(m)
        for i in range(f):
            v = int(255*i/f)
            if pl: md.line([(i, 0), (i, H)], fill=v)
            if pr: md.line([(W-1-i, 0), (W-1-i, H)], fill=v)
        m2 = Image.new('L', (W, H), 255); md2 = ImageDraw.Draw(m2)
        for i in range(f):
            v = int(255*i/f)
            if pt: md2.line([(0, i), (W, i)], fill=v)
            if pb: md2.line([(0, H-1-i), (W, H-1-i)], fill=v)
        from PIL import ImageChops
        canvas.paste(im, (ox, oy), ImageChops.multiply(m, m2))
    else:
        canvas.paste(im, (ox, oy))
    canvas.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, k + '.jpg'), quality=82)
print(len(BOX), 'done')
