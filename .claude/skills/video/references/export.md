# Exporting the HTML sequence to a real MP4

This environment has Chromium (Playwright-managed) and, once `apt-get install ffmpeg` has been run,
a full-featured `ffmpeg` — which means the animated HTML doesn't strictly require the user to
screen-record it. It can be rendered to an actual MP4 file directly. Prefer this when the
environment supports it (Bash + network + apt access); fall back to "screen-record the Artifact
yourself" only if any step here isn't available.

## Why this needs two ffmpeg checks, not one

Playwright bundles its own minimal `ffmpeg` (under `/opt/pw-browsers/ffmpeg-*/ffmpeg-linux` in this
environment) — but it's a stripped build compiled only for Playwright's internal webm
screenshot/video needs (`--disable-everything` plus just `libvpx`/`mjpeg`/`png`). It **cannot**
encode H.264 or mux MP4 — running `-c:v libx264 ... .mp4` against it fails with "Unrecognized
option". Don't reach for it for the transcode step. Install a real one:

```bash
apt-get update -qq && apt-get install -y --no-install-recommends ffmpeg
```

then use whatever `ffmpeg` resolves to on `PATH` afterward (it'll be the full build) — not the
Playwright-bundled path — for the transcode step below.

## Pipeline

1. **Record the HTML with Playwright's built-in video capture** — a small Node script (the `playwright`
   npm package is globally installed already; find the actual chromium binary under
   `/opt/pw-browsers/chromium-*/chrome-linux/chrome` rather than assuming a path, it's versioned):

   ```js
   const { chromium } = require('playwright'); // resolve the real global install path if this bare require fails
   const path = require('path');

   (async () => {
     const outDir = '/absolute/path/to/output/dir';
     const width = 1920, height = 1080; // match the aspect ratio confirmed with the user

     const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-XXXX/chrome-linux/chrome' });
     const context = await browser.newContext({
       viewport: { width, height },
       recordVideo: { dir: outDir, size: { width, height } },
     });
     const page = await context.newPage();
     await page.goto('file://' + path.resolve(outDir, '../path/to/teaser.html'));

     // Wait slightly LONGER than the sequence's total duration (last scene's delay + its own
     // duration) so the final held frame is actually captured, not cut off mid-hold.
     await page.waitForTimeout(20500);

     await context.close(); // finalizes the .webm — the file doesn't exist/isn't valid until this
     await browser.close();
   })();
   ```

   `context.close()` is what flushes and finalizes the `.webm` — closing only the page isn't enough.
   The output filename is a random hash Playwright assigns; find it with a fresh `ls` after the
   script exits rather than guessing.

2. **Transcode to MP4** with the real `ffmpeg` installed above:

   ```bash
   ffmpeg -y -i recorded.webm -vf fps=30 -c:v libx264 -pix_fmt yuv420p -movflags +faststart -crf 18 teaser.mp4
   ```

   `-pix_fmt yuv420p` matters — without it the output can fail to play in some players/editors that
   don't support the default higher-fidelity pixel format. `-movflags +faststart` moves the moov atom
   to the front so the file starts playing before it's fully downloaded, standard practice for
   anything headed to the web.

3. **Verify before delivering** — don't hand over a file you haven't confirmed is real:

   ```bash
   ffprobe -v error -show_entries format=duration -show_entries stream=width,height,codec_name -of default=noprint_wrappers=1 teaser.mp4
   ```

   Confirm the codec is `h264`, the resolution matches what was asked for, and the duration is in
   the ballpark of the sequence's intended length (a duration of ~0s or a missing video stream means
   the recording step silently produced nothing — usually a `context.close()` that never ran because
   an earlier step threw).

4. **Deliver the file** via whatever file-sending tool is available in this environment, not just a
   link to the Artifact — the whole point of this pipeline is that the user gets an actual video file
   without doing the screen-recording themselves.

## When to skip this and just tell the user to screen-record

If Bash/network/apt access isn't available, or the `playwright` package / Chromium binary can't be
located, don't burn time debugging a sandboxed environment's specifics — fall back to the Artifact
tool's normal delivery (publish it, tell the user to screen-record). Say plainly which path was
taken so the user knows whether they're getting a finished file or need to do a recording step.
