# Embedding real fonts (Artifact CSP blocks font CDNs)

The published Artifact can't `@import` or `<link>` a Google Fonts URL — the CSP blocks it, and it'll
silently fall back to a system font with no error. The fix is inlining the font as a `@font-face`
`data:` URI. This is fiddly enough to get wrong that it's worth following exactly.

## The gotcha: weight ranges return the wrong file

Requesting multiple weights in one Google Fonts CSS2 request (e.g.
`family=Unbounded:wght@800;900`) can silently return the **same** underlying file for every
requested weight — Google's variable-font negotiation sometimes picks one static instance and
serves it for all of them depending on the client hint it thinks it's talking to. You won't get an
error, you'll just get identical-looking weights and not notice until the design looks flat.

**Fix: request one weight per call.** Loop over each exact weight you need, one HTTP request each:

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
for w in 800 900; do
  curl -s -A "$UA" "https://fonts.googleapis.com/css2?family=Unbounded:wght@$w&display=swap" -o "unb_$w.css"
done
```

Then pull just the `latin` subset block from each (skip cyrillic/vietnamese/etc. — no need to bloat
the payload with unicode ranges the video won't use):

```bash
awk '/^\/\* latin \*\/$/{flag=1} flag{print} /^}$/{if(flag){print "---"; flag=0}}' unb_800.css
```

Confirm the extracted URLs actually differ between weights before downloading — if two weights show
the same `fonts.gstatic.com` URL, something went wrong upstream; don't proceed with those files.

## Downloading and embedding

```bash
curl -sL "https://fonts.gstatic.com/s/unbounded/v.../....woff2" -o unbounded-800.woff2
base64 -w0 unbounded-800.woff2 > unbounded-800.b64
```

Then in the HTML:

```css
@font-face {
  font-family: 'Unbounded';
  font-weight: 800;
  font-display: swap;
  src: url(data:font/woff2;base64,AAEAAAAP...) format('woff2');
}
```

## Keep the payload sane

Each embedded weight is typically 20-40KB base64'd — fine in small numbers, but don't embed five
weights of two families "just in case." Pick 1-2 display weights and 1-2 body weights, matching what
the design plan actually uses. The 16MB artifact ceiling is generous but wallpapers/mockup images add
up too.

## Picking faces

Avoid the cliché "safe" picks (Inter, Space Grotesk) unless the design plan has a specific reason to
reach for them — see the `artifact-design` skill's guidance on this. For PixelOS specifically, a
geometric/expressive display face pairs naturally with the brand's rounded-square mark and
Android-adjacent identity; a clean grotesk keeps body/label text out of the way. Don't default to the
exact same pairing every time this skill runs — treat the face choice as part of the design plan for
that specific video's content, not a fixed brand typeface locked in forever (PixelOS hasn't declared
one).
