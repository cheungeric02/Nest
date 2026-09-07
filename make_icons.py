from PIL import Image, ImageDraw, ImageFont

EMOJI = "\U0001FABA"  # nest with egg
FONT = r"C:\Windows\Fonts\seguiemj.ttf"

def rounded(size, radius, fill):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=fill)
    return img

def draw_emoji(base, box_frac):
    size = base.size[0]
    target = int(size * box_frac)
    # Segoe color emoji renders at fixed sizes; pick nearest supported then paste scaled
    render_px = 109  # native color bitmap size in seguiemj
    font = ImageFont.truetype(FONT, render_px)
    layer = Image.new("RGBA", (render_px * 2, render_px * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((render_px, render_px), EMOJI, font=font, embedded_color=True, anchor="mm")
    bbox = layer.getbbox()
    layer = layer.crop(bbox)
    scale = target / max(layer.size)
    layer = layer.resize((max(1, int(layer.size[0] * scale)), max(1, int(layer.size[1] * scale))), Image.LANCZOS)
    x = (size - layer.size[0]) // 2
    y = (size - layer.size[1]) // 2
    base.alpha_composite(layer, (x, y))
    return base

# "any" icons: emoji on soft cream rounded square with subtle green ring
for size in (192, 512):
    img = rounded(size, int(size * 0.22), (238, 246, 233, 255))  # #eef6e9
    d = ImageDraw.Draw(img)
    m = int(size * 0.06)
    d.rounded_rectangle([m, m, size - 1 - m, size - 1 - m], radius=int(size * 0.17),
                        outline=(58, 107, 79, 255), width=max(2, size // 64))
    draw_emoji(img, 0.66)
    img.save(f"icons/icon-{size}.png")

# maskable: emoji in safe zone on solid green full-bleed
mask = Image.new("RGBA", (512, 512), (58, 107, 79, 255))  # #3a6b4f
draw_emoji(mask, 0.56)
mask.save("icons/icon-maskable.png")

print("done")
