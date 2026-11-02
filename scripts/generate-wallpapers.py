#!/usr/bin/env python3
"""Source of the original Kuhl day and dusk PNG wallpapers.
Requires Pillow + NumPy (only for regenerating the art, not to use Kuhl).
Run: python3 scripts/generate-wallpapers.py
"""
from pathlib import Path
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 2560, 1440
OUT = Path(__file__).resolve().parents[1] / 'assets' / 'wallpapers'
OUT.mkdir(parents=True, exist_ok=True)

def rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def gradient(top, bottom, seed=0):
    a = np.asarray(rgb(top), dtype=np.float32)
    b = np.asarray(rgb(bottom), dtype=np.float32)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    vals = a[None,None,:] * (1-y) + b[None,None,:] * y
    vals = np.broadcast_to(vals, (H,W,3)).copy()
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1.6, (H,W,1)).astype(np.float32)
    vals = np.uint8(np.clip(vals+noise, 0, 255))
    return Image.fromarray(vals, mode='RGB')

def hill(draw, peak, baseline, amplitude, color, phase=0, frequency=1.0):
    points = [(0,H)]
    points += [(x, int(baseline - amplitude * math.sin((x/W)*math.pi*frequency + phase)
                      - peak * math.sin((x/W)*math.pi*2.6 + phase*.7)))
               for x in range(0,W+20,20)]
    points.append((W,H))
    draw.polygon(points, fill=color)

def tree(draw, x, y, s, stem, leaf):
    # Vector pine silhouettes. y is ground level.
    draw.rounded_rectangle((x-5*s,y-80*s,x+5*s,y+12*s), radius=3*s, fill=stem)
    for level in range(3):
        w=(38-level*8)*s; top=y-(168-level*42)*s
        draw.polygon([(x, top), (x-w,y-(70-level*23)*s), (x+w,y-(70-level*23)*s)], fill=leaf)

def make(day=True):
    if day:
        colors=dict(top='#92bac0', bottom='#f4d8b6', sun='#ffe5ab', glow='#fff4d4',
                    far='#96b3a7', mid='#6f9a89', near='#436e60', front='#2e554b',
                    stem='#355f51', leaf='#365e54', faint='#f7d6b5', ink='#e2ebd7')
        suffix='day'; sunpos=(1920,425); stars=False
    else:
        colors=dict(top='#233344', bottom='#b37a85', sun='#edd4a2', glow='#f5bc9c',
                    far='#667d89', mid='#4d6676', near='#334e61', front='#233d4c',
                    stem='#263f4d', leaf='#2d4956', faint='#e4a0a5', ink='#dfe7e1')
        suffix='dusk'; sunpos=(1940,385); stars=True
    im=gradient(colors['top'], colors['bottom'], seed=(10 if day else 30))
    d=ImageDraw.Draw(im, 'RGBA')
    if stars:
        random.seed(614)
        for _ in range(115):
            x=random.randint(110,W-100); y=random.randint(45,680)
            r=random.choice([1,1,1,2,2,3])
            d.ellipse((x-r,y-r,x+r,y+r), fill=(255,239,222, random.randint(100,210)))
    # Hand-placed gentle sun bloom, blurred independently.
    glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gx,gy=sunpos
    gd.ellipse((gx-285,gy-285,gx+285,gy+285),fill=(*rgb(colors['glow']),100))
    im=Image.alpha_composite(im.convert('RGBA'),glow.filter(ImageFilter.GaussianBlur(116)))
    d=ImageDraw.Draw(im, 'RGBA')
    d.ellipse((gx-125,gy-125,gx+125,gy+125),fill=(*rgb(colors['sun']),245))
    if stars:
        # Crescent moon instead of hard bright circle.
        d.ellipse((gx-52,gy-145,gx+177,gy+105), fill=(*rgb(colors['top']),245))
    # Atmospheric broad shape behind mountains.
    d.ellipse((-350,510,1020,1360),fill=(*rgb(colors['faint']),45))
    # Mountain skyline layers.
    hill(d, 60, 795, 124, colors['far'], phase=0.5, frequency=1.7)
    hill(d, 82, 975, 147, colors['mid'], phase=2.0, frequency=2.2)
    hill(d, 61, 1130, 93, colors['near'], phase=0.8, frequency=2.2)
    hill(d, 48, 1330, 70, colors['front'], phase=3.2, frequency=2.2)
    # Decorative gentle creek through hills.
    stream=[(580,1440),(730,1350),(920,1250),(1120,1180),(1280,1145),(1300,1145),
            (1210,1230),(1060,1330),(900,1440)]
    d.polygon(stream,fill=(*rgb('#e4b998' if day else '#c88c99'),84))
    # Silhouette trees at edges leave quiet central workspace.
    for x,y,s in [(-50,1390,2.4),(120,1410,1.6),(270,1455,1.25),
                  (2300,1450,1.45),(2480,1490,2.2),(2570,1490,1.8)]:
        tree(d,x,y,s,colors['stem'],colors['leaf'])
    # Small stylistic 'horizon' rings.
    ring=(*rgb('#faf1dc' if day else '#ecc9b5'),95)
    for offset in range(3):
        d.arc((gx-160-offset*35,gy-160-offset*35,gx+160+offset*35,gy+160+offset*35),
              start=208,end=297,fill=ring,width=3)
    # Tiny branding in lower-left that won't conflict with icons.
    try:
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
    except OSError:
        font=ImageFont.load_default()
    d.text((65,1370),'✳  kuhl / '+suffix, fill=(*rgb(colors['ink']),175),font=font)
    out=OUT/f'kuhl-{suffix}.png'
    im.convert('RGB').save(out, 'PNG', optimize=True)
    print(f'Wrote {out}, {out.stat().st_size//1024} KiB')

make(True)
make(False)
