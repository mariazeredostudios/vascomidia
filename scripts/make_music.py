#!/usr/bin/env python3
"""
Vasco International — trilha sonora original sintetizada do zero (numpy).

100% sintetizado (kick, hi-hat, clap, sub-bass, arpejo, riser e impacto),
sem amostras de terceiros — sem risco de direito autoral. Estruturada para
acompanhar o reel "5 passos": build-up no gancho, groove energético durante
os passos, riser + impacto na entrada do CTA, e um fade limpo no final.

Uso: python3 scripts/make_music.py [duracao_segundos]
Saída: build/trilha.wav
"""

import json
import os
import sys
import numpy as np
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "trilha.wav")
TIMELINE_IN = os.path.join(ROOT, "build", "timeline.json")

SR = 44100
BPM = 128.0
BEAT = 60.0 / BPM

# marcos da timeline (segundos) — lidos de build/timeline.json (gerado pelo
# animate.py a partir da duração real de cada cena), com fallback manual
# caso o arquivo não exista ainda.
if os.path.exists(TIMELINE_IN):
    with open(TIMELINE_IN) as f:
        _tl = json.load(f)
    DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else _tl["total"]
    T_DROP = _tl["t_drop"]
    T_RISER = _tl["t_riser"]
    T_IMPACT = _tl["t_impact"]
else:
    DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 13.8
    T_DROP = 2.6
    T_RISER = 9.3
    T_IMPACT = 11.0
T_END = DURATION


def t_axis(t0, t1):
    n = max(1, int(round((t1 - t0) * SR)))
    return np.linspace(t0, t1, n, endpoint=False)


def adsr(n, sr, a=0.005, d=0.08, s=0.0, r=0.05):
    a_n, d_n, r_n = int(a * sr), int(d * sr), int(r * sr)
    s_n = max(0, n - a_n - d_n - r_n)
    env = np.concatenate([
        np.linspace(0, 1, max(a_n, 1)),
        np.linspace(1, s, max(d_n, 1)),
        np.full(s_n, s),
        np.linspace(s, 0, max(r_n, 1)),
    ])
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def kick(sr, dur=0.22, f0=150, f1=42, amp=1.0):
    n = int(dur * sr)
    t = np.arange(n) / sr
    freq = f0 * np.exp(-t / 0.045) + f1
    phase = 2 * np.pi * np.cumsum(freq) / sr
    tone = np.sin(phase)
    env = np.exp(-t / 0.09)
    click = np.random.uniform(-1, 1, n) * np.exp(-t / 0.004) * 0.25
    return amp * (tone * env + click)


def hihat(sr, dur=0.05, amp=0.35, open_=False):
    n = int((0.22 if open_ else dur) * sr)
    noise = np.random.uniform(-1, 1, n)
    # high-pass simples via diferenciação repetida
    for _ in range(2):
        noise = np.diff(noise, prepend=0)
    env = np.exp(-np.arange(n) / sr / (0.09 if open_ else 0.02))
    return amp * noise * env


def clap(sr, amp=0.5):
    n = int(0.15 * sr)
    out = np.zeros(n)
    for offset in (0, 0.010, 0.022):
        o = int(offset * sr)
        burst = np.random.uniform(-1, 1, n - o)
        env = np.exp(-np.arange(n - o) / sr / 0.03)
        out[o:] += burst * env
    # leve passa-banda (diferença de médias) pra dar corpo de "palma"
    kernel = np.array([1, 2, 1]) / 4.0
    out = np.convolve(out, kernel, mode="same")
    return amp * out / np.max(np.abs(out) + 1e-9)


def subbass(t0, t1, freq=48, amp=0.5, vibrato=0.0):
    t = t_axis(t0, t1)
    f = freq + vibrato * np.sin(2 * np.pi * 0.5 * t)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(phase)


def pluck(sr, freq, dur=0.18, amp=0.28):
    n = int(dur * sr)
    t = np.arange(n) / sr
    tone = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
    env = np.exp(-t / 0.09)
    return amp * tone * env


def mix_at(buf, sound, t_start_sec):
    i0 = int(round(t_start_sec * SR))
    i1 = min(len(buf), i0 + len(sound))
    if i0 >= len(buf):
        return
    buf[i0:i1] += sound[: i1 - i0]


def main():
    n_total = int(DURATION * SR)
    buf = np.zeros(n_total, dtype=np.float64)

    # --- 1) GANCHO (0 -> T_DROP): sub-bass crescente + hats esparsos ---
    hook_bass = subbass(0, T_DROP, freq=44, amp=0.22, vibrato=1.5)
    fade_in = np.linspace(0, 1, len(hook_bass)) ** 1.5
    mix_at(buf, hook_bass * fade_in, 0)

    t = 0.0
    step = BEAT * 2  # hats esparsos, a cada meia nota
    while t < T_DROP - 0.05:
        mix_at(buf, hihat(SR, amp=0.15 + 0.1 * (t / T_DROP)), t)
        t += step

    # --- 2) GROOVE (T_DROP -> T_RISER): kick/hat/clap/arpejo ---
    arp_notes = [110.00, 130.81, 146.83, 164.81, 196.00]  # A2 C#3 D3 E3 G3 (energético, sem ficar "triste")
    beat_i = 0
    t = T_DROP
    arp_idx = 0
    while t < T_RISER:
        phase_in_bar = beat_i % 4
        # kick nos tempos 1 e 3 (four-on-the-floor "quebrado")
        if phase_in_bar in (0, 2):
            mix_at(buf, kick(SR, amp=0.95), t)
        # clap nos tempos 2 e 4
        if phase_in_bar in (1, 3):
            mix_at(buf, clap(SR, amp=0.5), t)
        # hi-hats em colcheias
        mix_at(buf, hihat(SR, amp=0.28, open_=(phase_in_bar == 3)), t)
        mix_at(buf, hihat(SR, amp=0.18), t + BEAT / 2)
        # arpejo sincopado (entra a cada 2 tempos, some energia melódica)
        if phase_in_bar in (0, 2):
            f = arp_notes[arp_idx % len(arp_notes)]
            mix_at(buf, pluck(SR, f, amp=0.22), t + BEAT / 4)
            arp_idx += 1
        beat_i += 1
        t += BEAT

    groove_bass = subbass(T_DROP, T_RISER, freq=48, amp=0.32)
    mix_at(buf, groove_bass, T_DROP)

    # --- 3) RISER (T_RISER -> T_IMPACT): sweep + hats acelerando ---
    riser_dur = T_IMPACT - T_RISER
    tt = t_axis(0, riser_dur)
    sweep_noise = np.random.uniform(-1, 1, len(tt))
    # filtro passa-alta progressivo simples (diferenciação com peso crescente)
    diffed = np.diff(sweep_noise, prepend=0)
    mixw = np.linspace(0, 1, len(tt))
    sweep = sweep_noise * (1 - mixw) + diffed * mixw
    env = np.linspace(0.05, 1.0, len(tt)) ** 1.3
    riser_tone_freq = np.linspace(180, 900, len(tt))
    riser_tone = np.sin(2 * np.pi * np.cumsum(riser_tone_freq) / SR)
    riser = (0.35 * sweep + 0.25 * riser_tone) * env
    mix_at(buf, riser, T_RISER)

    t = T_RISER
    interval = BEAT
    while t < T_IMPACT:
        mix_at(buf, hihat(SR, amp=0.2 + 0.5 * (t - T_RISER) / riser_dur), t)
        interval = max(BEAT / 8, interval * 0.72)
        t += interval

    # --- 4) IMPACTO (no T_IMPACT): thump grave + estalo, entrada do CTA ---
    imp_n = int(0.5 * SR)
    ti = np.arange(imp_n) / SR
    imp_tone = np.sin(2 * np.pi * 55 * ti) * np.exp(-ti / 0.35)
    imp_click = np.random.uniform(-1, 1, imp_n) * np.exp(-ti / 0.02)
    impact = 0.9 * imp_tone + 0.5 * imp_click
    mix_at(buf, impact, T_IMPACT)

    # leve "duck" (abaixa o que vinha antes) bem no instante do impacto
    duck_n = int(0.12 * SR)
    i0 = int(T_IMPACT * SR)
    if i0 > duck_n:
        ramp = np.linspace(1.0, 0.4, duck_n)
        buf[i0 - duck_n:i0] *= ramp

    # --- 5) CTA (T_IMPACT -> fim): pad grave sustentado + fade out limpo ---
    cta_bass = subbass(T_IMPACT, T_END, freq=41, amp=0.30, vibrato=0.8)
    mix_at(buf, cta_bass, T_IMPACT)
    t = T_IMPACT + BEAT
    while t < T_END - 0.3:
        mix_at(buf, hihat(SR, amp=0.16), t)
        t += BEAT * 2

    fade_len = int(0.45 * SR)
    if fade_len < n_total:
        buf[-fade_len:] *= np.linspace(1, 0, fade_len)

    # --- normalização e limitador simples ---
    peak = np.max(np.abs(buf)) + 1e-9
    buf = buf / peak * 0.92
    buf = np.tanh(buf * 1.15) / np.tanh(1.15)  # soft-clip suave

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pcm = np.clip(buf, -1.0, 1.0)
    pcm16 = (pcm * 32767).astype(np.int16)
    wavfile.write(OUT, SR, pcm16)
    print(f"trilha gerada em: {OUT} ({DURATION:.2f}s)")


if __name__ == "__main__":
    main()
