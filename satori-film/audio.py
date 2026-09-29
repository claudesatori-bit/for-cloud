"""Original synthesized score for the Satori Craft film. 120 BPM, F minor -> Ab major.
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
CH = {
    "Fm": ([53, 56, 60, 63, 67], 41),
    "Db": ([49, 53, 56, 60, 63], 37),
    "Ab": ([51, 56, 60, 63, 67], 44),
    "Eb": ([51, 55, 58, 62, 65], 39),
}
PROG = ["Fm", "Db", "Ab", "Eb"]
kicks = []


def tick(g=1.0, f=(2500, 7000)):
    n = int(0.015 * SR)
    return filt(rs.standard_normal(n), "bp", f) * np.exp(-np.arange(n) / SR * 260) * g


def woodblock(m):
    t = tt(0.12)
    f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 45)


def bowl(m, dur=5.0):
    """singing-bowl / temple bell: inharmonic partials, slow beating."""
    t = tt(dur)
    f = mtof(m)
    s = np.zeros(len(t))
    for ratio, amp, dec in [(1, 1, 0.7), (2.71, 0.5, 1.1), (5.18, 0.25, 1.8), (8.4, 0.12, 2.6)]:
        s += amp * np.sin(2 * np.pi * f * ratio * t + 0.3 * np.sin(2 * np.pi * 3.1 * t)) * np.exp(-t * dec)
    return s * np.minimum(1, t * 300) * 0.5


def brush(dur):
    """a dry brush stroke across paper."""
    n = int(dur * SR)
    x = filt(rs.standard_normal(n), "bp", (1200, 7000))
    tex = 0.6 + 0.4 * np.abs(filt(rs.standard_normal(n), "lp", 40)) * 3
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.7 * np.linspace(1, 0.35, n)
    return x * tex * e * 0.5


def thud(g=1.0):
    t = tt(0.6)
    f = 60 + 90 * np.exp(-t * 40)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    s += filt(rs.standard_normal(len(t)), "lp", 900) * np.exp(-t * 30) * 0.8
    return np.tanh(s * 2) * g


# ---------------------------------------------------------------- arrangement
# 0-4 countdown ---------------------------------------------------------
put(np.sin(2 * np.pi * 43.65 * tt(4.0)) * env_adsr(int(4 * SR), 0.01, 0.2, 0.7, 0.3, 3.7), 0.0, 0.3)
put(pad(CH["Fm"][0], 3.9, a=0.05, r=0.3, cutoff=700), 0.0, 0.3, bus="verb")
for b in np.arange(0.0, 4.0, BEAT):
    put(blip(1760, 0.05), b, 0.16, 0.2)
    put(kick(0.5), b, 0.45 if b >= 2 else 0.3)
    kicks.append(b)
for i, tc in enumerate(cues["count"]):
    put(tick(0.8, (3000, 8000)), tc, 0.35, (-0.3, 0.3)[i % 2])
for i, tc in enumerate(cues["chips"]):
    put(pluck(72 + [0, 3, 7, 10, 12, 15, 19, 22][i], 0.4, 2.0), tc, 0.1, (-0.6, 0.6)[i % 2], bus="verb")
put(riser(2.0, 0.55), 2.0)
put(thud(1.0), 3.5, 0.7)
for gl in np.arange(3.4, 4.0, 0.0625):
    put(blip(rs.uniform(300, 2400), 0.03), gl, 0.12, rs.uniform(-0.7, 0.7))

# 4-11.5 the noise --------------------------------------------------------
for b in np.arange(4.0, 11.5, BEAT):
    kicks.append(b)
    put(kick(1.0), b, 0.9)
for b in np.arange(4.0, 11.5, 0.25):
    put(hat(), b, 0.45 if (b * 4) % 2 else 0.25, 0.3)
for b in np.arange(4.0, 11.5, 0.25):
    m = 29 + (1 if int(b * 4) % 8 in (5, 6) else 0)
    put(bassnote(m + 12, 0.22), b, 0.55, bus="duck")
for i, st in enumerate(cues["slams"]):
    cl = pad([53, 54, 60, 61, 66], 0.2, a=0.003, r=0.18, cutoff=5000, detune=0.3)
    put(cl, st, 0.9, bus="verb")
    put(cl, st, 0.5)
    if i % 2 == 1:
        put(clap(), st, 0.5)
for i, ct in enumerate(cues["cards"]):
    put(blip([1568, 1760, 2093, 1397, 2349][i % 5], 0.14), ct, 0.2, [-0.6, 0.5, -0.2, 0.7, -0.5][i % 5], bus="verb")
put(riser(3.0, 0.75), 8.5)
# "Breathe." — everything drops out
put(pad([56, 60, 63, 67], 0.5, a=0.01, r=0.6, cutoff=2000), 11.5, 0.25, bus="verb")
put(reverse_swell(0.7), 11.5, 0.4)

# 12-16 satori ---------------------------------------------------------------
m0, m1 = cues["morph"]
put(boom(0.6), 12.0, 0.5)
put(sweep_noise(m1 - m0, 600, 6000, "rise"), m0, 0.35)  # the tangle pulls taut
tc = m0
while tc < m1:
    put(tick(0.4, (2500, 7000)), tc, 0.25, rs.uniform(-0.8, 0.8))
    tc += 0.02 + 0.09 * (1 - (tc - m0) / (m1 - m0))
put(bowl(56, 6.0), m1, 0.55, bus="verb")  # sunrise
put(bowl(63, 5.0), m1 + 0.05, 0.3, 0.3, bus="verb")
for i, m in enumerate([80, 84, 87]):
    put(pluck(m, 1.2, 1.0), m1 + 0.1 + i * 0.09, 0.1, (-0.4, 0, 0.4)[i], bus="verb")
put(pad([44, 56, 60, 63], 3.0, a=1.2, r=0.8, cutoff=900), 12.6, 0.28, bus="verb")
put(riser(1.0, 0.7), 15.0)
put(reverse_swell(0.6), 15.4, 0.6)

# 16-21 identity ------------------------------------------------------------
put(boom(1.2), 16.0, 1.0)
put(kick(1.2), 16.0, 1.0)
put(crash(3.0), 16.0, 0.5, bus="verb")
put(pad(CH["Fm"][0] + [72], 1.6, a=0.005, r=1.6, cutoff=4000), 16.0, 0.45, bus="verb")
put(bowl(68, 3.0), 16.6, 0.25, bus="verb")
kicks.append(16.0)
for i, m in enumerate([72, 75, 79, 80, 84]):
    put(pluck(m, 1.0, 1.2), 18.05 + i * 0.12, 0.1, (-0.4, 0.4)[i % 2], bus="verb")
for i, m in enumerate([75, 79, 84, 87]):
    put(pluck(m, 1.0, 1.2), 19.0 + i * 0.12, 0.1, (-0.4, 0.4)[i % 2], bus="verb")
for i, tc in enumerate(cues["triple"]):  # Not assembly. Not theatre. Craft.
    cl = pad([56, 60, 63, 67] if i < 2 else [44, 56, 60, 63, 67, 72], 0.3 if i < 2 else 0.5, a=0.003, r=0.4, cutoff=5000)
    put(cl, tc, 0.7, bus="verb")
    put(kick(1.1), tc, 0.8)
    put(thud(0.8 if i < 2 else 1.1), tc, 0.6)
put(boom(0.9), cues["triple"][-1], 0.7)
put(whoosh(0.5, 0.5), 20.75)

# 16-43 groove -------------------------------------------------------------
for bar_t in np.arange(16.0, 42.5, 2.0):
    notes, root = CH[PROG[int((bar_t - 16) // 2) % 4]]
    cut = 1500 if bar_t < 21 else 2800
    put(pad(notes, 1.95, a=0.08, r=0.5, cutoff=cut), bar_t, 0.24, bus="duck")
    put(pad(notes, 1.95, a=0.08, r=0.5, cutoff=cut), bar_t, 0.1, bus="verb")
    if bar_t >= 18:
        for k in range(8):
            put(bassnote(root - 12 + (12 if k in (3, 7) else 0), 0.22), bar_t + k * 0.25, 0.55, bus="duck")
    if bar_t >= 22 and not (30 <= bar_t < 34):
        arp = sorted(notes) + [notes[1] + 12]
        pattern = [0, 2, 4, 5, 3, 1, 4, 2, 0, 3, 5, 4, 2, 1, 3, 5]
        for k in range(16):
            put(pluck(arp[pattern[k] % len(arp)] + 12, 0.35, 2.0), bar_t + k * 0.125, 0.07, (-0.5, 0.5)[k % 2], bus="verb")
for b in np.arange(16.5, 42.5, BEAT):
    if b < 18 and b % 1:
        continue
    if 34.4 <= b < 36.0:  # the service slams carry their own hits
        continue
    kicks.append(b)
    put(kick(), b, 0.8)
for b in np.arange(18.0, 42.5, BEAT):
    if int(round(b / BEAT)) % 2 == 1 and not (34.4 <= b < 36.0):
        put(clap(), b, 0.5, 0.05, bus="verb")
        put(clap(), b, 0.4)
for b in np.arange(17.0, 42.5, 0.125):
    k = int(round(b / 0.125)) % 4
    put(hat(open_=(k == 2)), b, [0.15, 0.07, 0.28, 0.07][k], 0.35 if k % 2 else -0.25)

# implement: 17 configs climb the scale; timeline snaps; go-live hit
PENTA = [68, 70, 72, 75, 77, 80, 82, 84, 87, 89, 92, 94, 96, 99, 101, 104, 106]
for i, tc in enumerate(cues["cfg"]):
    put(woodblock(PENTA[i] - 12), tc, 0.16, -0.7 + i * 0.085, bus="verb")
    put(tick(0.5), tc, 0.3)
put(whoosh(0.9, 0.7), 25.4)
for i, tc in enumerate(cues["phases"]):
    put(blip([880, 988, 1175, 1319, 1480, 1760][i], 0.1), tc, 0.25, bus="verb")
    put(tick(1.0, (1500, 5000)), tc, 0.5)
gl = cues["phases"][-1]
put(boom(0.9), gl, 0.8)
put(crash(2.5), gl, 0.4, bus="verb")
put(pad([56, 60, 63, 67, 72], 1.2, a=0.005, r=1.0, cutoff=5000), gl, 0.3, bus="verb")
put(whoosh(0.5, 0.9), 29.6)

# run: tickets in, tickets resolved
for tc in cues["tickets"]:
    put(blip(1319, 0.08), tc, 0.14, 0.4, bus="verb")
for i, tc in enumerate(cues["resolved"]):
    put(pluck([80, 84, 87, 91][i % 4], 0.6, 1.0), tc, 0.1, -0.3, bus="verb")
put(riser(1.0, 0.5), 33.5)
for i, tc in enumerate(cues["svc"]):
    cl = pad([56, 60, 63, 67] if i < 2 else [53, 56, 60, 65], 0.3, a=0.003, r=0.3, cutoff=5000)
    put(cl, tc, 0.7, bus="verb")
    put(kick(1.1), tc, 0.8)
    put(clap(), tc, 0.4)
put(boom(0.8), cues["svc"][-1], 0.6)

# AI: typing, answers, locks, the stamp
for m in cues["msgs"]:
    if m["user"]:
        for c in range(m["n"]):
            put(tick(rs.uniform(0.4, 0.8), (2500, 6500)), m["t0"] + 0.1 + c / 44, 0.18, rs.uniform(-0.3, 0.3))
    else:
        put(blip(1568, 0.12), m["t0"], 0.2, -0.2, bus="verb")
        put(blip(2093, 0.12), m["t0"] + 0.08, 0.15, 0.2, bus="verb")
for tc in cues["locks"]:
    put(thud(0.6), tc, 0.35)
    put(tick(1.0, (1500, 4000)), tc + 0.02, 0.4)
st = cues["stamp"]
put(reverse_swell(0.5), st - 0.5, 0.5)
put(thud(1.2), st, 1.0)
put(boom(1.3), st, 1.0)
put(crash(3.0), st, 0.45, bus="verb")
put(pad([44, 56, 60, 63, 67], 2.0, a=0.005, r=1.2, cutoff=3000), st, 0.35, bus="verb")
kicks.append(st)

# 42.6-49 proof -------------------------------------------------------------
for i, tc in enumerate(cues["panes"]):
    put(whoosh(0.4, 0.35), tc - 0.1)
    put(kick(1.1), tc + 0.1, 0.9)
    kicks.append(tc + 0.1)
    put(pad([56, 60, 63, 67], 0.3, a=0.003, r=0.3, cutoff=5000), tc + 0.1, 0.5, bus="verb")
    t0 = tc + 0.15
    tcc = t0
    while tcc < t0 + 1.3:
        put(tick(0.5, (3000, 8000)), tcc, 0.35, rs.uniform(-0.3, 0.3))
        tcc += 0.03 + 0.14 * ((tcc - t0) / 1.3) ** 2
for bar_t in np.arange(42.6, 46.4, 0.5):
    if not any(abs(bar_t - (p + 0.1)) < 0.2 for p in cues["panes"]):
        put(kick(0.8), bar_t, 0.6)
for b in np.arange(42.6, 46.4, 0.25):
    put(hat(), b, 0.2, 0.3)
for bar_t in (42.5, 44.5):
    notes, root = CH[PROG[int((bar_t - 16) // 2) % 4]]
    put(pad(notes, 1.95, a=0.08, r=0.5, cutoff=3000), bar_t, 0.2, bus="duck")
    for k in range(8):
        put(bassnote(root - 12, 0.22), bar_t + k * 0.25, 0.5, bus="duck")
po = cues["paneOut"]
put(whoosh(0.6, 0.6), po - 0.1)
put(bowl(60, 3.0), po + 0.3, 0.3, bus="verb")
put(pad([44, 56, 60, 63, 67], 2.2, a=0.4, r=0.6, cutoff=1600), po + 0.3, 0.3, bus="verb")
put(riser(1.0, 0.5), 48.0)

# 49-54 reach ---------------------------------------------------------------
put(boom(0.7), 49.0, 0.6)
for b in np.arange(49.0, 53.0, BEAT):
    put(kick(0.9), b, 0.7)
    kicks.append(b)
for b in np.arange(49.0, 53.0, 0.25):
    put(hat(), b, 0.18, 0.3)
for bar_t in np.arange(49.0, 53.0, 2.0):
    notes, root = CH[["Db", "Ab"][int((bar_t - 49) // 2)]]
    put(pad(notes, 1.95, a=0.1, r=0.6, cutoff=2600), bar_t, 0.26, bus="duck")
    for k in range(8):
        put(bassnote(root - 12 + (12 if k in (3, 7) else 0), 0.22), bar_t + k * 0.25, 0.5, bus="duck")
for i, tc in enumerate(cues["cities"]):
    put(pluck([80, 82, 84, 87, 89, 92, 94, 96, 99, 101][i], 0.8, 1.2), tc, 0.12, -0.8 + i * 0.18, bus="verb")
    put(woodblock(PENTA[i] - 12), tc, 0.08, -0.8 + i * 0.18)
put(reverse_swell(0.9), 53.1, 0.6)

# 54-60 end card ------------------------------------------------------------
put(sweep_noise(1.2, 400, 5000, "bell"), 53.95, 0.25)  # the sun rises again
final = [44, 56, 60, 63, 67, 70, 72]
put(pad(final, 4.4, a=0.02, r=1.4, cutoff=3000), 54.0, 0.42, bus="verb")
put(pad(final, 4.4, a=0.02, r=1.4, cutoff=3000), 54.0, 0.16)
put(np.sin(2 * np.pi * 51.9 * tt(5)) * env_adsr(int(5 * SR), 0.02, 0.6, 0.6, 1.8, 3.2), 54.0, 0.35)
put(boom(0.8), 54.0, 0.7)
put(kick(1.0), 54.0, 0.9)
put(bowl(56, 6.0), 54.8, 0.4, bus="verb")
for i, m in enumerate([80, 84, 87, 91, 87, 84]):
    put(pluck(m, 1.0, 1.0), 55.2 + i * 0.25, 0.07, (-0.5, 0.5)[i % 2], bus="verb")
put(blip(2093, 0.25), 56.0, 0.08, bus="verb")

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
