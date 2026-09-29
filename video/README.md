# Streamline Workflows — 60s brand film

A 1920×1080, 60 fps motion film for **Streamline Workflows**, built to the Brand Guidelines v1.0:
forest / cream / ember / sage, Instrument Serif + Archivo + JetBrains Mono, the eight-node mark,
and the "fused row" graphic device. Every frame is a pure function of time (`render(t)` in
`index.html`), captured headlessly and scored with an original synthesized soundtrack synced to the same cues.

**Output:** `streamline-film.mp4` (full quality) · `streamline-film-preview.mp4` (light)

## Storyboard (120 BPM — cuts land on the beat)

| Time | Chapter | What happens |
|---|---|---|
| 0–4s | Prologue | A pulse on forest; a terminal types *"every business runs on workflows."*; the line ripples, then tangles. |
| 4–13s | Friction | Kinetic word slams (*Tabs. Pings. Handoffs. Spreadsheets. … Repeat.*), audit-style cards, tangled network, shake and glitch; "hours lost" counter climbs to 09h. Everything implodes. |
| 13–16s | The truth | Cream: *"Your business already works. It just works too hard."* |
| 16–21s | Identity | Shockwave; eight nodes fly in, the middle row fuses ember; wordmark. Dive into a node. |
| 21–29s | Automation | 3D product: drag a step in, wire *New order → Check stock → In stock? → Send invoice / Reorder*, hit Run, orders flow. Whip-pan out. |
| 29–34s | Product | Nodes open into a working job-status board; a sign-off clears live. |
| 34–38s | Marketing | *Demand. Brand. Measurement.* slam in, collapse into one 360° ring: *One system.* |
| 38–43s | Impact | Split screen: **9 hrs** returned / **6 wks** to first shipped tool. |
| 43–47s | Voice | *"We leverage cutting-edge synergies."* gets struck out → *"Here's the plan to get your hours back."* |
| 47–54s | One line | A noisy field settles; one row fuses: *"One line through the noise."* |
| 54–60s | End card | The row becomes the mark; *"Fewer moving parts."*, **Book a 30-min audit**, URL. |

Brand rules respected: ember only on the bar and as punctuation; sage only on forest; one fused row per
composition; serif set regular, never all-caps; the mark is never rotated, skewed or recoloured.

## Rebuild

```bash
pip install imageio-ffmpeg numpy scipy
export FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
node cues.js            # export cue times for the score
python3 audio.py        # -> score.wav
node render.js 0 3600 seg/all.mp4   # (or split ranges across workers)
$FFMPEG -i seg/all.mp4 -i score.wav -c:v copy -c:a aac -b:a 256k -shortest streamline-film.mp4
```

Open `index.html` in a browser for a live real-time preview (`?t=23.5` to freeze a frame).
Copy lives in `COPY`, `SLAMS`, `NODES`, `STATS` and `sFinale` in `index.html`.
