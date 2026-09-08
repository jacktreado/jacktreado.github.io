# Handoff: hero, mobile nav, research grid, project pages

For `jacktreado/jacktreado.github.io`, branch `main`, GitHub Pages serving from `docs/`.

## What this bundle is

Two different things, and the distinction matters:

- **`files/`** — production code, not a mock. The CSS, the JS and the Liquid
  templates are written against the real repo (Bootstrap 5 stays loaded, the
  existing `#64a19d` / `#5fa666` palette, Varela Round + Nunito). Copy them to
  the paths shown and they work. Fidelity is high: exact colors, type and
  spacing, taken from the current `docs/css/styles.css`.
- **`previews/`** — three standalone HTML pages that demonstrate the design.
  Open `previews/hero.html` in a browser; they are not part of the site build.
  Their thumbnails are striped SVG placeholders standing in for real posters.

Scope: hero, mobile nav, research grid, project pages. About, Publications and
Contact are untouched.

## The migration, in order

The repo is currently hand-edited static HTML with no build step. The design
assumes Jekyll. That migration is the first three steps and is the only risky
part — do it on a branch and preview locally with `bundle exec jekyll serve`.

**1. Turn `docs/` into a Jekyll source.**

`docs/_config.yml`:

```yaml
short_name: Jack Treado
github_username: jacktreado
scholar_url: https://scholar.google.com/citations?hl=en&user=15DbBbwAAAAJ

collections:
  projects:
    output: true
    permalink: /research/:name/

exclude: [cv.pdf]   # keep it copied, not processed
```

`docs/_data/nav.yml`:

```yaml
- title: About
  url: /#about
  section: home
- title: Research
  url: /research/
  section: research
- title: Publications
  url: /#publications
  section: home
- title: Contact
  url: /#contact
  section: home
```

GitHub Pages already builds `docs/` with Jekyll — no Actions workflow needed
as long as every plugin used is on the Pages allowlist. Nothing here uses a
plugin.

**2. Split the current `index.html` into a layout plus a page.**

Everything from `<!DOCTYPE html>` down to the opening of `<header class="masthead">`,
and the footer/scripts at the bottom, becomes `docs/_layouts/default.html` with
`{{ content }}` between them. The remaining sections become `docs/index.html`
with `layout: default` front matter. Two changes inside the layout:

- `<body id="page-top">` → `<body id="page-top" class="jt">`
- delete the whole `<nav class="navbar ..." id="mainNav">` block, replace with
  `{% include site-nav.html %}`
- add, after the existing stylesheet link:
  `<link rel="stylesheet" href="{{ '/assets/css/redesign.css' | relative_url }}">`
- add, after `bootstrap.bundle.min.js`:
  `<script src="{{ '/assets/js/redesign.js' | relative_url }}" defer></script>`

Load order matters: `redesign.css` must come after `styles.css`.

**3. Verify nothing regressed** — About/Publications/Contact should render
identically, nav links should still jump, MathJax should still typeset.
That is a good commit to stop at.

**4. Drop in the new files.** Copy `files/docs/**` over `docs/`. Replace the
old `#projects` section in `docs/index.html` with a short teaser plus a link to
`/research/`, or remove it entirely — the grid now lives on its own page.

**5. Write one `_projects/*.md` per project.** `mesophyll-development.md` is a
working example; the front-matter keys are the whole API. `order` controls grid
position and next/prev. Your existing project copy moves across verbatim.

**6. Encode the media** (see below), drop it in `assets/video/`,
`assets/video/thumbs/` and `assets/img/posters/`, delete the placeholder SVGs.

## Video: what format, and why

Stay with **`.mp4`, H.264, `-pix_fmt yuv420p`**. It is what your clips already
are and the only encoding every browser plays. The important part is not the
container, it is that each project needs **three files**:

| File | Purpose | Budget |
| --- | --- | --- |
| `assets/img/posters/<slug>.jpg` | resting state of the card — what people actually look at | < 80 KB |
| `assets/video/thumbs/<slug>.mp4` | the hover loop, ≤ 640px wide | < 400 KB |
| `assets/video/<slug>.mp4` | the project-page hero | < 3 MB |

```bash
# poster from the first frame
ffmpeg -i source.mp4 -vf "select=eq(n\,0)" -q:v 3 assets/img/posters/slug.jpg

# thumbnail loop
ffmpeg -i source.mp4 -vf "scale=640:-2" -c:v libx264 -crf 30 -preset slow \
       -pix_fmt yuv420p -an -movflags +faststart assets/video/thumbs/slug.mp4

# hero
ffmpeg -i source.mp4 -c:v libx264 -crf 26 -preset slow \
       -pix_fmt yuv420p -an -movflags +faststart assets/video/slug.mp4
```

Rules the templates already enforce: `preload="none"` on thumbnails so nothing
downloads until hover, `preload="metadata"` on heroes, `width`/`height` on
every element so the layout cannot jump, no `autoplay` on grid thumbnails.
Six autoplaying videos is the fastest way to make the page slower than it is
today. A `.webm`/VP9 second `<source>` saves ~30% and is worth adding only if
the grid gets heavy.

## Screens

### Hero (`docs/index.html`, `.jt-hero--anchored`)

Full-viewport (`100svh`), looping muted video behind, gradient scrim
(`rgba(0,0,0,.35)` → `rgba(0,0,0,.70)` at 70% → `#000`). Content is anchored to
the **lower left**, not centered: a 4rem × 2px `#64a19d` rule, then the name,
then role, then two buttons. Name is Varela Round, uppercase,
`clamp(2rem, 7.5vw, 4.5rem)`, `letter-spacing: .18em`, clipped to a
`rgba(255,255,255,.95)` → `.62` vertical gradient — the same top-lit treatment
the current masthead uses. `max-width: 18ch` so it wraps to two or three lines
rather than one long track.

The mobile fix here is structural: `100svh` instead of `min-height: 35rem` plus
`15rem` of vertical padding, and a fluid `clamp()` type size instead of three
fixed breakpoint sizes.

### Mobile nav (`_includes/site-nav.html`)

Below `62rem`: brand left, a 44px "Menu" button right. Above: the button
disappears and a horizontal link row appears. The bar is transparent over the
hero and gains `rgba(0,0,0,.92)` + 8px backdrop blur once `scrollY > 40`.

The drawer is a right-side panel, `width: min(88vw, 22rem)`, translating in over
220ms `cubic-bezier(.22,.61,.36,1)`, with a `rgba(0,0,0,.6)` scrim. Links are
Varela Round 1.5rem, stacked, each on a hairline rule. CV / GitHub / Scholar sit
at the bottom.

It is deliberately **not** Bootstrap's `.navbar-collapse`. Collapse expands in
document flow and pushes the page down, which is the current mobile failure.
This is ~40 lines of vanilla JS in `redesign.js`: focus moves into the panel on
open and back to the hamburger on close, focus is trapped while open, Esc and
scrim-click close it, `body` scroll is locked, and an in-drawer link click
closes it after the jump.

### Research grid (`docs/research/index.html`)

`.jt-grid--roomy`: one column, two at `40rem`, two with wider gaps at `62rem`.
Cards are title-only — 4:3 media, `#0c0c0c` body, hairline border, 4px radius.

The card is a single `<a>`, so a tap anywhere navigates. Media is a `<video>`
with a `poster` and **no autoplay**; `redesign.js` calls `play()` on
`pointerenter` and `focus`, `pause()` + rewind on leave/blur, guarded by
`matchMedia("(hover: hover) and (pointer: fine)")` and by
`prefers-reduced-motion`. So: poster frame at rest, loop on hover, and on a
phone nothing plays and the tap goes straight to the project page.

Hover lift is `translateY(-4px) scale(1.02)` plus
`0 1.25rem 2.5rem rgba(0,0,0,.55)`, inside the same `(hover: hover)` query. A
small "loops on hover" cue badge sits bottom-right and fades on hover.

### Project page (`_layouts/project.html`, `hero_layout: split`)

Two columns at `62rem`: media left (`1.05fr`) with the video sticky at
`nav-height + 1.5rem`, text right (`1fr`) — back link, kicker, title, prose,
links row. Below `62rem` it stacks, media first. Prose is capped at `34rem`,
1.65 line-height, `rgba(255,255,255,.75)`.

Links are pill outlines with a monospace `#86bfbb` kind label ("Paper") followed
by the citation. Add `code`, `press` or `data` entries to the `links:` list in
front matter and they render the same way. A next/prev strip closes the page,
computed from `order`.

`hero_layout: stacked` is still implemented: full-bleed 16:9 hero, title
overlapping it by `-6rem`, links in a sticky right rail. Use it for one project
if a clip deserves the space.

## Tokens

All in `:root` at the top of `redesign.css`, prefixed `--jt-`.

Colors: `--jt-bg #000`, `--jt-bg-raised #0c0c0c`, `--jt-bg-raised-2 #151515`,
`--jt-line rgba(255,255,255,.12)`, `--jt-line-strong rgba(255,255,255,.28)`,
`--jt-ink #fff`, `--jt-ink-75`, `--jt-ink-55`, `--jt-accent #64a19d`,
`--jt-accent-hi #86bfbb`, `--jt-accent-2 #5fa666`.

Type: `--jt-font-display` Varela Round, `--jt-font-body` Nunito,
`--jt-font-mono` system mono. Scale `--jt-fs-xs .75rem` → `--jt-fs-xl 2rem`,
plus fluid `--jt-fs-hero clamp(2rem, 7.5vw, 4.5rem)` and
`--jt-fs-title clamp(1.75rem, 4.5vw, 3rem)`.

Space: `--jt-s1 .25rem` through `--jt-s9 7rem`,
`--jt-gutter clamp(1.25rem, 5vw, 3.5rem)`, `--jt-measure 34rem`,
`--jt-page-max 78rem`, `--jt-nav-h 4rem`.

Other: `--jt-radius 4px`, `--jt-shadow-lift`, `--jt-dur 220ms`,
`--jt-ease cubic-bezier(.22,.61,.36,1)`.

Everything is namespaced `.jt-*` and the box-sizing reset is scoped to `.jt`,
so nothing here can leak into the untouched Bootstrap sections.

## Accessibility, already handled

Skip link; focus trap, Esc, scrim-click and focus restore on the drawer; cards
play on `focus` as well as hover so keyboard users see the loop;
`prefers-reduced-motion` disables both the hover play and the card lift;
decorative videos are `aria-hidden` + `tabindex="-1"` so the card's name comes
from its title; 44px minimum hit targets; `aria-current="page"` on both nav
copies.

## Checks before pushing

`du -sh docs` should stay in the low tens of MB. Lighthouse mobile on
`/research/` — watch LCP, which will be the first poster JPG. DevTools device
toolbar at iPhone SE width: no horizontal scroll, drawer opens over the page
rather than pushing it, hero fits without the address bar eating it.

## Files in this bundle

```
files/docs/assets/css/redesign.css     all new styles, tokens at the top
files/docs/assets/js/redesign.js       drawer, shrink-on-scroll, hover-play
files/docs/_includes/site-nav.html     bar + drawer
files/docs/_includes/project-card.html grid card
files/docs/_includes/project-links.html
files/docs/_includes/project-more.html next / prev
files/docs/_layouts/project.html       both hero layouts
files/docs/research/index.html         the grid page
files/docs/_projects/mesophyll-development.md   worked example
previews/                              open previews/hero.html
```
