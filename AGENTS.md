# AGENTS.md

This file gives coding agents the context needed to work in this repository
without re-deriving it from scratch. Human contributors can also use it as a
reference; the canonical human-facing overview is [README.md](README.md).

## What this repo is

Source for [José Hisse's personal blog](https://www.josehisse.dev), a
static site built with [Hugo](https://gohugo.io/) and deployed on
[Cloudflare Pages](https://pages.cloudflare.com/). Content is written in
Portuguese (pt-br).

## Repository structure

```text
.github/workflows/   GitHub Actions (link checking, markdown lint, pre-commit)
archetypes/          Hugo archetype for new posts
assets/              CSS processed by Hugo (main.css, syntax highlight themes)
content/
  _index.md          Homepage content
  blog/<slug>/        One folder per post
    index.md          Post content + frontmatter
    images/            Post-local images referenced from index.md
hugo.yaml            Hugo site configuration
layouts/             Hugo templates and render hooks
static/               Files served as-is (favicon, Cloudflare Pages _headers/_redirects)
.markdownlint.json    markdownlint-cli2 config (extends .prettierrc.json)
.prettierrc.json      Prettier config, also the base for markdownlint
.pre-commit-config.yaml  pre-commit hooks (whitespace, EOF, YAML, large files)
```

## Content conventions

- All posts live under `content/blog/<slug>/index.md`. The folder name is
  the slug and becomes the URL (see `permalinks.blog` in `hugo.yaml`).
- Required frontmatter:

  ```yaml
  ---
  title: "Título do Post"
  date: AAAA-MM-DD
  layout: post
  ---
  ```

  Use `draft: true` while a post isn't ready to publish (see
  `archetypes/default.md`).
- The post title lives only in frontmatter. In-body headings start at `##`
  (h2); don't repeat the title as an `# h1`.
- Images go in `content/blog/<slug>/images/` and are referenced with a
  path relative to the post, e.g. `![alt](images/nome-da-imagem.png)`.
  Source images can be PNG/JPEG — do **not** pre-convert to WebP by hand.
- WebP is generated automatically at build time by the render hook at
  `layouts/_default/_markup/render-image.html`: it resizes any image wider
  than 1400px (Lanczos), then emits a `<picture>` with a fingerprinted WebP
  source and a fingerprinted JPEG `<img>` fallback for older browsers. See
  the post
  [Gerando imagens WebP com Hugo](content/blog/gerando-imagens-webp-com-hugo/index.md)
  for the full rationale. Don't add a separate image-conversion script or
  step — the render hook is the single source of truth for this.
- New posts can be scaffolded with `hugo new content blog/<slug>/index.md`
  (uses `archetypes/default.md`).

## Local build & verification

Hugo isn't vendored in this repo; install the extended edition locally
(Cloudflare Pages controls the build-time Hugo version separately, via its
own dashboard config, not a file in this repo).

```bash
hugo server --buildDrafts --noHTTPCache --disableFastRender --buildFuture   # live preview
hugo build --buildFuture                                                     # production-equivalent build, fails on template errors
```

Before opening a PR that touches content or templates, run a local
`hugo build` and confirm it succeeds with no errors.

## CI

Three workflows in `.github/workflows/`:

- **`markdown-lint.yaml`** — `markdownlint-cli2` over `content/**/*.md` on
  every push to `main`/`master` and every PR. Fix locally with
  `markdownlint-cli2 --config .markdownlint.json "content/**/*.md"`.
- **`pre-commit.yaml`** — runs the hooks in `.pre-commit-config.yaml`
  (trailing whitespace, end-of-file fixer, YAML validation, large-file
  check) on every PR. Install locally with `pre-commit install` /
  `pre-commit run --all`.
- **`check-links.yaml`** — [lychee](https://github.com/lycheeverse/lychee)
  link checker over `content/blog/**/*.md`, on a weekly cron (Saturdays)
  and on manual dispatch. On failure it opens a GitHub issue with the
  report instead of failing the run (`fail: false`); treat that issue as
  the source of truth for broken links rather than re-running lychee
  locally unless you're actively debugging one.
- Secret scanning (GitHub native, `security_and_analysis`) and Dependabot
  run outside of these workflow files, via repo settings / `.github/dependabot.yml`.

## PR & merge flow

- Never commit directly to `master` — always a branch + PR.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for
  commit messages and PR titles.
- Keep PRs minimal in scope — no drive-by refactors bundled with an
  unrelated change.
- Squash-merge only. `delete_branch_on_merge` is enabled, so merged
  branches are cleaned up automatically.
- Dependabot PRs: auto-merge is limited to patch-level, dev/build-only
  dependency bumps, and only after CI passes. See `.github/dependabot.yml`.

## Sensitive paths — do not merge without explicit human sign-off

Opening a PR that touches these is fine; **merging** requires an explicit
go-ahead from the repo owner (José Hisse), even if CI is green:

- `.github/workflows/**` — CI behavior and any third-party Action pin.
- `.github/dependabot.yml` — dependency update / auto-merge policy.
- `CODEOWNERS`
- Branch protection rules / rulesets for `master`
- Any repository secret

When adding or updating a third-party GitHub Action:

- Pin by full commit SHA, never a mutable tag like `@v4`.
- Only use Actions from a publisher recognized and actively maintained by
  the community; prefer official `actions/*` Actions. Verify this even for
  an Action that's already SHA-pinned in the repo — re-check before
  bumping its pin.
