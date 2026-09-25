"""Edit the Desktop Drawer walkthrough from real session footage.

A different format from the other product videos: the footage is the whole
desktop, full-bleed. A synthetic "cluttered desktop" intro on the same wallpaper
sweeps its icons into the panel, then the real recording plays in trimmed
segments with lower-third captions, and a wipe takes us to the closing card.
Reads rec/footage.mp4 (extracted to rec/frames) and rec/events.json.
"""
import json, math, os, random, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import captions as CAP
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 25; W, H = 1280, 960
REC = 'rec'; OUT = 'frames'
FONTS = os.environ.get('WALKTHROUGH_FONTS', os.path.expanduser('~/.claude/skills/canvas-design/canvas-fonts/'))
ACCENT = (232, 140, 92); INK = (26, 42, 70); PAPER = (250, 244, 232)
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
if not os.path.isdir(f'{REC}/frames'):
    os.makedirs(f'{REC}/frames'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{REC}/footage.mp4', f'{REC}/frames/%05d.png'], check=True)
EV = {e['name']: e['t'] for e in json.load(open(f'{REC}/events.json'))}
WALL = Image.open('wallpaper.png').convert('RGB').resize((W, H))
ICON_AT = (19, 940)   # the applet icon in the panel, bottom-left


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)

F_BIG = font('BricolageGrotesque-Bold.ttf', 84)
F_MID = font('BricolageGrotesque-Bold.ttf', 44)
F_CAP = font('BricolageGrotesque-Bold.ttf', 52)
F_BODY = font('WorkSans-Regular.ttf', 38)
F_SMALL = font('WorkSans-Regular.ttf', 22)


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


_NFRAMES = None
def footage(t):
    """A footage frame with the bare desktop (exact black in the disposable session) keyed to the wallpaper."""
    global _NFRAMES
    if _NFRAMES is None:
        _NFRAMES = len(os.listdir(f'{REC}/frames'))
    i = max(1, min(int(round(t * FPS)) + 1, _NFRAMES))
    im = Image.open(f'{REC}/frames/{i:05d}.png').convert('RGB')
    r, g, b = im.split()
    from PIL import ImageChops
    mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mask = mx.point(lambda v: 255 if v <= 6 else 0).filter(ImageFilter.MinFilter(3))
    return Image.composite(WALL, im, mask)


# --- synthetic clutter -----------------------------------------------------------
random.seed(11)
NAMES = ['invoice-final-v3.pdf', 'IMG_2041.jpg', 'notes (copy).txt', 'Screenshot 2026-09-01.png', 'draft2.docx', 'setup.deb',
         'tax-2025.xlsx', 'holiday.zip', 'recipe.md', 'meeting.ics', 'logo-old.svg', 'export (3).csv', 'todo.txt', 'IMG_2042.jpg',
         'slides.pptx', 'cv-latest.pdf', 'archive.tar.gz', 'photo-edit.xcf', 'Untitled.odt', 'reading list.txt', 'song.mp3',
         'IMG_2043.jpg', 'form-signed.pdf', 'sketch.png', 'quotes.txt', 'budget.ods', 'backup.img', 'idea.md']
ICONS = []
for k, name in enumerate(NAMES):
    col = k % 8; row = k // 8
    x = 40 + col * 150 + random.randint(-12, 12); y = 40 + row * 190 + random.randint(-10, 10)
    ICONS.append((x, y, name))


def draw_icon(d, x, y, name, scale=1.0, alpha=255):
    s = 56 * scale
    ext = name.rsplit('.', 1)[-1].lower()
    col = {'pdf': (214, 76, 60), 'jpg': (72, 150, 200), 'png': (72, 150, 200), 'txt': (240, 240, 240), 'md': (240, 240, 240),
           'zip': (200, 160, 70), 'gz': (200, 160, 70), 'deb': (200, 90, 60)}.get(ext, (230, 230, 230))
    d.rounded_rectangle((x, y, x + s, y + s * 1.25), radius=6 * scale, fill=col + (alpha,), outline=(0, 0, 0, alpha // 3))
    d.polygon([(x + s * 0.68, y), (x + s, y + s * 0.32), (x + s * 0.68, y + s * 0.32)], fill=(255, 255, 255, alpha // 2))
    if scale > 0.6:
        f = font('WorkSans-Regular.ttf', int(15 * scale))
        tw = d.textlength(name, font=f)
        d.rounded_rectangle((x + s / 2 - tw / 2 - 5, y + s * 1.3, x + s / 2 + tw / 2 + 5, y + s * 1.3 + 22 * scale), radius=4, fill=(0, 0, 0, int(140 * alpha / 255)))
        d.text((x + s / 2 - tw / 2, y + s * 1.3 + 2), name, font=f, fill=(255, 255, 255, alpha))


def panel(canvas):
    # approximate the recorded panel so the intro matches the first footage frame
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 920, W, H), fill=(44, 44, 44))
    return canvas


def intro_frame(t, dur):
    """0-1.4s: cluttered desktop + headline; 1.4-2.8: icons fly into the panel icon; 2.8-dur: clean wallpaper + line."""
    canvas = WALL.copy()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    fly = ease((t - 1.4) / 1.3)
    for (x, y, name) in ICONS:
        if fly <= 0:
            draw_icon(d, x, y, name)
        elif fly < 1:
            nx = x + (ICON_AT[0] - x) * fly; ny = y + (ICON_AT[1] - y) * fly
            draw_icon(d, nx, ny, name, scale=1 - 0.85 * fly, alpha=int(255 * (1 - fly * 0.6)))
    canvas.paste(ov, (0, 0), ov)
    canvas = panel(canvas)
    # first frame of footage has the real panel + icon; blend it in over the last part so the cut is seamless
    if t > 2.6:
        canvas = Image.blend(canvas, footage(EV['desktop']), ease((t - 2.6) / 0.5))
    d = ImageDraw.Draw(canvas, 'RGBA')
    if t < 1.8:
        a = int(255 * ease(t / 0.5))
        _headline(d, 'Too many files|on your desktop?', a)
    elif t > 2.7:
        a = int(255 * ease((t - 2.7) / 0.5))
        _headline(d, 'Now enjoy your wallpaper.', a, sub='Your files are one hover away, in the panel.')
    return canvas


def _headline(d, text, a, sub=None):
    canvas = d._image
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    sh = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    lines = text.split('|'); y = 330
    for line in lines:
        tw = ld.textlength(line, font=F_BIG); x = (W - tw) / 2
        sd.text((x + 3, y + 5), line, font=F_BIG, fill=(0, 0, 0, int(a * 0.75)))
        ld.text((x, y), line, font=F_BIG, fill=(255, 255, 255, a)); y += 100
    if sub:
        sw = ld.textlength(sub, font=F_BODY)
        sd.text(((W - sw) / 2 + 2, y + 16), sub, font=F_BODY, fill=(0, 0, 0, int(a * 0.75)))
        ld.text(((W - sw) / 2, y + 14), sub, font=F_BODY, fill=(255, 238, 214, a))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    base = canvas.convert('RGBA'); base = Image.alpha_composite(base, sh); base = Image.alpha_composite(base, layer)
    canvas.paste(base.convert('RGB'))


def lower_third(canvas, text, a=255):
    return CAP.caption(canvas, text, F_CAP, alpha=a / 255, accent=ACCENT, margin=330, bottom=70, scrim_from_x=300)


def outro_frame(t, dur):
    canvas = Image.blend(WALL.copy(), Image.new('RGB', (W, H), INK), 0.55)
    d = ImageDraw.Draw(canvas)
    a = ease(t / 0.6)
    lines = [('Desktop Drawer', F_BIG), ('Free and open source, for Cinnamon 6.', F_MID),
             ('Get the beta at implantintelligence.com', F_BODY)]
    y = 300
    for text, f in lines:
        tw = d.textlength(text, font=f); d.text(((W - tw) / 2, y), text, font=f, fill=(255, 255, 255)); y += (110 if f is F_BIG else 70 if f is F_MID else 46)
    small = 'Real Cinnamon session, sample files. Music: Wallpaper by Kevin MacLeod, CC BY 4.0. Photo: Daniel Mirlea, Unsplash.'
    sw = d.textlength(small, font=F_SMALL); d.text(((W - sw) / 2, H - 90), small, font=F_SMALL, fill=(220, 210, 190))
    if a < 1:
        canvas = Image.blend(Image.new('RGB', (W, H), INK), canvas, a)
    return canvas


# segments of real footage: (from_event, to_event, speed, caption)
SEGMENTS = [
    ('desktop', 'menu-open', 1.0, 'Hover over the panel icon. The drawer opens.'),
    ('menu-open', 'projects', 1.0, 'Folders open right inside the menu.'),
    ('projects', 'reading', 1.0, 'Click a file to open it in its usual app.'),
    ('reading', 'escape', 1.15, 'Arrow keys, Enter and Escape work too.'),
    ('escape', 'settings', 1.2, 'Choose folder lets you pick any folder.'),
    ('settings', 'settings-closed', 1.4, 'Turn hover on or off, and set the delay.'),
    ('settings-closed', 'light-menu', 1.1, 'It follows your light or dark theme.'),
    ('light-menu', 'end', 1.0, ''),
]
INTRO = 5.2; OUTRO = 4.4; WIPE = 0.5

frame_idx = 0
def emit(img):
    global frame_idx
    img.save(f'{OUT}/{frame_idx:05d}.png'); frame_idx += 1

cues = []
# intro
for i in range(int(INTRO * FPS)):
    emit(intro_frame(i / FPS, INTRO))
cues.append((0.0, INTRO, 'Too many files on your desktop? Now enjoy your wallpaper. Your files are one hover away, in the panel.'))
# footage segments, captions fade in over 0.3 s, out before the next
t_out = INTRO
for (a, b, speed, caption) in SEGMENTS:
    start, end = EV[a], EV[b]
    n = int((end - start) / speed * FPS)
    seg_start = t_out
    for i in range(n):
        t = start + i / FPS * speed
        img = footage(t)
        if caption:
            fade = ease(i / (0.3 * FPS)) * ease((n - i) / (0.3 * FPS))
            img = lower_third(img, caption, int(255 * fade))
        emit(img)
    t_out = frame_idx / FPS
    if caption:
        cues.append((seg_start, t_out, caption))
# wipe to outro
last = footage(EV['end'])
first_outro = outro_frame(0.6, OUTRO)
for i in range(int(WIPE * FPS)):
    u = ease((i + 1) / (WIPE * FPS)); edge = int(W * u)
    img = last.copy(); img.paste(first_outro.crop((0, 0, max(1, edge), H)), (0, 0))
    emit(img)
outro_start = frame_idx / FPS
for i in range(int(OUTRO * FPS)):
    emit(outro_frame(0.6 + i / FPS, OUTRO))
cues.append((outro_start, frame_idx / FPS, 'Desktop Drawer. Free and open source, for Cinnamon 6. Get the beta at implantintelligence.com.'))
duration = frame_idx / FPS

def ts(s): return '%02d:%02d:%06.3f' % (int(s // 3600), int(s % 3600 // 60), s % 60)
vtt = ['WEBVTT', '']; chapters = []
for s, e, text in cues:
    vtt += [f'{ts(s)} --> {ts(e)}', text, '']
    chapters.append({'title': text.split('.')[0], 'start': round(s, 3), 'time': '%d:%02d' % (int(s // 60), int(s % 60))})
open('usage-demo.vtt', 'w').write('\n'.join(vtt)); open('chapters.json', 'w').write(json.dumps(chapters, indent=1))
open('usage-demo-transcript.txt', 'w').write('Desktop Drawer: a walkthrough\nRecorded in a disposable Cinnamon 6 session with sample files. The opening clutter is illustrative; everything after it is the real applet.\n\n' + '\n'.join(c[2] for c in cues) + '\n\nMusic: Wallpaper by Kevin MacLeod (incompetech.com), CC BY 4.0. Excerpt with volume adjusted, fades and transition sounds added.\nWallpaper: photo by Daniel Mirlea, from the Linux Mint backgrounds collection, Unsplash License.\n')
json.dump({'duration': duration, 'cue_starts': [c[0] for c in cues][1:]}, open('timing.json', 'w'))
print('frames', frame_idx, 'duration', duration)
