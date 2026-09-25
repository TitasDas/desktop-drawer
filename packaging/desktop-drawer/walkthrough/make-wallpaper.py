#!/usr/bin/env python3
"""A calm 1280x960 wallpaper for the walkthrough: dusk gradient, sun, layered hills."""
import math, sys
from PIL import Image, ImageDraw, ImageFilter
W, H = 1280, 960
out = sys.argv[1] if len(sys.argv) > 1 else 'wallpaper.png'
img = Image.new('RGB', (W, H)); px = img.load()
top = (26, 42, 70); mid = (232, 140, 92); bottom = (250, 214, 160)
for y in range(H):
    t = y / H
    c = (tuple(int(top[i] + (mid[i] - top[i]) * ((t / 0.55) ** 1.6)) for i in range(3)) if t < 0.55
         else tuple(int(mid[i] + (bottom[i] - mid[i]) * ((t - 0.55) / 0.45)) for i in range(3)))
    for x in range(W): px[x, y] = c
d = ImageDraw.Draw(img)
sun = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sun)
sd.ellipse((W * 0.62 - 90, H * 0.50 - 90, W * 0.62 + 90, H * 0.50 + 90), fill=(255, 236, 200, 230))
sun = sun.filter(ImageFilter.GaussianBlur(6)); img.paste(sun, (0, 0), sun)
for color, base, amp in [((58, 70, 96), 0.58, 60), ((74, 92, 112), 0.66, 50), ((48, 66, 78), 0.76, 40), ((36, 50, 58), 0.86, 30)]:
    pts = [(0, H)] + [(x, H * base - amp * (0.6 * math.sin(x / 190 + base * 9) + 0.4 * math.sin(x / 67 + base * 3))) for x in range(0, W + 41, 40)] + [(W, H)]
    d.polygon(pts, fill=color)
img.save(out); print('wrote', out)
