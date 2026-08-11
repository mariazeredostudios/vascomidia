#!/usr/bin/env python3
"""
Vasco International — anima as 7 cenas estáticas em vídeo mudo.

Aplica Ken Burns (zoom lento, alternando zoom-in/zoom-out por cena) via
zoompan do ffmpeg, e transições crossfade (xfade) entre as cenas.

Uso: python3 scripts/animate.py
Entrada: build/scenes/scene_1.png ... scene_7.png
Saída: build/reel_mudo.mp4
"""

import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENES = os.path.join(ROOT, "build", "scenes")
CLIPS = os.path.join(ROOT, "build", "clips")
OUT = os.path.join(ROOT, "build", "reel_mudo.mp4")
TIMELINE_OUT = os.path.join(ROOT, "build", "timeline.json")
os.makedirs(CLIPS, exist_ok=True)

FPS = 30
W, H = 1080, 1920

# duração de cada cena (s): ~3,5s por cena, última (CTA) mais longa (~5,5s)
DURATIONS = [3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 5.5]
XFADE = 0.35  # duração da transição crossfade entre cenas
ZOOM_MAX = 0.12  # zoom vai de 1.0 a 1.0+ZOOM_MAX


def make_clip(idx, duration, zoom_in):
    src = os.path.join(SCENES, f"scene_{idx}.png")
    dst = os.path.join(CLIPS, f"clip_{idx}.mp4")
    frames = int(round(duration * FPS))

    if zoom_in:
        z_expr = f"1+{ZOOM_MAX}*on/{frames}"
    else:
        z_expr = f"(1+{ZOOM_MAX})-{ZOOM_MAX}*on/{frames}"

    vf = (
        f"scale=2160:3840,"
        f"zoompan=z='{z_expr}':d={frames}:s={W}x{H}:fps={FPS}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", src,
        "-vf", vf, "-t", str(duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        dst,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return dst


def build_xfade_chain(clips, durations):
    inputs = []
    for c in clips:
        inputs += ["-i", c]

    filter_parts = []
    offsets = []
    prev_label = "0:v"
    cumulative = durations[0]
    for i in range(1, len(clips)):
        offset = cumulative - XFADE
        offsets.append(offset)
        out_label = f"v{i}" if i < len(clips) - 1 else "vout"
        filter_parts.append(
            f"[{prev_label}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{out_label}]"
        )
        prev_label = out_label
        cumulative += durations[i] - XFADE

    filter_complex = ";".join(filter_parts)
    return inputs, filter_complex, cumulative, offsets


def main():
    clips = []
    for i, dur in enumerate(DURATIONS, start=1):
        zoom_in = (i % 2 == 1)  # alterna zoom-in / zoom-out por cena
        print(f"gerando clip {i} ({'zoom-in' if zoom_in else 'zoom-out'}, {dur}s)...")
        clips.append(make_clip(i, dur, zoom_in))

    inputs, filter_complex, total, offsets = build_xfade_chain(clips, DURATIONS)
    print(f"duração total estimada: {total:.2f}s")

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        OUT,
    ]
    subprocess.run(cmd, check=True)
    print("vídeo mudo gerado em:", OUT)

    # marcos pra sincronizar a trilha (make_music.py lê esse arquivo se existir)
    t_drop = offsets[0]      # início do groove (entrada do passo 1)
    t_impact = offsets[-1]   # aterrissagem do CTA
    t_riser = max(t_drop + 1.0, t_impact - 1.7)  # riser nos ~1,7s antes do impacto
    timeline = {
        "total": round(total, 3),
        "t_drop": round(t_drop, 3),
        "t_riser": round(t_riser, 3),
        "t_impact": round(t_impact, 3),
    }
    with open(TIMELINE_OUT, "w") as f:
        json.dump(timeline, f, indent=2)
    print("timeline gravada em:", TIMELINE_OUT, timeline)


if __name__ == "__main__":
    main()
