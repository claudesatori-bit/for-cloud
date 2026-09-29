# Satori Craft — 60s motion film (v2, on brand)

A 1920×1080, 60 fps motion film for **Satori Craft** (satoricraft.com), built to the **Brand Guidelines
v1.0 (2026)**. Satori Craft is a practitioner-led Darwinbox implementation, application management and governed-AI partner for
Southeast Asia, India and the Middle East. Every frame is a pure function of time (`render(t)` in `index.html`).
Frames are captured headlessly and scored with an original synthesized soundtrack synced to the same cues.

**Output:** `satori-craft-film.mp4` (full quality) · `satori-craft-film-preview.mp4` (light)

## Concept, taken from the brand story

> "Confusing for months, then clear in an instant — once the right partner is in the room."

The film is that sentence. The tangled lines of an HRMS rollout pull taut and land on the strokes of the mark,
*a lotus opening into a sunrise*. The sunrise comes back at the end. The Bengaluru dot on the map becomes the sun,
and the lotus opens around it into the approved lockup, with the brand essence
*Quiet expertise that resolves into clarity.*

## Storyboard (120 BPM, cuts land on the beat)

| Time | Chapter | What happens |
|---|---|---|
| 0–4s | Countdown | Charcoal. A coral point. *HRMS rollout · go-live in* **90 → 0 days**, with workstream chips orbiting faster. |
| 4–11.5s | Noise | Word slams on every beat, each ending in a coral full stop (*Payroll. Leave. … UAT, round four. Go-live moved. Again. Who owns this?*). Alert cards, a tangled network, and shake and glitch that keep building. |
| 11.5–12s | — | *Confusing for months…* |
| 12–16s | Satori | Off-white. Every tangled line pulls onto a stroke of the mark and the coral sun rises. *…then clear in an instant.* Then *Sa·to·ri (悟り): a sudden moment of clarity.* |
| 16–21s | Identity | The mark settles into the approved full-colour lockup: *AI-First HR Tech Services · Darwinbox Prime Partner*. *Built by HR tech practitioners. Delivered by an enterprise services machine.* Then *Not assembly. Not theatre. Craft.* |
| 21–30s | 01 Implement | Navy. A ring of 17 module tiles flips to configured (0/17 → 17/17). The ring tilts edge-on into the Discover → Go-live timeline. *On time.* Whip-pan. |
| 30–36s | 02 Run | *Go-live is **the start line.*** A live service desk resolves tickets and a payroll run completes. Then *Implement. Run. Extend with AI.* |
| 36–43s | 03 Governed AI | An agent answers an HRBP's attrition question, then refuses a manager's Finance-salary request as those rows lock under row-level access. An ISO/IEC 27001:2022 seal stamps down. *AI that knows **who is asking.*** |
| 42.6–49s | 04 By the numbers | Navy / coral / sand / off-white panes with odometers: **300+** enterprise engagements, **100+** HRMS rollouts personally led, **56+** combined years, **95%+** on time. *Built by ex-Darwinbox **practitioners.*** |
| 49–54s | 05 Reach | Sand dot-field map. Coral arcs fly from Bengaluru to the Gulf, India and SEA. *One practitioner team. **Three regions.*** |
| 54–60s | End card | The Bengaluru dot becomes the sunrise and the lotus opens into the lockup. *Quiet expertise that **resolves into clarity.***, **Talk to a practitioner →**, satoricraft.com. |

## How the guidelines are applied

- **Colour 60/30/10.** Off-white and sand carry most scenes, navy anchors the hero sections (Implement, AI),
  and coral is kept for sparks: stat numbers, the second half of headlines, full stops, the sun and the CTA line.
  Charcoal appears only in the "problem" opening.
- **Type.** Cambria for headlines and big stats, and Calibri for body, UI and letter-spaced eyebrows, via
  their metric-compatible open versions Caladea and Carlito (`fonts/`).
- **Logo.** The approved artwork from the PDF (`assets/logo-full.png`, `logo-white.png`) is used whenever the mark
  is at rest, with the symbol centred above the wordmark. A vector trace of the same geometry is used only while
  the mark *builds*. The mark is never recoloured, stretched, rotated in 3D, or given shadows or glows.
- **Chrome** mirrors the guidelines deck: coral chapter number + letter-spaced label top-left, SATORI CRAFT
  top-right, footer *Satori Craft · AI-First HR Tech Services* and a page count.
- **Voice.** Copy comes from the guidelines (brand story, *Not assembly. Not theatre. Craft.*, the brand essence,
  *100+ HRMS rollouts personally led*) and the site. Nothing on the "don't say" list is used.

## Assumptions to check

- The countdown, alert cards, tickets, chat and table rows are illustrative UI. The city arcs show regions, not named clients.
- *Talk to a practitioner*, *Go-live is the start line* and *AI that knows who is asking* were written for the film.
- The wordmark is drawn from the PDF's raster logo (480 px wide) at up to 1.3×. A vector or high-res logo file
  from drive.satoricraft.com/brand would make the lockup sharper.

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
