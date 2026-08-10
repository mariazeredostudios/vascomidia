#!/usr/bin/env python3
"""
Vasco International — gerador de cenas estáticas do reel (template diagonal).

Gera 7 PNGs 1080x1920 usando o recurso gráfico oficial do clube (corte
diagonal preto/branco, o mesmo padrão do escudo), tipografia Barlow
Condensed ExtraBold/Black (título) + Barlow (texto corrido), números em
dourado (#9C7728) e a cruz de Malta vermelha (#C52822 no selo oficial)
como ÚNICO uso de vermelho na peça, sempre discreta, no canto.

Uso: python3 scripts/build_reel.py
Saída: build/scenes/scene_1.png ... scene_7.png
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
BRAND = os.path.join(ROOT, "assets", "brand")
OUT = os.path.join(ROOT, "build", "scenes")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920

# Paleta oficial (Direcional Visual 2026)
BLACK = (14, 14, 14, 255)
WHITE = (247, 247, 245, 255)
GOLD = (156, 119, 40, 255)
RED = (197, 40, 34, 255)  # usar SOMENTE na cruz de Malta

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

F_TITLE_BLACK = lambda s: font("BarlowCondensed-Black.ttf", s)
F_TITLE_XB = lambda s: font("BarlowCondensed-ExtraBold.ttf", s)
F_TITLE_BOLD = lambda s: font("BarlowCondensed-Bold.ttf", s)
F_BODY = lambda s: font("Barlow-Regular.ttf", s)
F_BODY_MED = lambda s: font("Barlow-Medium.ttf", s)
F_BODY_SEMI = lambda s: font("Barlow-SemiBold.ttf", s)
F_BODY_BOLD = lambda s: font("Barlow-Bold.ttf", s)

crest = Image.open(os.path.join(BRAND, "escudo_vasco.png")).convert("RGBA")
cross_badge = Image.open(os.path.join(BRAND, "cruz_malta_selo.png")).convert("RGBA")


# O corte diagonal fica confinado a uma faixa estreita perto da borda direita
# (SEAM_MIN..SEAM_MAX), nunca cruzando a coluna de texto à esquerda — assim o
# painel principal (onde ficam título/número/corpo) é sempre uma cor sólida,
# e o corte diagonal aparece como acento gráfico na borda, sem risco de texto
# "sumir" ao trocar de cor no meio da frase.
SEAM_MAX = 920  # topo do frame
SEAM_MIN = 680  # base do frame
SAFE_TEXT_W = SEAM_MIN - 70 - 50  # margem esquerda (70) + respiro (50)


def diagonal_split(black_on="left"):
    """Fundo 1080x1920: painel principal sólido + acento diagonal preto/branco
    na borda direita, no mesmo espírito do corte do escudo do clube."""
    img = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    main_poly = [(0, 0), (SEAM_MAX, 0), (SEAM_MIN, H), (0, H)]
    accent_poly = [(SEAM_MAX, 0), (W, 0), (W, H), (SEAM_MIN, H)]

    main_color = BLACK if black_on == "left" else WHITE
    accent_color = WHITE if black_on == "left" else BLACK

    draw.polygon(main_poly, fill=main_color)
    draw.polygon(accent_poly, fill=accent_color)

    return img


def text_color_at(x, black_on):
    """Cor de texto legível para a coluna à esquerda (sempre dentro do
    painel principal sólido, então independe de y)."""
    on_black = black_on == "left"
    return WHITE if on_black else BLACK


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_multiline(draw, xy, lines, fnt, fill, line_gap=1.04, align="left", max_width=None):
    x, y = xy
    ascent, descent = fnt.getmetrics()
    line_h = (ascent + descent) * line_gap
    for line in lines:
        lw = draw.textlength(line, font=fnt)
        lx = x
        if align == "center" and max_width is not None:
            lx = x + (max_width - lw) / 2
        elif align == "right" and max_width is not None:
            lx = x + (max_width - lw)
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def kicker_and_watermark(img, black_on, kicker="VASCO INTERNATIONAL"):
    draw = ImageDraw.Draw(img)
    # kicker no topo
    fnt = F_BODY_SEMI(30)
    color = text_color_at(70, black_on)
    draw.text((70, 96), kicker, font=fnt, fill=(*color[:3], 235))
    tracked_underline_w = draw.textlength(kicker, font=fnt)
    draw.rectangle([70, 140, 70 + min(120, tracked_underline_w), 143], fill=GOLD)

    # selo da cruz de malta, discreto, no canto inferior direito
    badge = cross_badge.copy()
    bsize = 108
    badge.thumbnail((bsize, bsize))
    alpha = badge.split()[3].point(lambda p: int(p * 0.92))
    badge.putalpha(alpha)
    img.alpha_composite(badge, (W - badge.width - 56, H - badge.height - 64))
    return img


def scene_hook():
    img = diagonal_split(black_on="left")
    img = kicker_and_watermark(img, "left")
    draw = ImageDraw.Draw(img)

    fnt = F_TITLE_BLACK(78)
    lines = wrap_text(draw, "NINGUÉM TE EXPLICA COMO FUNCIONA UMA SELETIVA DE CLUBE GRANDE".upper(), fnt, SAFE_TEXT_W)
    y = 620
    for line in lines:
        draw.text((70, y), line, font=fnt, fill=WHITE)
        ascent, descent = fnt.getmetrics()
        y += (ascent + descent) * 1.0

    y += 26
    fnt2 = F_TITLE_XB(78)
    draw.text((70, y), "ATÉ AGORA.", font=fnt2, fill=GOLD)

    fnt3 = F_BODY_MED(36)
    draw.text((70, H - 260), "Seletiva Vasco International", font=fnt3, fill=WHITE)
    fnt4 = F_BODY(30)
    body_line = wrap_text(draw, "16 de agosto · CT Almirante Heleno de Barros Nunes", fnt4, SAFE_TEXT_W)
    draw_multiline(draw, (70, H - 205), body_line, fnt4, (247, 247, 245, 215), line_gap=1.25)
    return img


def scene_step(number, title, body, black_on):
    img = diagonal_split(black_on=black_on)
    img = kicker_and_watermark(img, black_on)
    draw = ImageDraw.Draw(img)

    num_color = GOLD
    fnt_num = F_TITLE_BLACK(360)
    draw.text((56, 330), str(number), font=fnt_num, fill=num_color)

    label_color = text_color_at(70, black_on)
    fnt_label = F_BODY_BOLD(32)
    draw.text((70, 300), f"PASSO {number} DE 5", font=fnt_label, fill=label_color)

    fnt_title = F_TITLE_XB(72)
    title_lines = wrap_text(draw, title.upper(), fnt_title, SAFE_TEXT_W)
    y = 850
    for line in title_lines:
        draw.text((70, y), line, font=fnt_title, fill=label_color)
        ascent, descent = fnt_title.getmetrics()
        y += (ascent + descent) * 1.0

    y += 22
    fnt_body = F_BODY(36)
    body_lines = wrap_text(draw, body, fnt_body, SAFE_TEXT_W)
    body_color = (*label_color[:3], 225)
    draw_multiline(draw, (70, y), body_lines, fnt_body, body_color, line_gap=1.3)

    return img


def scene_cta():
    # fundo sólido preto (texto centralizado não pode cruzar o corte diagonal)
    img = Image.new("RGBA", (W, H), BLACK)
    draw = ImageDraw.Draw(img)
    # sutil textura diagonal (mesmo tom, quase imperceptível) só pra não ficar
    # um preto totalmente chapado — ecoa o corte oficial sem competir com o texto
    accent = (24, 24, 24, 255)
    draw.polygon([(W * 0.72, 0), (W, 0), (W, H), (W * 0.94, H)], fill=accent)

    # escudo grande, centralizado, parte de cima
    c = crest.copy()
    c.thumbnail((300, 300))
    img.alpha_composite(c, ((W - c.width) // 2, 210))

    fnt_kicker = F_BODY_SEMI(32)
    kt = "SELETIVA"
    kw = draw.textlength(kt, font=fnt_kicker)
    draw.text(((W - kw) / 2, 560), kt, font=fnt_kicker, fill=WHITE)

    fnt_title = F_TITLE_BLACK(118)
    t1 = "VASCO"
    t2 = "INTERNATIONAL"
    for i, (t, fs) in enumerate([(t1, 118), (t2, 78)]):
        fnt = F_TITLE_BLACK(fs)
        tw = draw.textlength(t, font=fnt)
        draw.text(((W - tw) / 2, 615 + i * 130), t, font=fnt, fill=WHITE)

    fnt_date = F_TITLE_XB(64)
    dt = "16.08.2026"
    dw = draw.textlength(dt, font=fnt_date)
    draw.text(((W - dw) / 2, 990), dt, font=fnt_date, fill=GOLD)

    fnt_body = F_BODY(36)
    body_lines = [
        "Inscrição só pelo canal oficial",
        "do Sympla — sem intermediários.",
    ]
    y = 1110
    for line in body_lines:
        lw = draw.textlength(line, font=fnt_body)
        draw.text(((W - lw) / 2, y), line, font=fnt_body, fill=(247, 247, 245, 230))
        y += 52

    # CTA em destaque
    fnt_cta = F_TITLE_XB(58)
    ct = "LINK NA BIO"
    cw = draw.textlength(ct, font=fnt_cta)
    pad_x, pad_y = 46, 26
    box = [
        (W - cw) / 2 - pad_x, 1330,
        (W + cw) / 2 + pad_x, 1330 + 58 + pad_y * 2 - 20,
    ]
    draw.rectangle(box, fill=GOLD)
    draw.text(((W - cw) / 2, 1330 + pad_y - 12), ct, font=fnt_cta, fill=BLACK)

    badge = cross_badge.copy()
    badge.thumbnail((150, 150))
    img.alpha_composite(badge, ((W - badge.width) // 2, H - badge.height - 110))

    return img


STEPS = [
    (1, "Inscreva-se no canal oficial", "Só pelo Sympla oficial do Vasco International — nunca por links ou intermediários por fora."),
    (2, "Confira sua faixa de horário", "08h às 10h: nascidos entre 2013 e 2018. 10h às 12h: nascidos entre 2007 e 2012."),
    (3, "Anote a data e o local", "16 de agosto, no CT Almirante Heleno de Barros Nunes, Parque Sarapuí, Duque de Caxias/RJ."),
    (4, "Compareça pronto para o treino", "A avaliação é conduzida pelos treinadores da base do clube, no horário da sua faixa etária."),
    (5, "Siga @vasco_international", "Para acompanhar os próximos passos rumo à Disney Cup 2027."),
]


def main():
    scenes = []
    scenes.append(("scene_1", scene_hook()))
    sides = ["right", "left", "right", "left", "right"]
    for (n, title, body), side in zip(STEPS, sides):
        scenes.append((f"scene_{n+1}", scene_step(n, title, body, side)))
    scenes.append(("scene_7", scene_cta()))

    for name, img in scenes:
        path = os.path.join(OUT, f"{name}.png")
        img.convert("RGB").save(path, quality=95)
        print("gerado:", path)


if __name__ == "__main__":
    main()
