"""Original synthesized score for the Streamline Workflows film. 120 BPM, F minor -> Ab major.
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
CH = {  # warm voicings (pad) + bass root
    "Ab": ([56, 60, 63, 67, 70], 44),
    "Fm": ([53, 56, 60, 63, 67], 41),
    "Db": ([53, 56, 60, 61, 65], 37),
    "Eb": ([55, 58, 62, 63, 67], 39),
}
PROG = ["Ab", "Fm", "Db", "Eb"]
PENTA = [68, 70, 72, 75, 77, 80, 82, 84]
kicks = []


def soft_kick(g=0.7):
    return kick(1.0) * g


def tick(g=1.0, f=(2500, 7000)):
    n = int(0.015 * SR)
    return filt(rs.standard_normal(n), "bp", f) * np.exp(-np.arange(n) / SR * 260) * g


def woodblock(m):
    t = tt(0.12)
    f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 45)


# 0-12 the problem ------------------------------------------------------
put(pad([41, 53, 56, 60], 11.8, a=4.0, r=0.4, cutoff=700), 0.0, 0.32, bus="verb")
for i, nt in enumerate(cues["nodes"]):
    put(woodblock(PENTA[i % 8] - 12 + (12 if i % 5 == 0 else 0)), nt, 0.10, rs.uniform(-0.7, 0.7), bus="verb")
tc = 3.0  # unquantised ticking that thickens
while tc < 11.95:
    put(tick(rs.uniform(0.2, 0.5)), tc, 0.5, rs.uniform(-0.8, 0.8))
    tc += max(0.04, 0.45 * np.exp(-(tc - 3) / 3.2)) * rs.uniform(0.5, 1.5)
for b in np.arange(5.0, 12.0, BEAT):  # heartbeat
    kicks.append(b)
    put(soft_kick(0.45 if b < 9 else 0.6), b, 0.8)
for ct in cues["chips"]:
    put(blip(1318, 0.1), ct, 0.14, 0.3, bus="verb")
    put(tick(0.6, (1500, 4000)), ct, 0.5)
put(riser(1.9, 0.5), 10.1)

# 12-17 the fix: everything lands on the grid -----------------------------
for col in range(9):
    put(pluck([60, 63, 65, 67, 70, 72, 75, 77, 79][col], 0.5, 1.4), 12.0 + col * 0.05 + 0.5, 0.20, -0.8 + col * 0.2, bus="verb")
    put(tick(0.7), 12.0 + col * 0.05 + 0.5, 0.5, -0.8 + col * 0.2)
put(pad(CH["Ab"][0], 2.6, a=0.4, r=0.6, cutoff=1600), 12.6, 0.28, bus="verb")
for col in range(9):  # ripple arpeggio
    put(pluck([72, 75, 77, 79, 82, 84, 87, 89, 91][col], 0.6, 1.0), 13.4 + col / 11, 0.12, -0.8 + col * 0.2, bus="verb")
for b in np.arange(12.5, 16.0, 0.25):
    put(hat(), b, 0.18 if b % 0.5 else 0.08, 0.3)
put(riser(1.15, 0.65), 14.85)
t_ = tt(1.15)
put(np.sin(2 * np.pi * np.cumsum(220 * 4 ** (t_ / 1.15)) / SR) * (t_ / 1.15) ** 1.5 * 0.25, 14.85, 1.0, bus="verb")
put(boom(0.9), 16.0, 0.8)
put(soft_kick(1.0), 16.0, 0.9)
put(crash(3.0), 16.0, 0.35, bus="verb")
put(pad([44, 56, 60, 63, 67, 70, 75], 1.2, a=0.005, r=2.2, cutoff=3200), 16.0, 0.45, bus="verb")
for k in range(12):
    put(tick(0.5), 16.0 + k * 0.035, 0.35, rs.uniform(-0.8, 0.8))
for i, m in enumerate([80, 84, 87]):
    put(pluck(m, 1.6, 0.8), 17.05 + i * 0.12, 0.13, (-0.3, 0, 0.3)[i], bus="verb")
put(pluck(79, 1.4, 0.8), 18.25, 0.12, bus="verb")
put(pad(CH["Ab"][0], 3.0, a=0.8, r=0.8, cutoff=1400), 17.2, 0.2, bus="verb")
put(whoosh(0.7, 0.45), 20.3)
put(whoosh(0.6, 0.35), 20.85)
put(boom(0.6), 21.4, 0.6)

# 21.4-41 what we do: the groove ------------------------------------------
for bar_t in np.arange(22.0, 41.0, 2.0):
    ch = PROG[int((bar_t - 22) // 2) % 4]
    notes, root = CH[ch]
    put(pad(notes, 1.95, a=0.1, r=0.5, cutoff=1900), bar_t, 0.24, bus="duck")
    put(pad(notes, 1.95, a=0.1, r=0.5, cutoff=1900), bar_t, 0.10, bus="verb")
    if bar_t >= 24.0:
        for k in range(8):
            put(bassnote(root - 12 + (12 if k in (3, 6) else 0), 0.22), bar_t + k * 0.25, 0.5, bus="duck")
    arp = sorted(notes)
    pat = [0, 2, 4, 3, 1, 3, 4, 2]
    for k in range(8):
        put(pluck(arp[pat[k]] + 12, 0.4, 1.3), bar_t + k * 0.25, 0.08, (-0.5, 0.5)[k % 2], bus="verb")
for b in np.arange(24.5, 41.0, BEAT):
    kicks.append(b)
    put(soft_kick(0.75), b, 0.8)
    if int(round(b / BEAT)) % 2 == 0:
        put(clap(), b + 0.5, 0.28, 0.1, bus="verb")
for b in np.arange(24.5, 41.0, 0.125):
    k = int(round(b / 0.125)) % 4
    put(hat(open_=(k == 2)), b, [0.12, 0.06, 0.2, 0.06][k], 0.35 if k % 2 else -0.25)
for p0 in cues["pillars"]:
    put(whoosh(0.5, 0.25), p0 - 0.25)
    put(pluck(84, 1.0, 1.0), p0 + 0.08, 0.12, bus="verb")
# P1: handoffs straighten
put(riser(0.7, 0.35), 27.1)
put(pad([75, 79, 82, 87], 0.8, a=0.01, r=1.2, cutoff=5000), 27.8, 0.14, bus="verb")
# P2: blocks snap in
for i in range(8):
    tc = 30.0 + 0.7 + i * 0.09 + 0.4
    put(woodblock(72 + [0, 3, 5, 7, 10, 12, 15, 17][i]), tc, 0.14, -0.6 + i * 0.17, bus="verb")
    put(tick(0.5), tc, 0.35)
put(pad([80, 84, 87], 0.5, a=0.01, r=1.0, cutoff=6000), 33.55, 0.16, bus="verb")
# P3: three become one
put(whoosh(0.9, 0.4), 37.7)
put(pad([68, 72, 75, 79, 84], 0.9, a=0.01, r=1.4, cutoff=5000), 38.6, 0.2, bus="verb")
put(sweep_noise(1.0, 2000, 9000, "bell"), 38.5, 0.1)
# iris
put(whoosh(0.8, 0.45), 40.6)
put(boom(0.5), 41.4, 0.5)

# 41.4-47.4 impact --------------------------------------------------------
put(pad([44, 56, 60, 63, 67], 2.9, a=0.2, r=0.4, cutoff=1500), 41.4, 0.3, bus="verb")
for tc, m in [(41.45, 72), (41.85, 75), (42.6, 79)]:
    put(pluck(m, 1.2, 1.0), tc, 0.13, bus="verb")
for bar_t in (44.0, 46.0):
    notes, root = CH[PROG[int((bar_t - 44) // 2) % 4]]
    put(pad(notes, 1.95, a=0.05, r=0.5, cutoff=2200), bar_t, 0.24, bus="duck")
    for k in range(8):
        put(bassnote(root - 12 + (12 if k in (3, 6) else 0), 0.22), bar_t + k * 0.25, 0.5, bus="duck")
for b in np.arange(44.0, 47.0, BEAT):
    kicks.append(b)
    put(soft_kick(0.8), b, 0.8)
for b in np.arange(44.0, 47.3, 0.125):
    put(hat(), b, 0.1, 0.3)
for t0 in (44.3, 44.55):
    tc = t0
    while tc < t0 + 1.6:
        put(tick(0.5, (3000, 8000)), tc, 0.4, rs.uniform(-0.3, 0.3))
        tc += 0.03 + 0.14 * ((tc - t0) / 1.6) ** 2
put(whoosh(0.6, 0.35), 47.0)

# 47.4-54 one line through the noise --------------------------------------
put(whoosh(0.6, 0.4), 47.35)
for k in range(40):
    put(woodblock(rs.choice(PENTA) - 12), 47.75 + rs.random() * 0.8, 0.05, rs.uniform(-0.9, 0.9), bus="verb")
noise_bed = filt(rs.standard_normal(int(2.4 * SR)), "bp", (800, 5000)) * env_adsr(int(2.4 * SR), 0.6, 0.2, 0.8, 0.7, 1.7)
put(noise_bed, 47.8, 0.08)
put(pad([53, 54, 60, 61], 2.0, a=0.5, r=0.4, cutoff=1200, detune=0.35), 47.8, 0.2, bus="verb")
tc = 47.9
while tc < 49.6:
    put(tick(rs.uniform(0.2, 0.5)), tc, 0.45, rs.uniform(-0.9, 0.9))
    tc += rs.uniform(0.03, 0.1)
put(pad(CH["Ab"][0], 1.2, a=0.3, r=0.5, cutoff=1400), 49.2, 0.25, bus="verb")
put(riser(0.9, 0.55), 50.1)
t_ = tt(0.9)
put(np.sin(2 * np.pi * np.cumsum(330 * 3 ** (t_ / 0.9)) / SR) * (t_ / 0.9) ** 1.5 * 0.22, 50.1, 1.0, bus="verb")
put(boom(0.8), 51.0, 0.75)
put(soft_kick(1.0), 51.0, 0.85)
put(pad([44, 56, 60, 63, 67, 70, 72], 1.8, a=0.005, r=1.2, cutoff=3200), 51.0, 0.4, bus="verb")
for tc, m in [(50.85, 79), (51.1, 82), (51.35, 84)]:
    put(pluck(m, 1.2, 1.0), tc, 0.12, bus="verb")
put(whoosh(0.8, 0.4), 53.3)

# 54-60 end card ----------------------------------------------------------
for i in range(7):
    put(woodblock([68, 72, 75, 80, 75, 79, 84][i]), 53.95 + i * 0.05, 0.12, -0.6 + i * 0.2, bus="verb")
final = [44, 56, 60, 63, 67, 70, 72]
put(pad(final, 4.4, a=0.02, r=1.4, cutoff=3000), 54.2, 0.42, bus="verb")
put(pad(final, 4.4, a=0.02, r=1.4, cutoff=3000), 54.2, 0.18)
put(np.sin(2 * np.pi * 51.9 * tt(5)) * env_adsr(int(5 * SR), 0.02, 0.6, 0.6, 1.8, 3.2), 54.2, 0.35)
put(soft_kick(0.9), 54.2, 0.8)
for i, m in enumerate([80, 84, 87, 91, 87, 84]):
    put(pluck(m, 1.0, 1.0), 55.0 + i * 0.25, 0.08, (-0.5, 0.5)[i % 2], bus="verb")
put(soft_kick(0.6), 55.7, 0.6)
put(blip(2093, 0.25), 55.75, 0.08, bus="verb")

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
