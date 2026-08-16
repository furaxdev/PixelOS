---
name: video
description: Build an animated HTML teaser/presentation sequence for PixelOS (the custom Android OS project in this repo, built on LineageOS) using its real brand assets — wallpapers, brand mark, palette, mockup — and, where the environment allows it, render it straight to a real MP4 file rather than making the user screen-record it themselves. Use this whenever the user asks for a "teaser," "presentation video," "promo video," "demo video," a video "test," or anything about showing off PixelOS visually — even if they just say "make a video" or "/video" without more detail, since there's no other video-generation path in this project. Also use it for milestone-specific videos later (a first-boot demo, a feature showcase for gestures/AOD/quick panel, a wallpaper showcase) once real builds exist — the skill isn't limited to one fixed teaser.
---

# PixelOS video teaser

What this skill builds, underneath, is a self-contained animated HTML page — real CSS keyframe
animation, orchestrated as a timed sequence. Where that ends up depends on what the environment
allows:

- **If Bash + network + package install are available**, render it to a real MP4 directly (Chromium
  + ffmpeg — see `references/export.md`) and deliver the video file. This is the better outcome when
  it's reachable — the user gets a finished file, not a recording chore.
- **Otherwise**, publish it as an Artifact and have the user screen-record it themselves.

Try the MP4 path first; fall back to Artifact-only if any step in `references/export.md` isn't
available in this environment. Either way, say plainly in your delivery message which one happened —
don't leave the user guessing whether they're holding a finished file or need to do a recording step.

## Before writing any HTML

1. **Read `references/brand.md`** in this skill directory — palette, brand mark, existing wallpaper
   assets, tagline, voice. Don't invent new brand colors or redesign the logo; reuse what's there.
2. **Load the `artifact-design` skill.** This is an editorial deliverable (a promo/teaser piece the
   user will show other people), not a utilitarian doc — treat it with that level of craft: a real
   design plan (color/type/layout), deliberate typography, one real point of view, motion used with
   intent rather than scattered everywhere.
3. **Confirm focus and format if not given.** Don't assume — a few seconds of asking saves a
   redo:
   - **Focus**: full brand teaser (logo → wallpapers/mockup → tagline) vs. one specific thing (a
     wallpaper showcase, a feature once it's real — gestures/AOD/quick panel — a first-boot moment).
     If nothing else exists yet to show off beyond the brand assets, the full teaser is the only
     honest option — say so rather than inventing footage of features that don't run anywhere yet.
   - **Aspect ratio**: vertical 9:16 (shorts/reels/stories) or horizontal 16:9 (YouTube/general) —
     these need different pacing and layout, not just a resize, so get this before building.
   - **Length/pacing**: a teaser loop (~5-8s, seamlessly repeats) reads differently than a longer
     one-shot sequence (~15-20s) that plays once and stops. Ask which fits their use, don't default
     silently.

## Building the sequence

- Treat it as one orchestrated moment, not a slideshow of unrelated effects — a real page-load
  sequence with a beginning, a peak, and a resolution (or a loop point if it's meant to repeat
  seamlessly). See `artifact-design`'s guidance on motion: an orchestrated sequence lands harder than
  scattered animation, and restraint often reads better than more effects.
- Drive timing with CSS `@keyframes` and `animation-delay` on a fixed timeline — don't rely on JS
  `setTimeout` chains for something this deterministic, keyframes are more robust and scrub better if
  the user records at a different frame rate than expected.
- Respect `prefers-reduced-motion` — provide a static fallback frame (the strongest single moment of
  the sequence, e.g. the fully-revealed logo + tagline) rather than disabling the page.
- Real typography matters here more than most artifacts, since this is a brand piece — see
  `references/fonts.md` for the exact recipe to embed real font files as data URIs (the CSP blocks
  font CDNs, and the naive multi-weight request silently returns wrong files — read this before
  fetching anything).
- This will almost always end up a deliberately single dark-themed piece (PixelOS's brand is
  dark-first, and a teaser especially benefits from committing to one mood) — `artifact-design`
  permits that for a piece with a committed visual world, but still paint `background` and every
  color explicitly rather than leaving anything to inherit from the viewer's theme.
- Size the artifact's content to the confirmed aspect ratio (e.g. a centered fixed-aspect frame with
  letterboxing, or full-viewport sized to that ratio) so what the user records/renders matches what
  they asked for — don't build 16:9 and call it close enough for a 9:16 request.
- **Size everything relative to the fixed-aspect stage box, not the outer viewport.** If that stage
  is centered/letterboxed inside `100vw`/`100vh` (the natural way to build a fixed 16:9 or 9:16 frame
  that still fills whatever window it's opened in), don't then size the *contents* of that stage in
  `vw`/`vh` too — those units are relative to the outer viewport, not your stage box, so on a window
  whose aspect ratio differs from your stage's (e.g. a narrow mobile screen showing a 16:9 stage
  letterboxed top and bottom), a size like `22vw` can resolve to something far bigger than the actual
  stage it's supposed to fit inside, overflowing it. Give the stage `container-type: size` and size
  its descendants in `cqw`/`cqh` (container query units) instead — those stay relative to the stage's
  own rendered box no matter how the outer window is shaped. This one is easy to miss when previewing
  on a normal desktop browser (viewport and stage aspect often happen to be close enough there) and
  only shows up as visibly broken on a differently-shaped screen — test the second Artifact preview
  screenshot from an actual mobile-shaped viewport if you can, not just the first desktop-shaped one.
- **Build a CSS typewriter reveal from a box sized to the text's own natural width (`display:
  inline-block`, no explicit width), revealed via an animated `clip-path: inset(0 100% 0 0)` →
  `inset(0 0% 0 0)`**, rather than animating `width` from `0` to a guessed target. A guessed `em`
  value (`4.15em` to "roughly" fit "PixelOS") is the obvious way this goes wrong, but even the
  seemingly-exact fix — `width: 7ch` for a 7-character word, correct in principle since monospace
  makes `ch` exact — is still one more moving part than necessary when the font-size involved is
  itself `cqw`-driven, and one more thing to doubt when something looks clipped. `clip-path` on a
  naturally-sized box has nothing to compute or guess: it reveals exactly what's already there, by
  construction, regardless of viewport or font metrics. Put the blinking cursor in a sibling element,
  absolutely positioned with its own `left: 0% → 100%` animation *of the same box* (matching duration/
  steps/delay) — it then tracks the reveal edge exactly without ever needing to know the text's pixel
  width.
- **Before concluding a reveal is clipped, check whether the screenshot just landed on the
  animation's exact completion frame, not after it.** `steps()` changes value in discrete jumps, and
  a screenshot taken at (or a hair before) the precise moment `delay + duration` elapses can catch the
  render one frame short of the final step — reading exactly like a clipped word even though the
  animation is defined correctly. Confirm a real bug by checking a moment clearly *inside* the
  element's stable, fully-settled window (e.g. reveal completes at 4.85s and the scene doesn't start
  fading until 6.25s — screenshot at 5.5s, not 4.9s), and cross-check the computed `clip-path`/`width`
  value via `getComputedStyle` if the screenshot still looks wrong. Chasing a timing artifact as if it
  were a CSS bug wastes a full fix-rebuild-reverify cycle for nothing.
- **A recurring "status line" motif (terminal-style typed lines, or anything else that types in more
  than once at the same position) needs its own fade-out**, not just a fade-in. If each occurrence's
  animation only handles typing in and holding, the next occurrence starts while the previous one is
  still sitting at full opacity in the same spot — the text visibly mashes together. Give each
  occurrence one self-contained keyframe animation that types in, holds, *and* fades to opacity 0
  before the next one's delay begins, with a real gap between one's end and the next's start.
- **A blinking cursor should be its own solid block element, not a wide `border-right` on the text
  box.** Putting it on the same box as an animated width is a double bug: with the near-universal
  `* { box-sizing: border-box }` reset, a border wide enough to read as a cursor (real terminal
  cursors are roughly one character-cell wide, so `border-right: 2-4px` reads as a stray line, not a
  cursor — use something like `0.5em`) eats directly into that box's own declared width, silently
  shrinking the room left for the actual characters. A separate cursor element sidesteps this
  entirely, and pairs naturally with the `clip-path` reveal technique above (see there for how it
  tracks position). Also don't add a leading prompt glyph (`$`/`>`) unless you've actually checked it
  reads as text and not as a second cursor at the render's real output size — a thin character next to
  a solid cursor block, especially after video compression at small display sizes, easily reads as
  "there are two cursors" rather than "there's a prompt symbol." If it's not clearly pulling its
  weight, it's simplest and most robust to just leave it out — the typing motion alone reads as a
  terminal.

## Delivering

Try `references/export.md`'s pipeline first (Playwright + a real `ffmpeg`, not the stripped one
Playwright bundles for its own internal use — the reference explains the distinction and why it
matters) to render an actual MP4 and deliver it as a file. If that pipeline isn't reachable in this
environment, publish via the `Artifact` tool instead. Either way:
- Name what focus/ratio/length you built, in case they asked for something and want to confirm it
  matches.
- If you delivered an Artifact rather than a file, say so plainly and remind them screen-recording it
  (their OS's screen recorder, or a browser extension) is how they get an actual video file.
- If they want changes, iterate on the same HTML and re-render/redeploy rather than starting over —
  redeploy an Artifact to the same path/URL per the Artifact tool's own guidance, or just re-run the
  export pipeline against the updated HTML for the MP4 path.
