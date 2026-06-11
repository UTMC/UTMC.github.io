# UTMC website generator

Web site generater for UTMC (University of Tokyo Microcomputer Club).

This generator is written in python3.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Run:

```sh
cd scripts
uv sync
```

## How to update the website

1. Run `git pull` or `git pull --rebase`.
2. Create or update pages in Markdown format.
3. From the repository root, run:

```sh
./scripts/update.sh
```

4. Review generated files.
5. Commit and push changes.

## Source documents and URL format

All pages are written in Markdown.

Raw HTML embedded in Markdown is allowed and copied to generated HTML as-is. This generator assumes that all Markdown files are written by trusted maintainers.

Metadata for each page is written as YAML frontmatter.

A Markdown file is converted to an HTML file at the corresponding path:

```txt
/path/to/page.md        -> /path/to/page.html
/path/to/index.md       -> /path/to/index.html
/path/to/subdir/hoge.md -> /path/to/subdir/hoge.html
```

Generated public URLs must omit the `.html` extension.

For non-index pages, generated URLs must not have a trailing slash:

```txt
/path/to/page.html -> /path/to/page
```

For index pages, generated URLs must use the directory URL:

```txt
/index.html           -> /
/path/to/index.html   -> /path/to/
```

Therefore, `https://www.utmc.or.jp/subdir/` is correct, and `https://www.utmc.or.jp/subdir/index` is incorrect.

## Markdown frontmatter

The following frontmatter fields are supported.

Required:

* `title`: page title used for `<title>`, `og:title`, and `twitter:title`.

Optional:

* `site_name`: site name used for `og:site_name`. Defaults to the value in `config.toml`, then `UTMC`.
* `description`: page description used for `og:description` and `twitter:description`.
* `image`: filename of the OGP image relative to `${ROOT}/files/`. Used for `og:image` and `twitter:image`.
* `layout`: HTML template filename relative to `${ROOT}/_layout/`. Defaults to `layout.html`.

Example:

```yaml
---
title: Example page
description: This is an example page.
image: example.png
layout: layout.html
---
```

## Configuration

All global configuration is stored in `config.toml` at the repository root.

Recommended fields:

```toml
base_url = "https://www.utmc.or.jp"
site_name = "UTMC"
default_layout = "layout.html"
files_dir = "files"
layout_dir = "_layout"
```

## Layouts

Layouts are HTML templates stored under `${ROOT}/_layout/`.

The default layout is `${ROOT}/_layout/layout.html`.

A layout receives at least the following variables:

* `title`
* `site_name`
* `description`
* `content`
* `canonical_url`
* `og_image_url`

## Build behavior

`scripts/update.sh` must be executed from the repository root.

The script generates HTML files from Markdown files and exits with a non-zero status code if the build fails.

The build must fail when:

* frontmatter is invalid
* required metadata is missing
* the specified layout file does not exist
* the specified image file does not exist
* two Markdown files generate the same output path

The build should warn when:

* `description` is missing
* `image` is missing
