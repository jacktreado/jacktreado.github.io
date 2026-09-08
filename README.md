# jacktreado.github.io

Personal/academic website, served by GitHub Pages at [jacktreado.github.io](https://jacktreado.github.io).

## Stack

Plain static HTML/CSS/JS — a hand-edited Bootstrap 5 build of the [StartBootstrap "Grayscale"](https://startbootstrap.com/theme/grayscale) theme. **There is no build step.** Everything under `docs/` is the live site, edited directly.

GitHub Pages is configured (repo Settings → Pages) to serve from the `docs/` folder on the `main` branch. No custom domain (no `CNAME` file) — the site lives at the default `jacktreado.github.io` URL.

## Folder layout

```
docs/
├── index.html          the entire site (single page, anchor-linked sections)
├── cv.pdf              linked from the nav bar
├── assets/
│   ├── favicon.ico
│   ├── img/            static images (photos, figures, background images)
│   └── video/          looping background/figure clips (muted <video>, not GIF)
├── css/                styles.css (compiled/hand-edited Bootstrap theme CSS) + academicons
├── fonts/               academicons icon font (CV/GitHub/Scholar icons in the nav)
└── js/scripts.js
```

## How to edit

- **Content/sections** (bio, research blurbs, publications list, contact info): edit `docs/index.html` directly. Publications are plain hand-written `<p>` entries under `#publications` — copy an existing entry's structure for a new one.
- **Styling**: edit `docs/css/styles.css` directly.
- **CV**: replace `docs/cv.pdf`.
- **Adding a static image**: drop it in `docs/assets/img/`.
- **Adding an animated figure**: don't add a GIF directly — GIFs are huge (one used to be 92MB and was loaded by every visitor). Convert it to a small looping video first:

  ```bash
  ffmpeg -i source.gif -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -an -movflags +faststart docs/assets/video/name.mp4
  ```

  Then embed it as a muted, autoplaying, looping `<video>` (not an `<img>`):

  ```html
  <video class="img-fluid" src="assets/video/name.mp4" width="W" height="H" autoplay muted loop playsinline preload="metadata"></video>
  ```

  Use the real pixel dimensions of the source for `width`/`height` (check with `ffprobe -select_streams v:0 -show_entries stream=width,height source.gif`) so the layout doesn't jump while it loads. If it's a large background image, don't upscale beyond the source resolution — CSS/the browser scales it up for display for free.

## Preview locally

No install needed:

```bash
cd docs && python3 -m http.server 8000
```

Open `http://localhost:8000`.

## Push

```bash
git add -A
git commit -m "..."
git push
```

Pushing to `main` updates the **live** site within a minute or two — there's no staging environment, so preview locally first.

## Verify a deploy actually worked

1. In the GitHub repo, check the **Actions** tab for a "pages build and deployment" run and confirm it succeeded.
2. Visit `https://jacktreado.github.io` and hard-refresh (Cmd+Shift+R) to bypass cache.
3. Quick checklist:
   - Page loads, masthead video plays.
   - Nav links (`About`, `Research`, `Publications`, `Contact`) jump to the right section.
   - CV, GitHub, and Google Scholar icons in the nav open the right things.
   - New/changed publication entries render correctly and links open in a new tab.
   - No errors in the browser console.

## Checking mobile-friendliness / performance

Before adding any new large media file, or after any layout change:

1. Preview locally (see above), open Chrome DevTools → Device Toolbar, and check a couple of phone widths (e.g. iPhone SE, a mid-size Android). Confirm: no horizontal scroll, the nav collapses into the hamburger menu correctly, video backgrounds don't cause layout jumps.
2. Run a **Lighthouse** audit in Chrome DevTools (Lighthouse tab → Mobile + Desktop). Investigate anything flagged, especially:
   - Largest Contentful Paint / total page weight — usually means a new image/video isn't compressed enough.
   - Cumulative Layout Shift — usually means a missing `width`/`height` on an `<img>`/`<video>`.
3. As a sanity check on total size, `du -sh docs` should stay in the low tens of MB — if it jumps a lot after adding something, that thing probably needs compressing (see the `ffmpeg`/image-compression notes above; `cwebp` and `sips` work well for images on macOS with no install needed).

## Note on repo history size

`.git` itself is large (~300MB) because early commits included the original uncompressed GIFs before this cleanup. That history isn't rewritten as part of normal edits — it would require `git filter-repo` and a force-push, which is a separate, deliberate operation, not something to do casually.
