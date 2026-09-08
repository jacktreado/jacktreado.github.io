# Migration: static HTML → Jekyll

Everything below happens inside `docs/`, which is what GitHub Pages already
serves. Nothing is deleted until step 5.

## 0. What changed conceptually

Your `docs/index.html` was one file doing three jobs: page chrome (head, nav,
footer, scripts), home-page content, and the research + publications content.
The split separates them:

| Job | New file |
| --- | --- |
| Chrome — head, nav, footer, scripts | `docs/_layouts/default.html` |
| Home page — masthead, About, research teaser, Contact | `docs/index.html` |
| Research index (card grid) | `docs/research/index.html` |
| One page per project | `docs/_projects/*.md` |
| Publications | `docs/publications/index.html` + `docs/_data/publications.yml` |

The nav no longer lives in the page. It comes from `_includes/site-nav.html`,
which reads its links from `_data/nav.yml`.

## 1. Drop the files in

From this handoff:

```
jekyll/_config.yml               → docs/_config.yml
jekyll/_data/nav.yml             → docs/_data/nav.yml
jekyll/_data/publications.yml    → docs/_data/publications.yml
jekyll/_data/commentary.yml      → docs/_data/commentary.yml
jekyll/_layouts/default.html     → docs/_layouts/default.html
jekyll/_layouts/project.html     → docs/_layouts/project.html
jekyll/_includes/*.html          → docs/_includes/
jekyll/index.html                → docs/index.html      (see step 5)
jekyll/research/index.html       → docs/research/index.html
jekyll/publications/index.html   → docs/publications/index.html
jekyll/_projects/*.md            → docs/_projects/
site/css/redesign.css            → docs/assets/css/redesign.css
site/js/redesign.js              → docs/assets/js/redesign.js
```

Your existing `docs/css/styles.css`, `docs/css/academicons.css`,
`docs/js/scripts.js`, `docs/assets/**` and `docs/cv.pdf` stay exactly where
they are. `default.html` still loads all of them; `redesign.css` loads *after*
`styles.css` and overrides it.

Add a `Gemfile` at the repo root so local and remote builds match:

```ruby
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "webrick"   # Ruby 3+ needs this
```

## 2. Test locally before touching anything live

```bash
gem install bundler
bundle install
bundle exec jekyll serve --source docs --livereload
```

Open <http://127.0.0.1:4000>. Check, in this order:

1. **Home** — masthead video autoplays, About renders with the headshot,
   Contact card shows. Resize the window under 576px: the hamburger appears,
   the drawer slides in, Esc closes it, and **nothing overflows sideways**.
2. **`/research/`** — the card grid renders one card per file in `_projects/`.
   Posters show at rest; hovering plays the clip on desktop.
3. **`/research/mesophyll-development/`** — project page renders, MathJax
   typesets the `\({\cal A}\)` expression, "All research" link goes back.
4. **`/publications/`** — every year heading and paper appears, in reverse
   chronological order, with working DOI links.
5. **Console** — should be clean. A 404 on a `.mp4` or poster just means that
   project's video isn't encoded yet.

If `bundle exec` fails, `jekyll serve --source docs` with a system Jekyll works
too; the Gemfile only guarantees you get the same version Pages uses.

## 3. Move the research content into `_projects/`

Each of the five blocks in your old Research section becomes one file. Copy
`_projects/mesophyll-development.md` as the pattern:

```markdown
---
title: Deformability and response
kicker: Jamming
order: 2
hero_video: /assets/video/modes.mp4      # omit for an image-only project
hero_poster: /assets/img/modes.png
hero_width: 689
hero_height: 752
thumb_video: /assets/video/modes-thumb.mp4
thumb_poster: /assets/img/modes-poster.jpg
thumb_width: 640
thumb_height: 400
caption: Normal modes of jammed deformable particle packings.
links:
  - label: Phys. Rev. Materials
    url: https://journals.aps.org/prmaterials/abstract/10.1103/PhysRevMaterials.5.055605
---

Body copy in Markdown. Paste the paragraph from the old page verbatim —
MathJax still works, so `\( {\cal A} = p^2/4\pi a \)` renders.
```

`order` controls grid position (ascending). `permalink` is automatic:
`/research/<filename>/`. The home-page teaser shows the first three by `order`;
change `limit: 3` in `docs/index.html` to show more or fewer.

Encode the thumbnail clip and poster with the ffmpeg recipes in `README.md`
before adding a project — the poster is the card's resting state, so a missing
one leaves a grey box.

## 4. Add a publication

Append an entry to `docs/_data/publications.yml`:

```yaml
- year: 2026
  authors: '<b>J. D. Treado</b>, A. N. Other'
  title: Title with a trailing period.
  journal: Phys. Rev. Lett.
  url: https://doi.org/...
  volume: 136
  pages: '018101'
```

The page regroups by year automatically — no HTML to touch. Wrap `pages` and
zero-padded numbers in quotes so YAML keeps them as strings. Single quotes
around `authors` let you use `'` inside by doubling it (`O''Hern`), which is
why the existing entries look like that.

## 5. Cut over

Only after step 2 passes on every page:

```bash
git mv docs/index.html docs/index-old.html    # keep it until you're happy
cp <handoff>/jekyll/index.html docs/index.html
git add -A && git commit -m "Split index into Jekyll layout + pages" && git push
```

In the repo's **Settings → Pages**, confirm the source is still
`main` / `/docs`. Pages detects `_config.yml` and switches from "static files"
to a Jekyll build on the next push; the first build takes a minute or two
longer than usual. Watch the **Actions** tab — a failed build there is the one
failure mode that shows you a live-but-stale site with no other warning.

Delete `docs/index-old.html` once the live site looks right.

## Two things to know

- **`_config.yml` changes need a server restart.** Everything else hot-reloads.
- **A file starting with `---` gets processed by Jekyll; one that doesn't is
  copied verbatim.** That is why `research/index.html` has front matter and
  `css/styles.css` does not.
