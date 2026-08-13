#!/usr/bin/env python3
"""Validate required frontmatter fields on every blog post.

Catches malformed frontmatter (wrong type, missing field, typo) that
`hugo build` can silently swallow instead of failing on - see AGENTS.md
for the required-frontmatter contract this enforces.
"""
import datetime
import pathlib
import re
import sys

import yaml

FRONTMATTER_RE = re.compile(r"^﻿?---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
POSTS_DIR = pathlib.Path("content/blog")


def check_post(path):
    errors = []
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return [f"{path}: missing frontmatter block"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"{path}: invalid YAML frontmatter ({exc})"]

    if not isinstance(frontmatter, dict):
        return [f"{path}: frontmatter must be a mapping"]

    title = frontmatter.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"{path}: 'title' must be a non-empty string")

    date = frontmatter.get("date")
    if not isinstance(date, (datetime.date, datetime.datetime)):
        errors.append(
            f"{path}: 'date' must be an unquoted YAML date (AAAA-MM-DD), "
            f"got {date!r}"
        )

    layout = frontmatter.get("layout")
    if layout != "post":
        errors.append(f"{path}: 'layout' must be 'post', got {layout!r}")

    draft = frontmatter.get("draft")
    if draft is not None and not isinstance(draft, bool):
        errors.append(f"{path}: 'draft' must be a boolean, got {draft!r}")

    return errors


def main():
    posts = sorted(POSTS_DIR.glob("*/index.md"))
    if not posts:
        print(f"No posts found under {POSTS_DIR}/", file=sys.stderr)
        return 1

    errors = []
    for post in posts:
        errors.extend(check_post(post))

    if errors:
        print(f"Frontmatter validation failed ({len(errors)} issue(s)):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Frontmatter OK ({len(posts)} posts checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
