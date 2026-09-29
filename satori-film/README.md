# Satori Craft — 60s motion film

A 1920×1080, 60 fps motion film for **Satori Craft** (satoricraft.com), a practitioner-led Darwinbox
implementation, application management and governed-AI partner for Southeast Asia, India and the Middle East.
Every frame is a pure function of time (`render(t)` in `index.html`). Frames are captured headlessly and
scored with an original synthesized soundtrack synced to the same cues.

**Output:** `satori-craft-film.mp4` (full quality) · `satori-craft-film-preview.mp4` (light)

## Concept

An HRMS rollout is noise. *Satori* is the moment it all makes sense. One ensō (a single brush-stroke circle)
stops the chaos. It then becomes the mark, the ring of 17 module areas, the go-live timeline, and finally the
end card. A vermilion point runs through the whole film: the countdown light, the centre of the mark, Bengaluru HQ.

## Storyboard (120 BPM, cuts land on the beat)

| Time | Chapter | What happens |
|---|---|---|
| 0–4s | Countdown | A vermilion point. *HRMS rollout · go-live in* **90 → 0 days**, with workstream chips orbiting faster. |
| 4–11.5s | Noise | Kinetic word slams on every beat (*Payroll. Leave. … UAT, round four. Go-live moved. Again. Who owns this?*), alert cards, a tangled network, and shake and glitch that keep building. |
| 11.5–12s | Breathe. | Everything drops out. |
| 12–16s | Satori | Paper. An ensō is brushed bristle by bristle. *Satori · 悟り · the moment everything makes sense.* The camera dives into the ink. |
| 16–21s | Identity | Shockwave. Mark and wordmark, *Darwinbox Prime Partner*. *Built by HR tech practitioners. Delivered by an enterprise services machine.* |
| 21–30s | Implement | The mark opens into a 3D ring of 17 module tiles that flip to configured (0/17 → 17/17). The ring tilts edge-on and becomes the timeline: Discover → Go-live. *On time.* Whip-pan. |
| 30–36s | Run | *Go-live is the start line.* A live service desk resolves tickets while a payroll run completes. Then *Implement. Run. Extend with AI.* |
| 36–43s | Governed AI | An agent answers an HRBP's attrition question, then refuses a manager's Finance-salary request as Finance rows lock under row-level access. An ISO/IEC 27001:2022 seal stamps down. *AI that knows who is asking.* |
| 42.6–49s | Proof | Four panes slam in with odometers: **300+** engagements, **100+** implementations led, **56+** combined years, **95%+** on time. *Built by ex-Darwinbox practitioners.* |
| 49–54s | Reach | Dot-field map. Arcs fly from Bengaluru to the Gulf, India and SEA cities. *One practitioner team. Three regions.* |
| 54–60s | End card | The ensō is brushed again around the vermilion point. **Satori Craft**, *Clarity, delivered.*, **Talk to a practitioner →**, satoricraft.com. |

## Assumptions to check

- **Brand look is original.** satoricraft.com was not reachable from the build environment, so the palette
  (sumi ink / rice paper / hanko vermilion), type (Instrument Serif, Archivo, JetBrains Mono) and ensō mark
  are proposals, not the official identity. Swap `B`, `F` and `mark()` in `index.html` for the real ones.
- **Facts** come from satoricraft.com search snippets: Darwinbox Prime Partner, 300+ engagements,
  100+ implementations, 56+ combined years, 95%+ on-time, 17 module areas, Academy-certified,
  ISO/IEC 27001:2022, row-level access for AI, GDPR/PDPA/labour law, SEA/India/Middle East.
- **Written for the film:** *Clarity, delivered.*, *Talk to a practitioner*, *AI that knows who is asking*,
  *Go-live is the start line*. Ticket names, chat and table rows are illustrative UI, and city arcs show regions, not named clients.

## Rebuild

```bash
pip install imageio-ffmpeg numpy scipy
export FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
node cues.js            # export cue times for the score
python3 audio.py        # -> score.wav
for i in 0 1 2 3; do node render.js $((i*900)) $((i*900+900)) seg/s$i.mp4 & done; wait
printf "file 's0.mp4'\nfile 's1.mp4'\nfile 's2.mp4'\nfile 's3.mp4'\n" > seg/list.txt
$FFMPEG -f concat -i seg/list.txt -i score.wav -c:v copy -c:a aac -b:a 256k -shortest seg/master.mp4
$FFMPEG -i seg/master.mp4 -c:v libx264 -preset slow -b:v 11M -maxrate 14M -bufsize 20M -movflags +faststart -c:a copy satori-craft-film.mp4
```

Open `index.html` in a browser for a real-time preview (`?t=23.5` freezes a frame).
`node stills.js 4.1 13.5 …` and `./sheet.sh out.jpg` make contact sheets for review.
