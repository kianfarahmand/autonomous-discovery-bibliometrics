"""Re-place three overlapping institution labels in Fig. 3a; the network drawing is unchanged.

Usage: python fig3_label_fix.py figures_in/fig3_lab_network.png figures_out/Fig3.png
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
font = ImageFont.truetype('DejaVuSans.ttf', 23)  # matplotlib default font, same size as original labels
im = Image.open(src).convert('RGBA')
a = np.array(im)


def clear_grey(x0, y0, x1, y1):
    """Whiten low-saturation pixels (old label text, faint edges) and keep coloured nodes."""
    sub = a[y0:y1, x0:x1, :3].astype(int)
    a[y0:y1, x0:x1][(sub.max(axis=2) - sub.min(axis=2)) < 25] = [255, 255, 255, 255]


clear_grey(536, 362, 631, 386)   # "Stanford", clipped by the "Tsinghua" label
clear_grey(440, 813, 572, 845)   # "DTU" and "Toronto", overlapping
im = Image.fromarray(a)
ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)


def label(text, x, ytop):
    b = font.getbbox(text)
    d.rectangle((x - 3, ytop - 3, x + b[2] - b[0] + 3, ytop + 23), fill=(255, 255, 255, 200))
    d.text((x - b[0], ytop - b[1]), text, font=font, fill=(0, 0, 0, 255))


label('Stanford', 522, 365)
label('DTU', 420, 815)
label('Toronto', 482, 825)
Image.alpha_composite(im, ov).convert('RGB').save(out, dpi=(300, 300))
