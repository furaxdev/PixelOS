---
name: video
description: Build an animated HTML teaser/presentation sequence for PixelOS (the custom Android OS project in this repo, built on LineageOS) using its real brand assets — wallpapers, brand mark, palette, mockup — for the user to screen-record into a real video. Use this whenever the user asks for a "teaser," "presentation video," "promo video," "demo video," a video "test," or anything about showing off PixelOS visually — even if they just say "make a video" or "/video" without more detail, since there's no other video-generation path in this project. Also use it for milestone-specific videos later (a first-boot demo, a feature showcase for gestures/AOD/quick panel, a wallpaper showcase) once real builds exist — the skill isn't limited to one fixed teaser.
---

# PixelOS video teaser

There is no tool in this environment that outputs an actual video file. What this skill produces is
a self-contained, animated HTML page — real CSS keyframe animation, orchestrated as a timed sequence
— published as an Artifact. The user previews it live in the browser and screen-records it
themselves; that recording is the actual video. Say this plainly when you deliver the result, so
it's clear the HTML *is* the deliverable and screen-recording is the export step, not a limitation
you're hiding.

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
  letterboxing, or full-viewport sized to that ratio) so what the user records matches what they
  asked for — don't build 16:9 and call it close enough for a 9:16 request.

## Delivering

Publish via the `Artifact` tool. In your message to the user:
- Name what focus/ratio/length you built, in case they asked for something and want to confirm it
  matches.
- Remind them screen-recording the artifact (their OS's screen recorder, or a browser extension) is
  how they get an actual video file — this skill doesn't export one.
- If they want changes, iterate on the same artifact (redeploy to the same path/URL) rather than
  creating a new one each round, per the Artifact tool's own guidance.
