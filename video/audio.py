"""Original synthesized score for the Streamline film. 120 BPM, F minor -> Ab major.
Every hit is placed on the same cue times the visuals use (cues.json)."""
import json
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 60.0
N = int(SR * DUR)
cues = json.load(open("cues.json"))
rs = np.random.default_rng(3)

buses = {k: np.zeros((N, 2)) for k in ["dry", "verb", "duck"]}


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def filt(x, kind, f, order=2):
    if kind == "bp":
        sos = butter(order, [f[0] / (SR / 2), f[1] / (SR / 2)], "band", output="sos")
    else:
        sos = butter(order, f / (SR / 2), kind, output="sos")
    return sosfilt(sos, x)


def put(sig, at, gain=1.0, pan=0.0, bus="dry"):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buses[bus][i : i + len(sig), 0] += sig * gain * l * 1.414
    buses[bus][i : i + len(sig), 1] += sig * gain * r * 1.414


def env_adsr(n, a, d, s, r, hold):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    h = max(0, int(hold * SR) - a - d)
    e = np.concatenate([np.linspace(0, 1, max(a, 1)), np.linspace(1, s, max(d, 1)), np.full(h, s), np.linspace(s, 0, max(r, 1))])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def saw(f, t, ph=0.0):
    return 2 * ((f * t + ph) % 1.0) - 1


# ---------------------------------------------------------------- instruments
def kick(g=1.0):
    t = tt(0.55)
    f = 44 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 6.5)
    s += filt(rs.standard_normal(len(t)), "hp", 2500) * np.exp(-t * 90) * 0.35
    return np.tanh(s * 1.6) * g


def clap():
    t = tt(0.35)
    n = filt(rs.standard_normal(len(t)), "bp", (900, 3200))
    e = np.zeros(len(t))
    for o in (0, 0.011, 0.022):
        e += (t >= o) * np.exp(-np.clip(t - o, 0, None) * 140)
    e += (t >= 0.03) * np.exp(-np.clip(t - 0.03, 0, None) * 14) * 0.5
    return n * e * 0.6


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    return filt(rs.standard_normal(len(t)), "hp", 7500) * np.exp(-t * (14 if open_ else 70)) * 0.35


def pluck(m, dur=0.45, bright=2.5):
    t = tt(dur)
    f = mtof(m)
    mod = np.sin(2 * np.pi * f * 2 * t) * bright * np.exp(-t * 9)
    return np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 7) * np.minimum(1, t * 400)


def blip(f, dur=0.12):
    t = tt(dur)
    return np.sin(2 * np.pi * f * t * (1 + 0.5 * np.exp(-t * 60))) * np.exp(-t * 30) * np.minimum(1, t * 800)


def pad(notes, dur, a=0.6, r=1.2, cutoff=2200, detune=0.12):
    t = tt(dur + r)
    s = np.zeros(len(t))
    for m in notes:
        for k in range(5):
            d = (k - 2) * detune / 2
            s += saw(mtof(m + d), t, rs.random())
    s = filt(s / (len(notes) * 5), "lp", cutoff, 2)
    return s * env_adsr(len(t), a, 0.3, 0.8, r, dur)


def bassnote(m, dur):
    t = tt(dur)
    f = mtof(m)
    s = filt(saw(f, t), "lp", 520, 2) * 0.7 + np.sin(2 * np.pi * f / 2 * t) * 0.8
    return s * env_adsr(len(t), 0.004, 0.12, 0.55, 0.05, dur - 0.05)


def boom(g=1.0):
    t = tt(2.6)
    f = 30 + 60 * np.exp(-t * 5)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    s += filt(rs.standard_normal(len(t)), "lp", 300) * np.exp(-t * 3) * 0.5
    return np.tanh(s * 1.4) * g


def crash(dur=2.4):
    t = tt(dur)
    return filt(rs.standard_normal(len(t)), "hp", 3500) * np.exp(-t * 2.2) * 0.35


def sweep_noise(dur, f0, f1, shape="rise"):
    """noise swept through a band-pass by overlap-add."""
    n = int(dur * SR)
    out = np.zeros(n + 4096)
    hop, win = 1024, np.hanning(2048)
    noise = rs.standard_normal(n + 4096)
    for i in range(0, n, hop):
        k = i / n
        fc = f0 * (f1 / f0) ** k
        seg = filt(noise[i : i + 2048], "bp", (fc * 0.7, min(fc * 1.4, 20000)))
        out[i : i + 2048] += seg * win
    out = out[:n]
    t = np.linspace(0, 1, n)
    amp = t**2.2 if shape == "rise" else np.sin(np.pi * t) ** 2
    return out * amp


def riser(dur, g=0.5):
    s = sweep_noise(dur, 300, 9000) * 0.9
    t = tt(dur)
    f = 180 * (8 ** (t / dur))
    s += np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2 * 0.25
    return s * g


def whoosh(dur, g=0.5):
    return sweep_noise(dur, 400, 5000, "bell") * g


def reverse_swell(dur):
    return sweep_noise(dur, 200, 6000) * 0.7


# ---------------------------------------------------------------- arrangement
BEAT = 0.5
CH = {  # voicings (pad) + bass root
    "Fm": ([53, 56, 60, 63, 67], 41),
    "Db": ([49, 53, 56, 60, 63], 37),
    "Ab": ([51, 56, 60, 63, 67], 44),
    "Eb": ([51, 55, 58, 62, 65], 39),
}
PROG = ["Fm", "Db", "Ab", "Eb"]


def chord_at(t):
    bar = int((t - 16) // 2)
    return PROG[bar % 4]


kicks = []

# 0-4 prologue ----------------------------------------------------------
put(pad(CH["Fm"][0], 3.8, a=2.5, r=0.6, cutoff=900), 0.0, 0.35, bus="verb")
for b in np.arange(0.5, 4.0, 0.5):
    put(blip(1760, 0.05), b, 0.18, 0.2)
    put(np.sin(2 * np.pi * 55 * tt(0.4)) * np.exp(-tt(0.4) * 9), b, 0.25)
s = "every team runs on workflows."
for i in range(len(s)):
    tc = 0.6 + (i + 1) / len(s) * 1.25
    put(filt(rs.standard_normal(int(0.018 * SR)), "bp", (2000, 6000)) * np.exp(-tt(0.018) * 200), tc, 0.25, rs.uniform(-0.4, 0.4))
put(riser(1.4, 0.45), 2.6)
for g in np.arange(3.2, 4.0, 0.0625):  # stutter glitch
    put(blip(rs.uniform(300, 2400), 0.03), g, 0.12, rs.uniform(-0.7, 0.7))

# 4-12 friction ----------------------------------------------------------
for b in np.arange(4.0, 12.0, BEAT):
    kicks.append(b)
    put(kick(1.0), b, 0.9)
for b in np.arange(4.0, 12.0, 0.25):
    put(hat(), b, 0.45 if (b * 4) % 2 else 0.25, 0.3)
for b in np.arange(4.0, 12.0, 0.25):  # tense bass: F vs Gb
    m = 29 + (1 if int(b * 4) % 8 in (5, 6) else 0)
    put(bassnote(m + 12, 0.22), b, 0.55, bus="duck")
for st in cues["slams"]:
    cl = pad([53, 54, 60, 61, 66], 0.2, a=0.003, r=0.18, cutoff=5000, detune=0.3)
    put(cl, st, 0.9, bus="verb")
    put(cl, st, 0.5)
for i, ct in enumerate(cues["cards"]):
    put(blip([1568, 1760, 2093, 1397, 2349][i % 5], 0.14), ct, 0.22, [-0.6, 0.5, -0.2, 0.7, -0.5][i % 5], bus="verb")
put(riser(3.0, 0.7), 9.0)

# 12-16 shift -------------------------------------------------------------
put(reverse_swell(1.2), 12.0, 0.9)
put(boom(1.0), 13.2, 0.9)
put(crash(3.0), 13.2, 0.4, bus="verb")
put(pad([56, 60, 63, 67, 72], 2.4, a=0.3, r=1.0, cutoff=1800), 13.25, 0.32, bus="verb")
for i, (tc, m) in enumerate([(13.45, 72), (13.7, 75), (13.95, 79), (14.3, 80), (14.65, 84)]):
    put(pluck(m, 1.2, 1.5), tc, 0.22, (-0.4, 0.4)[i % 2], bus="verb")
put(riser(0.85, 0.6), 15.05)

# 16 identity impact -----------------------------------------------------
put(boom(1.2), 16.0, 1.0)
put(kick(1.2), 16.0, 1.0)
put(crash(3.0), 16.0, 0.6, bus="verb")
put(pad(CH["Fm"][0] + [72], 1.6, a=0.005, r=1.6, cutoff=4000), 16.0, 0.5, bus="verb")
kicks.append(16.0)

# 16-52 groove -----------------------------------------------------------
for bar_t in np.arange(16.0, 52.0, 2.0):
    ch = chord_at(bar_t + 0.01)
    notes, root = CH[ch]
    cut = 1500 if bar_t < 22 else 2600
    put(pad(notes, 1.95, a=0.08, r=0.5, cutoff=cut), bar_t, 0.28, bus="duck")
    put(pad(notes, 1.95, a=0.08, r=0.5, cutoff=cut), bar_t, 0.12, bus="verb")
    if bar_t >= 18:
        for k in range(8):  # bass 8ths, octave jumps
            m = root - 12 + (12 if k in (3, 7) else 0)
            put(bassnote(m, 0.22), bar_t + k * 0.25, 0.6, bus="duck")
    if bar_t >= 18 or bar_t >= 16 and False:
        arp = sorted(notes) + [notes[1] + 12]
        pattern = [0, 2, 4, 5, 3, 1, 4, 2, 0, 3, 5, 4, 2, 1, 3, 5]
        for k in range(16):
            put(pluck(arp[pattern[k] % len(arp)] + 12, 0.35, 2.2), bar_t + k * 0.125, 0.10, (-0.5, 0.5)[k % 2], bus="verb")
for b in np.arange(16.5, 52.0, BEAT):
    if b < 18 and b % 1:
        continue
    if 50.5 <= b:
        continue
    kicks.append(b)
    put(kick(), b, 0.85)
for b in np.arange(18.0, 51.0, BEAT):
    if int(round(b / BEAT)) % 2 == 1:
        put(clap(), b, 0.6, 0.05, bus="verb")
        put(clap(), b, 0.5)
for b in np.arange(17.0, 51.5, 0.125):
    k = int(round(b / 0.125)) % 4
    put(hat(open_=(k == 2)), b, [0.18, 0.1, 0.35, 0.1][k], 0.35 if k % 2 else -0.25)

# 21.55 lime cut -> 22
put(riser(0.45, 0.6), 21.55)
put(whoosh(0.5, 0.5), 21.7)
put(boom(0.6), 22.0, 0.7)
# build UI foley
for nt in cues["nodes"]:
    put(blip(880, 0.12), nt, 0.3, 0.1)
    put(pluck(84, 0.3, 1), nt, 0.12, bus="verb")
for tc, f in [(23.65, 2400), (24.4, 1800), (26.47, 2600)]:
    put(filt(rs.standard_normal(int(0.02 * SR)), "bp", (1500, 5000)) * np.exp(-tt(0.02) * 180), tc, 0.6)
    put(blip(f, 0.05), tc, 0.25)
put(pad([72, 75, 79, 84], 0.8, a=0.01, r=0.8, cutoff=6000), 26.5, 0.2, bus="verb")
for r in cues["runs"]:
    tc = r["t0"] + 3 * cues["seg"]
    if tc < 36:
        put(blip(2093 if r["br"] == "n4" else 1568, 0.08), tc, 0.12, 0.4 if r["br"] == "n4" else -0.4, bus="verb")
put(whoosh(0.8, 0.9), 35.2)
put(kick(1.1), 36.0, 0.5)

# stats odometer ticks
for t0, t1 in [(36.05, 37.6), (38.65, 40.1), (41.35, 42.9)]:
    tc = t0
    while tc < t1:
        put(blip(3200, 0.012), tc, 0.12, rs.uniform(-0.3, 0.3))
        tc += 0.025 + 0.12 * ((tc - t0) / (t1 - t0)) ** 2
for x in (38.6, 41.3):
    put(whoosh(0.5, 0.35), x - 0.25)

# 44 connect
put(whoosh(0.9, 0.4), 43.7)
put(pad([75, 79, 82, 87], 1.5, a=0.01, r=1.5, cutoff=7000), 44.0, 0.15, bus="verb")
for i in range(21):
    put(blip(mtof([72, 75, 79, 80, 84, 87, 91][i % 7]), 0.1), 44.2 + i * 0.05 + 0.15, 0.09, np.sin(i) * 0.8, bus="verb")
put(riser(1.7, 0.8), 50.3)
put(whoosh(1.6, 0.4), 50.3)

# 52 momentum -----------------------------------------------------------
put(boom(1.1), 52.0, 1.0)
put(kick(1.2), 52.0, 1.0)
put(crash(3.0), 52.0, 0.5, bus="verb")
put(pad([41, 53, 56, 60, 63, 67], 2.9, a=0.01, r=0.6, cutoff=3000), 52.0, 0.4, bus="verb")
put(pad([37, 49, 53, 56, 60, 63], 1.0, a=0.01, r=0.6, cutoff=3000), 54.0, 0.3, bus="verb")
for tc, m in [(52.15, 77), (52.95, 80), (53.2, 84), (53.45, 87)]:
    put(pluck(m, 1.2, 1.4), tc, 0.18, bus="verb")
put(riser(0.9, 0.6), 54.1)
put(boom(1.2), 55.0, 1.0)
put(kick(1.2), 55.0, 1.0)
put(crash(4.0), 55.0, 0.55, bus="verb")
final = [44, 56, 60, 63, 67, 70, 72]  # Ab maj9 — resolve to the major
put(pad(final, 4.0, a=0.02, r=1.2, cutoff=3500), 55.0, 0.45, bus="verb")
put(pad(final, 4.0, a=0.02, r=1.2, cutoff=3500), 55.0, 0.2)
for i, m in enumerate([80, 84, 87, 91, 87, 84, 80, 79]):
    put(pluck(m, 1.0, 1.2), 56.2 + i * 0.375, 0.09, (-0.6, 0.6)[i % 2], bus="verb")
put(np.sin(2 * np.pi * 44 * tt(4)) * env_adsr(int(4 * SR), 0.02, 0.5, 0.6, 1.5, 2.5), 55.0, 0.4)
for st in (57.1, 58.5):
    put(sweep_noise(0.8, 3000, 12000, "bell"), st, 0.12)
    put(blip(3136, 0.3), st + 0.4, 0.08, bus="verb")

# ---------------------------------------------------------------- mix
t = np.arange(N) / SR
duck = np.ones(N)
for k in kicks:
    i = int(k * SR)
    seg = min(N - i, int(0.45 * SR))
    duck[i : i + seg] = np.minimum(duck[i : i + seg], 1 - 0.65 * np.exp(-np.arange(seg) / SR * 9))


def ir(seed, dur=2.8):
    r = np.random.default_rng(seed)
    x = r.standard_normal(int(dur * SR)) * np.exp(-np.arange(int(dur * SR)) / SR * 2.4)
    return filt(x, "lp", 6000) * 0.08


verb_in = buses["verb"] + buses["duck"] * 0.25
wet = np.stack([fftconvolve(verb_in[:, 0], ir(1))[:N], fftconvolve(verb_in[:, 1], ir(2))[:N]], 1)
mixed = buses["dry"] + buses["duck"] * duck[:, None] + buses["verb"] * 0.6 + wet * 0.9
mixed = filt(mixed.T, "hp", 25).T
fade = np.clip((DUR - t) / 0.9, 0, 1) ** 1.5
mixed *= fade[:, None]
mixed = mixed / np.percentile(np.abs(mixed), 99.9) * 0.75
mixed = np.tanh(mixed)
mixed /= np.max(np.abs(mixed)) / 0.89
wavfile.write("score.wav", SR, (mixed * 32767).astype(np.int16))
print("peak ok, rms", float(np.sqrt(np.mean(mixed**2))))
