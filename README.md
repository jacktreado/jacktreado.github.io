# jacktreado.github.io

Personal/academic website, served by GitHub Pages at [jacktreado.github.io](https://jacktreado.github.io).

## Stack

A [Jekyll](https://jekyllrb.com/) site. GitHub Pages is configured (repo Settings → Pages) to build the `docs/` folder on the `main` branch — Pages detects `docs/_config.yml` and runs its own Jekyll build automatically on every push, no GitHub Actions workflow required. No custom domain (no `CNAME` file); the site lives at the default `jacktreado.github.io` URL.

Visual design is layered: the original hand-edited Bootstrap 5 theme (`docs/css/styles.css`, a customized [StartBootstrap "Grayscale"](https://startbootstrap.com/theme/grayscale) build) still powers the About/Contact sections and base typography, and a newer `docs/assets/css/redesign.css` layer — loaded *after* `styles.css` so it can override it — powers the nav bar, research grid, and project pages. Both are plain hand-written CSS; there's no Sass/PostCSS/bundler step.

## (a) How the repository is organized

```
docs/                          Jekyll source AND the GitHub Pages build root
├── _config.yml                site settings, the `projects` collection, defaults
├── _data/
│   ├── nav.yml                 top nav + mobile drawer links
│   ├── publications.yml        the Publications page, one entry per paper
│   └── commentary.yml          the "Commentary" list at the bottom of Publications
├── _layouts/
│   ├── default.html            page chrome: <head>, nav include, footer, scripts
│   └── project.html            one research project's page (split or stacked hero)
├── _includes/
│   ├── site-nav.html           nav bar + off-canvas mobile drawer
│   ├── project-card.html       one grid card (used on both index.html and research/)
│   ├── project-links.html      the pill-style "Paper / Press / Data" links row
│   └── project-more.html       next-project link at the bottom of a project page
├── _projects/
│   └── *.md                    one file per research project — see (c) below
├── index.html                  homepage: hero, About, Research teaser, Contact
├── research/index.html         full research grid (every project in _projects/)
├── publications/index.html     renders _data/publications.yml + commentary.yml
├── cv.pdf                      linked from the nav
├── favicon.ico
├── assets/
│   ├── css/redesign.css        new design system — tokens, nav, grid, project pages
│   ├── js/redesign.js          nav drawer, shrink-on-scroll, hover-to-play thumbnails
│   ├── img/                    photos, figures, posters/ (grid + hero poster frames)
│   └── video/                  project clips; thumbs/ holds the cropped hover loops
├── css/                        the original Bootstrap theme (styles.css) + academicons
├── fonts/                      academicons icon font (CV/GitHub/Scholar icons)
└── js/scripts.js               original Bootstrap theme JS (scroll-spy, etc.)
```

Two directories at the repo root, `docs_old/` and `jekyll_reference/`, are leftovers from the migration off the old single-page static site — not part of the live build. Safe to delete once you're confident nothing in them is still needed.

## (b) How the site works

- **Everything under `docs/` is the Jekyll source** *and* the build root — GitHub Pages doesn't read a separate `_site/` output; it builds `docs/` itself on push. Locally, `jekyll serve`/`jekyll build` reads the same `docs/` tree and writes a `docs/_site/` (or wherever `--destination` points) that you should never hand-edit or commit.
- **Front matter (`---` at the top of a file) is what makes Jekyll process a file** — apply a layout, run Liquid tags, etc. A file without front matter (`styles.css`, `redesign.js`, images, videos) is copied through untouched.
- **The `projects` collection** (declared in `_config.yml`) turns every file in `_projects/` into a page at `/research/<filename>/`, automatically laid out with `_layouts/project.html` (set via the `defaults:` block, so individual project files don't need `layout: project` in their front matter, though it's harmless if present for clarity).
- **The nav bar is data-driven**: `_includes/site-nav.html` loops over `_data/nav.yml`, so adding/renaming/reordering nav links never touches HTML.
- **The homepage Research section and the full `/research/` grid pull from the same source** — both loop over `site.projects` (sorted by each project's `order`) through the same `project-card.html` include, so they always show the same cards in the same order automatically. No content is duplicated between them.

### Previewing locally

Ruby + Jekyll need to be installed once (`gem install bundler jekyll`, or `sudo gem install jekyll` — this repo doesn't have its own `Gemfile`, so a global Jekyll install is enough; running `jekyll -v` tells you if it's already there). Then, from the repo root:

```bash
jekyll serve --source docs --livereload
```

Open `http://127.0.0.1:4000`. `--livereload` means edits to anything in `docs/` auto-refresh the page — no separate build/restart step for content or CSS changes (`_config.yml` changes are the one exception; those need the server restarted). Stop with `Ctrl+C`.

### Push / deploy

```bash
git add -A
git commit -m "..."
git push
```

Pushing to `main` triggers a Pages build within a minute or two — there's no staging environment, so preview locally first. To verify a deploy: check the **Actions** tab for a "pages build and deployment" run, then visit the live site and hard-refresh (Cmd+Shift+R) to bypass cache. A failed Pages build is the one failure mode that leaves the live site looking stale with no obvious warning, so it's worth actually checking Actions after a push that touches `_config.yml`, layouts, or includes.

## (c) How to add a project card + description

Each research project is one Markdown file in `docs/_projects/`. Copy an existing one (e.g. `mesophyll-development.md`) as a starting point — the front matter keys are the whole API:

```markdown
---
title: Your project title
order: 5                        # controls grid position (ascending) and next/prev order
kicker: Short category label     # small label above the title, e.g. "Jamming"
layout: project
hero_layout: split               # or: stacked — see the two layouts below

hero_video:  /assets/video/yourclip.mp4     # omit for an image-only project
hero_poster: /assets/img/posters/yourslug.jpg
hero_width:  1120                # actual pixel dimensions of the hero video/image
hero_height: 840
caption: One-line caption shown under the hero media.

thumb_video:  /assets/video/thumbs/yourslug.mp4   # the grid-card hover loop
thumb_poster: /assets/img/posters/yourslug.jpg
thumb_width:  640
thumb_height: 480

links:
  - kind: Paper
    label: Journal Name 99, 12345 (2026)
    url: https://doi.org/...
  - kind: Press
    label: Some Outlet
    url: https://...
---

Body copy in Markdown. This becomes the prose column on the project page.
MathJax still works: \\( {\\cal A} = p^2 / 4\\pi a \\).
```

- `order` is the only thing that controls where the card lands in the grid (ascending) — the filename just becomes the URL slug (`/research/<filename-without-.md>/`).
- Card thumbnails and hero media use `object-fit: contain`, so any aspect ratio is safe to use as-is — mismatched ratios just letterbox against the card's background panel instead of getting cropped. You still don't need to hand-pick dimensions carefully, but `hero_width`/`hero_height`/`thumb_width`/`thumb_height` should match the actual encoded file's pixel dimensions (check with `ffprobe`) so the browser can reserve the right space before the media loads, which avoids layout jank.
- Omit `hero_video`/`thumb_video` entirely for an image-only project (see `deformability-and-response.md` for an example) — the templates fall back to a plain `<img>` using the poster.
- `links` entries can use any short string as `kind` (`Paper`, `Press`, `Code`, `Data`, ...) — it's rendered as a small label next to the link text, nothing is hardcoded to specific values.
- `hero_layout: split` (the default, used by all current projects) is a two-column layout: media left, text right. `hero_layout: stacked` is a full-bleed hero with the title overlapping it — implemented but currently unused; reasonable for one project if a clip deserves the extra space.

### Encoding new video/poster assets

Given a source clip, generate the three files a project needs:

```bash
# poster — first frame, resting state of the card
ffmpeg -i source.mp4 -vf "select=eq(n\,0)" -q:v 3 docs/assets/img/posters/yourslug.jpg

# hover-thumb loop — keep it short (~5-8s) even if the source is longer;
# a 30s source scaled to 640px wide is still a multi-hundred-KB download
ffmpeg -i source.mp4 -t 6 -vf "scale=640:-2" -c:v libx264 -crf 30 -preset slow \
       -pix_fmt yuv420p -an -movflags +faststart docs/assets/video/thumbs/yourslug.mp4

# hero clip for the project page itself
ffmpeg -i source.mp4 -c:v libx264 -crf 26 -preset slow \
       -pix_fmt yuv420p -an -movflags +faststart docs/assets/video/yourslug.mp4
```

Rough size budgets (not hard limits, but good targets): poster < 80 KB, hover-thumb < 400 KB, hero clip < 3 MB. Check actual dimensions afterwards with:

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 docs/assets/video/yourslug.mp4
```

## (d) How to edit everything else

- **About / Contact / hero text**: edit the relevant `<section>` directly in `docs/index.html`.
- **Publications and Commentary**: the page reads `docs/_data/publications.yml` and `docs/_data/commentary.yml`, but **those two files are generated — don't hand-edit them.** The actual source of truth is `references.bib` at the repo root. To add/change a publication, just edit `references.bib` and push:

  ```bibtex
  @article{treado2026something,
    author  = {John D. Treado and A. N. Other},
    title   = {Title with a trailing period.},
    journal = {Phys. Rev. Lett.},
    year    = {2026},
    volume  = {136},
    pages   = {018101},
    url     = {https://doi.org/...},
  }
  ```

  A GitHub Actions workflow (`.github/workflows/bib-to-data.yml`) runs on every push to `main` that touches `references.bib`, regenerates both `.yml` files, and commits them back automatically — you never need to run anything by hand. That workflow needs the repo's Actions permissions set to "Read and write" (Settings → Actions → General → Workflow permissions) so it's allowed to push its commit; that's a one-time setting, already fine on a personal repo's default in most cases. If `main` has branch-protection rules requiring PRs, the bot's direct push will fail instead — ask if you want it switched to open a PR in that case.

  It's still stdlib-only Python (no `pip install`), so you can also run it locally any time to preview the result before pushing:

  ```bash
  python3 scripts/bib_to_data.py
  ```

  The full field conventions (author-name abbreviation, auto-bolding the site owner, the `*` equal-contribution marker, `@misc` → Commentary instead of Publications) are documented in the comment block at the top of `references.bib`. The script fails loudly with a specific error if a required field (`author`/`title`/`journal`, or `year` for a publication) is missing — it won't silently write a broken entry, and the Action run would show that failure instead of silently doing nothing.

  This whole setup exists because GitHub Pages' automatic build can't run a real BibTeX-parsing Jekyll plugin (that would need switching Pages' source to a GitHub Actions–based deploy, e.g. to use `jekyll-scholar`). Keeping the simple branch-based Pages deploy meant moving the "source of truth" back one step instead, to a `.bib` file regenerated by a small side workflow.
- **Nav links**: add/reorder/rename entries in `docs/_data/nav.yml`. `section:` should match a page's `nav_section` front-matter value (or use `url:` matching, for anchor links) so the right nav item gets the `aria-current`/underline treatment.
- **CV**: replace `docs/cv.pdf` (same filename, so the nav link doesn't need to change).
- **Old-theme styling** (About/Contact sections, typography, colors inherited from Bootstrap): `docs/css/styles.css`.
- **New-design styling** (nav, research grid, project pages): `docs/assets/css/redesign.css`. All custom properties (colors, spacing, type scale) are defined once at the top under `:root`, prefixed `--jt-`.
- **Nav/drawer/hover-play behavior**: `docs/assets/js/redesign.js`.
- **Favicon**: `docs/favicon.ico`, referenced from `docs/_layouts/default.html`.
- **A static image not tied to a project**: drop it in `docs/assets/img/`.
- **Any new video anywhere on the site** (not just a project card): never commit a GIF directly — GIFs are huge (one used to be 92MB and was loaded by every visitor). Convert with the `ffmpeg` recipe in (c) above and embed it as a muted, autoplaying, looping `<video>`.

## (e) Adding a new section or page

**A new anchor section on the homepage** (like About/Research/Contact): add a `<section id="yourname">` to `docs/index.html`, then add an entry to `docs/_data/nav.yml` with `url: /#yourname` and `section: home` so it's reachable from the nav.

**A brand-new top-level page** (like Publications): create `docs/yourpage/index.html` with front matter —

```yaml
---
layout: default
title: Your Page
nav_section: yourpage
permalink: /yourpage/
---
```

— then write whatever content/Liquid you need below the front matter, and add it to `docs/_data/nav.yml` with `url: /yourpage/` and `section: yourpage`. Reuse `.jt-wrap`/`.jt-section` classes from `redesign.css` (see `research/index.html` or `publications/index.html`) to match the site's existing spacing and type scale, or `.container`/Bootstrap classes to match the old-theme sections instead.

**A new collection** (like `_projects/`, e.g. if you wanted a separate "Talks" or "Teaching" set of pages): add a block to the `collections:` key in `docs/_config.yml` following the `projects:` example, create the matching `_talks/` (or similar) directory, and give it its own layout in `_layouts/` if the page shape differs from `project.html`. `defaults:` in `_config.yml` is where you set a layout for every file in a collection automatically, so individual files don't need to repeat `layout:` in front matter.

## Checking mobile-friendliness / performance

Before adding any new large media file, or after any layout change:

1. Preview locally (see above), open Chrome DevTools → Device Toolbar, and check a couple of phone widths (e.g. iPhone SE, a mid-size Android). Confirm: no horizontal scroll, the nav collapses into the hamburger/drawer correctly, video backgrounds don't cause layout jumps.
2. Run a **Lighthouse** audit in Chrome DevTools (Lighthouse tab → Mobile + Desktop). Investigate anything flagged, especially:
   - Largest Contentful Paint / total page weight — usually means a new image/video isn't compressed enough.
   - Cumulative Layout Shift — usually means a missing `width`/`height` on an `<img>`/`<video>`.
3. As a sanity check on total size, `du -sh docs` should stay in the low tens of MB — if it jumps a lot after adding something, that thing probably needs compressing (see the `ffmpeg`/image-compression notes above; `cwebp` and `sips` work well for images on macOS with no install needed).

## Note on repo history size

`.git` itself is large (~300MB) because early commits included the original uncompressed GIFs before an earlier cleanup. That history isn't rewritten as part of normal edits — it would require `git filter-repo` and a force-push, which is a separate, deliberate operation, not something to do casually.
