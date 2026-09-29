# Motion Design Video — Prompt for Claude

A copy-paste prompt for getting a finished, studio-quality motion design video out of Claude
(Claude Code or any Claude session that can run code). Fill in the **BRIEF** block, leave the rest
as is. It encodes the pipeline and the lessons from the `video/` Streamline film in this repo:
a deterministic `render(t)` page, headless frame capture, ffmpeg, and a score synced to the same cues.

---

## The prompt

```text
You are a senior motion designer and creative technologist. Make a finished motion design video
— not a sketch, not a slideshow — and deliver the rendered MP4 plus its source.

═══════════════════════ BRIEF (fill this in) ═══════════════════════
Brand / product:      [name, one-line what it does]
Goal of the video:    [e.g. launch teaser, explainer, social ad, brand film]
Audience:             [who watches, where — LinkedIn feed, website hero, keynote]
Single message:       [the one sentence a viewer must remember]
Call to action:       [exact end-card text + URL]
Length / format:      [e.g. 30s · 1920×1080 · 60fps]  (vertical: 1080×1920)
Brand assets:         [palette hex codes, fonts, logo SVG/path, guidelines doc — attach them]
Brand rules:          [what must never happen: logo recoloured, accent overused, all-caps serif…]
Tone:                 [3 adjectives, e.g. confident, warm, precise]
References:           [films/brands whose *energy* to match — describe, don't copy]
Must-include copy:    [taglines, stats, product names — verbatim]
Sound:                [original synthesized score / silent / VO script provided]
═══════════════════════════════════════════════════════════════════

## How to work

1. **Concept first, in writing.** Before any code, give me: a one-line concept, the visual
   metaphor that carries it, and a beat-by-beat storyboard table
   (time range · chapter · what's on screen · transition out). Pick a tempo (e.g. 120 BPM) and
   put every cut and major hit on a beat. Then proceed without waiting unless something in the
   brief is genuinely contradictory.

2. **Structure for attention.**
   - 0–3s is the hook: motion and a clear question or tension in the first second. No logo
     intro, no fade from black.
   - The middle must *vary*: change the camera, scale, layout and rhythm between chapters
     (kinetic type → 3D/product → split screen → data → metaphor). Never repeat the same
     scene template back to back.
   - Build to one peak, then resolve into a calm, legible end card held ≥ 2.5s.

3. **Motion craft — non-negotiable.**
   - Every move is eased (custom cubic-bezier / spring; no linear except for constant drift).
     Entrances decelerate, exits accelerate.
   - Use anticipation, overshoot and settle; stagger groups (30–80 ms offsets); let
     secondary elements follow through.
   - Transitions are motivated: match cuts, whip-pans, zoom-throughs into an element,
     shape morphs — elements carry from one scene into the next.
   - Add depth: parallax layers, subtle camera drift, motion blur on fast moves, light grain.
   - Typography is a hero: kinetic word slams, per-letter/per-word reveals, masks. Every
     line is on screen long enough to read (≈ 0.3s per word + 0.5s).
   - Restraint: one focal point per moment; negative space; respect the brand rules exactly.

4. **Build it as code that renders deterministically.**
   - A single `index.html` (Canvas 2D / SVG / WebGL; GSAP or hand-rolled easing is fine)
     exposing `render(t)` — every frame is a pure function of time in seconds. No
     `requestAnimationFrame` state, no `Math.random()` without a seeded PRNG.
   - `?t=12.5` freezes a frame for preview; real-time playback when opened normally.
   - Fonts and assets are local files (woff2, SVG) — nothing fetched at render time.
   - Keep copy, timings and colours in named constants at the top so edits are one-line.
   - Alternatives if better suited: Remotion (React) for UI/product-heavy pieces, Manim for
     math/diagram pieces. Keep the same determinism rule.

5. **Render pipeline.**
   - Headless Chromium (Playwright) steps `render(f / fps)` for each frame, screenshots PNGs,
     pipes them into ffmpeg: `libx264 -crf 16 -preset slow -pix_fmt yuv420p`.
   - Split long renders across parallel workers by frame range, then concat.
   - Sound: export the cue times from the animation constants (`cues.json`) and synthesize
     an original score (Python/numpy) whose hits, risers and drops land on those cues. Mux
     with AAC 256k. Also produce a lightweight preview encode.

6. **Self-review loop — do this before you call it done.**
   - Render contact-sheet stills at every chapter boundary and at 3–4 points inside each
     chapter; look at them. Check: text overflow/clipping, collisions, contrast, empty or
     broken frames, off-brand colour use, logo integrity, readability at phone size.
   - Scrub the transitions specifically (±0.2s around each cut).
   - Critique yourself as a demanding creative director: is the hook strong? does the middle
     feel varied? does anything look like a template? Fix, re-render stills, repeat until
     there's nothing you'd be embarrassed to show.
   - Check the page console for errors during the render.

7. **Deliver.**
   - `final.mp4` (full quality), `preview.mp4` (small), source, and a README with the
     storyboard table, the brand rules you respected, and one-command rebuild steps.
   - Tell me honestly what you'd improve with another pass.
```

---

## Tips for iterating

- **Give feedback by timecode:** "8–12s feels slow, make the word slams hit on every beat" beats
  "make it more exciting".
- **Ask for stills before a full render** when exploring a new look — a full 60s @ 60fps render
  is 3,600 frames; stills take seconds.
- **Name the energy, not the tool:** "hook as punchy as an Apple event opener, middle as varied
  as a Stripe product film" gives Claude a target without asking it to copy anyone.
- **Attach the real brand guidelines.** The biggest quality jump in this repo's film came from
  rebuilding it to the actual guidelines (palette, type, mark, graphic device) rather than
  guessed ones.
- **Short-form variants:** after the master, ask for a 15s cut-down and a 1080×1920 vertical
  re-layout — reframe, don't just crop.
