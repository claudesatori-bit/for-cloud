# Streamline — 60s motion film

A 1920×1080, 60 fps motion-graphics spot for **Streamline** (streamline-workflows-site.vercel.app),
built entirely in code: every frame is a pure function of time (`render(t)` in `index.html`),
captured headlessly and scored with an original synthesized soundtrack synced to the same cues.

**Output:** `streamline-film.mp4`

## Storyboard (120 BPM — every cut lands on the beat)

| Time | Chapter | What happens |
|---|---|---|
| 0–4s | 00 Prologue | A single pulse; a terminal types *“every team runs on workflows.”*; the line ripples, then tangles. |
| 4–12s | 01 Friction | Notification chaos, a tangled network, kinetic word slams (*Tabs. Pings. Handoffs. … Repeat.*), rising camera shake and glitch. |
| 12–16s | 02 Shift | Everything implodes to a point → *“What if work just flowed?”* |
| 16–22s | 03 Identity | Shockwave; the S-flow mark draws itself, wordmark reveals, flow field bends around it; zoom-through the lime node. |
| 22–36s | 04 Build | 3D product UI: drag-and-drop a node, wire the graph, hit Run — live packets, branching, run log, counter. |
| 36–44s | 05 Impact | Odometer stats with clock, bar and heartbeat visuals. |
| 44–52s | 06 Connect | Integrations orbit a glowing hub, then spiral into it. |
| 52–60s | 07 Momentum | *“Less busywork. More momentum.”* → end card with CTA; streamlines part around the logo. |

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
