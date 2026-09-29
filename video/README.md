# Streamline Workflows — 60s brand film

A 1920×1080, 60 fps motion film for **Streamline Workflows**, built to the Brand Guidelines v1.0:
forest / cream / ember / sage, Instrument Serif + Archivo + JetBrains Mono, the eight-node mark,
and the "fused row" graphic device. Every frame is a pure function of time (`render(t)` in
`index.html`), captured headlessly and scored with an original synthesized soundtrack synced to the same cues.

**Output:** `streamline-film.mp4` (full quality) · `streamline-film-preview.mp4` (light)

## The idea

The film *is* the mark: scattered nodes → one row resolved. Before and after, inside a single shape.

| Time | Chapter | What happens |
|---|---|---|
| 0–12s | 01 The problem | Nodes scatter into a tangled network on cream. *"Your business already works. It just works too hard."* Audit findings pin to nodes; *"Nine hours a week, lost to re-entry."* Unquantised ticking thickens. |
| 12–17s | 02 The fix | Every node snaps onto a 3×9 grid on the beat; the middle row fuses into the ember bar. *"We find the hours and give them back."* |
| 17–21s | Identity | The grid condenses into the mark; wordmark + *"Fewer moving parts."* The bar stretches edge to edge and slits open to forest. |
| 21–41s | 03 What we do | Positioning line, then the three pillars, each told with nodes: handoffs straightening into one flow, nodes opening into a working ops board, three rings merging into one 360° system. |
| 41–47s | 04 Impact | *"Your team spends nine hours a week retyping the same order."* → **9 hrs** returned / **6 wks** to first shipped tool. |
| 47–54s | 05 One line | A noisy field of nodes settles; one row fuses. *"One line through the noise."* |
| 54–60s | End card | The fused row becomes the mark: lockup, *"Fewer moving parts."*, **Book a 30-min audit**, URL. |

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
