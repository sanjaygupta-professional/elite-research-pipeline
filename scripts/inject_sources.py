#!/usr/bin/env python3
"""
inject_sources.py — enrich a baseline markdown file with source citations.

Reads a markdown file and its sidecar `<stem>.sources.yaml`; produces a
version with:
  - First mention of each source wrapped in a markdown inline hyperlink
  - Subsequent mentions appended with [^key] footnote markers
  - A '## Sources' section (grouped by type) inserted before
    '## Connections to Other Categories' (or at EOF if absent)

Idempotent: existing '## Sources' block is replaced cleanly on re-run, and
existing inline links / footnote markers are not duplicated.

Usage:
  python scripts/inject_sources.py <file.md>              # write in place
  python scripts/inject_sources.py <file.md> --check      # dry-run, print diff
  python scripts/inject_sources.py <file.md> --out X.md   # write elsewhere
  python scripts/inject_sources.py <file.md> --allow-todo # allow url: TODO entries

Sidecar format (YAML list of entries):
  - key: peng-2023
    type: paper                 # paper|report|benchmark|article|newsletter|person|organization
    authors: Peng, Kalliamvakou, et al.
    title: The Impact of AI on Developer Productivity...
    venue: arXiv:2302.06590
    year: 2023
    url: https://arxiv.org/abs/2302.06590
    first_mention_anchor: "Peng et al. (GitHub, 2023)"
    all_mentions:
      - "Peng et al."
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    sys.exit(2)


TYPE_GROUPS = [
    ("paper",        "Papers & Reports"),
    ("report",       "Papers & Reports"),
    ("benchmark",    "Benchmarks"),
    ("article",      "Articles & Newsletters"),
    ("newsletter",   "Articles & Newsletters"),
    ("person",       "People (Sources to Track)"),
    ("organization", "Organizations & Publications"),
]
SOURCES_HEADING = "## Sources"
CONNECTIONS_HEADING = "## Connections to Other Categories"


def load_sidecar(md_path: Path):
    candidates = [
        md_path.with_suffix(".sources.yaml"),
        md_path.with_suffix(md_path.suffix + ".sources.yaml"),
        md_path.parent / (md_path.stem + ".sources.yaml"),
    ]
    for p in candidates:
        if p.exists():
            with open(p) as f:
                data = yaml.safe_load(f) or []
            return p, data
    raise FileNotFoundError(
        f"No sidecar found. Tried: {', '.join(str(c) for c in candidates)}"
    )


def validate_sources(sources, allow_todo: bool):
    errors = []
    seen = set()
    for i, s in enumerate(sources):
        if not isinstance(s, dict):
            errors.append(f"entry {i}: not a mapping")
            continue
        if not s.get("key"):
            errors.append(f"entry {i}: missing 'key'")
            continue
        if s["key"] in seen:
            errors.append(f"entry {i}: duplicate key '{s['key']}'")
        seen.add(s["key"])
        url = (s.get("url") or "").strip()
        if not url and not allow_todo:
            errors.append(f"'{s['key']}': empty url (pass --allow-todo to proceed)")
        elif url.lower() == "todo" and not allow_todo:
            errors.append(f"'{s['key']}': url is TODO (pass --allow-todo to proceed)")
    return errors


def split_prose_and_tail(md: str):
    """Return (prose, tail) where tail starts at '## Connections to Other Categories'.
    If no existing '## Sources' section, prose is everything before connections.
    If there is one, we strip it out of prose."""
    lines = md.split("\n")
    sources_start = None
    connections_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == SOURCES_HEADING and sources_start is None:
            sources_start = i
        if stripped == CONNECTIONS_HEADING and connections_start is None:
            connections_start = i

    if sources_start is not None and connections_start is not None and sources_start < connections_start:
        prose = "\n".join(lines[:sources_start]).rstrip() + "\n"
        tail = "\n".join(lines[connections_start:])
        return prose, "\n" + tail
    if sources_start is not None and connections_start is None:
        prose = "\n".join(lines[:sources_start]).rstrip() + "\n"
        return prose, ""
    if connections_start is not None:
        prose = "\n".join(lines[:connections_start]).rstrip() + "\n"
        tail = "\n".join(lines[connections_start:])
        return prose, "\n" + tail
    return md.rstrip() + "\n", ""


_MASK_PATTERNS = [
    (re.compile(r"```.*?```", re.DOTALL), "fence"),
    (re.compile(r"`[^`\n]+`"), "inline_code"),
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), "image"),
    (re.compile(r"\[[^\]]*\]\([^)]*\)"), "link"),
    (re.compile(r"<!--.*?-->", re.DOTALL), "comment"),
    (re.compile(r"\[\^[A-Za-z0-9_\-]+\]"), "footnote_ref"),
]


def mask(text: str):
    segments = []

    def repl(m):
        token = f"\x00M{len(segments)}\x00"
        segments.append((token, m.group(0)))
        return token

    for pat, _label in _MASK_PATTERNS:
        text = pat.sub(repl, text)
    return text, segments


def unmask(text: str, segments):
    # Unmask in reverse order so nested masks (unlikely here) resolve correctly.
    for token, original in reversed(segments):
        text = text.replace(token, original)
    return text


def inject_first_mention(prose: str, anchor: str, url: str) -> tuple[str, bool]:
    """Replace FIRST plaintext occurrence of `anchor` with [anchor](url).
    Skips if an existing markdown link to the same URL is already present."""
    if not anchor or not url or url.strip().lower() in ("", "todo"):
        return prose, False
    # Idempotence: if this URL already appears in a markdown link, do nothing.
    if f"]({url})" in prose:
        return prose, False
    masked, segs = mask(prose)
    m = re.search(re.escape(anchor), masked)
    if not m:
        return prose, False
    start, end = m.span()
    replacement = f"[{anchor}]({url})"
    new_masked = masked[:start] + replacement + masked[end:]
    return unmask(new_masked, segs), True


def inject_footnote(prose: str, phrase: str, key: str) -> tuple[str, int]:
    """Append [^key] after every plaintext occurrence of `phrase` not already
    followed by a footnote ref (post-unmask-aware)."""
    if not phrase:
        return prose, 0
    masked, segs = mask(prose)
    marker = f"[^{key}]"
    out_parts = []
    pos = 0
    count = 0
    for m in re.finditer(re.escape(phrase), masked):
        start, end = m.span()
        # If the NEXT non-mask character-sequence is already a footnote ref, skip.
        # Because footnote refs were masked, look for a mask token pointing to one.
        tail = masked[end:end + 20]
        if tail.startswith("\x00M"):
            # Find which segment this token refers to
            tok_match = re.match(r"\x00M(\d+)\x00", tail)
            if tok_match:
                idx = int(tok_match.group(1))
                if idx < len(segs):
                    _tok, original = segs[idx]
                    if original.startswith("[^"):
                        continue
        out_parts.append(masked[pos:end])
        out_parts.append(marker)
        pos = end
        count += 1
    out_parts.append(masked[pos:])
    return unmask("".join(out_parts), segs), count


def format_citation(s: dict) -> str:
    parts = []
    for field in ("authors", "title", "venue", "year"):
        val = s.get(field)
        if val is None or val == "":
            continue
        val = str(val).strip()
        if field == "title":
            val = f"*{val}*"
        parts.append(val.rstrip("."))
    citation = ". ".join(parts).strip()
    if citation and not citation.endswith("."):
        citation += "."
    return citation


def format_sources_block(sources) -> str:
    label_by_type = dict(TYPE_GROUPS)
    # Preserve group ordering
    ordered_labels = []
    seen_labels = set()
    for _, label in TYPE_GROUPS:
        if label not in seen_labels:
            ordered_labels.append(label)
            seen_labels.add(label)
    groups = {label: [] for label in ordered_labels}
    other = []
    for s in sources:
        label = label_by_type.get((s.get("type") or "").lower())
        if label:
            groups[label].append(s)
        else:
            other.append(s)
    if other:
        groups["Other"] = other
        ordered_labels.append("Other")

    lines = [SOURCES_HEADING, ""]
    for label in ordered_labels:
        entries = groups.get(label) or []
        if not entries:
            continue
        lines.append(f"### {label}")
        lines.append("")
        entries = sorted(entries, key=lambda s: s.get("key", ""))
        for s in entries:
            key = s["key"]
            citation = format_citation(s)
            url = (s.get("url") or "").strip()
            if url and url.lower() != "todo":
                lines.append(f"[^{key}]: {citation} <{url}>".rstrip())
            else:
                lines.append(f"[^{key}]: {citation} **[needs-url]**".rstrip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render(md: str, sources, warnings=None) -> str:
    if warnings is None:
        warnings = []
    prose, tail = split_prose_and_tail(md)

    # Detect sources that were already fully processed on a prior run so we
    # can suppress spurious "not found" warnings.
    already_linked = {
        s["key"] for s in sources
        if (s.get("url") or "").strip().lower() not in ("", "todo")
        and f"]({(s.get('url') or '').strip()})" in prose
    }

    # 1) First-mention inline hyperlink (longest anchor first to reduce overlap surprises)
    sources_by_anchor_len = sorted(
        sources,
        key=lambda s: len((s.get("first_mention_anchor") or "")),
        reverse=True,
    )
    for s in sources_by_anchor_len:
        anchor = s.get("first_mention_anchor")
        url = (s.get("url") or "").strip()
        if anchor and url and url.lower() != "todo":
            prose, ok = inject_first_mention(prose, anchor, url)
            if not ok and s["key"] not in already_linked:
                warnings.append(
                    f"'{s['key']}': first_mention_anchor '{anchor}' not found in prose"
                )
    # 2) Footnote markers on all mentions (longer phrases first to avoid
    #    short-phrase-inside-long-phrase issues)
    mention_pairs = []
    for s in sources:
        key = s["key"]
        phrases = list(s.get("all_mentions") or [])
        url = (s.get("url") or "").strip()
        anchor = s.get("first_mention_anchor")
        # If the inline-link pass did NOT fire (no url / TODO), fall back to
        # footnoting the anchor too so first mention still links to the source.
        if anchor and (not url or url.lower() == "todo"):
            phrases.append(anchor)
        for phrase in phrases:
            mention_pairs.append((len(phrase), phrase, key))
    mention_pairs.sort(key=lambda t: -t[0])
    for _, phrase, key in mention_pairs:
        prose, count = inject_footnote(prose, phrase, key)
        # Suppress "not found" noise on re-run when the source is already linked
        # (all visible mentions are either inside a link or already footnoted).
        if count == 0 and key not in already_linked:
            warnings.append(f"'{key}': mention '{phrase}' not found in prose")

    sources_block = format_sources_block(sources)
    prose = prose.rstrip() + "\n"
    if tail:
        return prose + "\n" + sources_block + "\n---\n" + tail.lstrip("\n")
    return prose + "\n" + sources_block


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md", type=Path)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--allow-todo", action="store_true")
    args = ap.parse_args()

    if not args.md.exists():
        sys.stderr.write(f"Not found: {args.md}\n")
        sys.exit(2)

    original = args.md.read_text()
    sidecar_path, sources = load_sidecar(args.md)
    errors = validate_sources(sources, allow_todo=args.allow_todo)
    if errors:
        sys.stderr.write("Sidecar validation failed:\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        sys.exit(1)

    warnings = []
    new = render(original, sources, warnings=warnings)
    for w in warnings:
        sys.stderr.write(f"[warn] {w}\n")

    if args.check:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=str(args.md),
            tofile=str(args.md) + " (after injection)",
        )
        sys.stdout.writelines(diff)
        return

    out = args.out or args.md
    out.write_text(new)
    sys.stderr.write(
        f"[inject_sources] wrote {out} ({len(sources)} sources from {sidecar_path.name})\n"
    )


if __name__ == "__main__":
    main()
