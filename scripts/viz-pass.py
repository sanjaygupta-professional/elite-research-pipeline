#!/usr/bin/env python3
"""
viz-pass.py — Inject Mermaid diagrams (and optionally a PaperBanana concept diagram)
into a research baseline category file.

Usage:
    python scripts/viz-pass.py <path-to-category-file> [--with-paperbanana] [--dry-run]

See knowledge-system/design/07-visualization-guide.md for the full vocabulary.
"""

import re
import sys
import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PAPERBANANA_DIR = Path("/home/sanjayegupta/projects/app-engineering-methods/tools/PaperBanana")

# Axis mapping per the visualization guide
EVIDENCE_X = {1: 0.1, 2: 0.3, 3: 0.5, 4: 0.75, 5: 0.9}
HORIZON_Y  = {"Now": 0.1, "Near": 0.35, "Med": 0.65, "Far": 0.9}

TRAJ_ABBREV = {"Em": "Emerging", "Ac": "Accelerating", "Ma": "Maturing", "Sh": "Shifting",
               "Emerging": "Emerging", "Accelerating": "Accelerating",
               "Maturing": "Maturing", "Shifting": "Shifting"}


# ──────────────────────────────────────────────
# Parsers
# ──────────────────────────────────────────────

def parse_category_name(content: str) -> str:
    m = re.search(r'^# (.+)', content, re.MULTILINE)
    return m.group(1).strip() if m else "Category"


def parse_signals(content: str) -> list[dict]:
    """Extract ranked shortlist signals with their 5-dimension profiles."""
    signals = []
    # Match signal headers + profile lines — hyphenated H/T values like H-Post-hype handled by [\w-]+
    pattern = re.compile(
        r'### \d+\.\s+(.+?)\n(?:.*\n)*?\*\*Profile:\*\*\s+E(\d)\s+T-([\w-]+)\s+U(\d)\s+H-([\w-]+)\s+Z-([\w-]+)',
        re.MULTILINE
    )
    for m in pattern.finditer(content):
        name = m.group(1).strip()
        short_name = (name[:24] + "…") if len(name) > 25 else name
        e = int(m.group(2))
        z_raw = m.group(6)
        z_map = {"Now": "Now", "Near": "Near", "Med": "Med", "Medium": "Med",
                 "Far": "Far", "Near-term": "Near", "Medium-term": "Med"}
        z = z_map.get(z_raw, "Near")
        x = EVIDENCE_X.get(e, 0.5)
        y = HORIZON_Y.get(z, 0.35)
        signals.append({"name": short_name, "e": e, "z": z, "x": x, "y": y})
    return signals


def parse_developments(content: str) -> list[dict]:
    """Extract key developments with approximate dates."""
    devs = []
    section_m = re.search(r'## Key Developments.*?\n(.*?)(?=\n## )', content, re.DOTALL)
    if not section_m:
        return devs
    section = section_m.group(1)

    for m in re.finditer(r'-\s+\*\*(.+?)\*\*:?\s+(.+?)(?=\n|$)', section):
        title = m.group(1).strip().rstrip(":")  # strip trailing colon
        date_m = re.search(r'\(([A-Z][a-z]+ \d{4}|Q[1-4] \d{4}|H[12] \d{4}|\d{4})\)', title)
        date = date_m.group(1) if date_m else ""
        label = re.sub(r'\s*\(.*?\)', '', title).strip().rstrip(":")
        if len(label) > 48:
            label = label[:47].rsplit(' ', 1)[0] + "…"
        devs.append({"date": date, "label": label, "year": _extract_year(date or title)})

    return devs[:8]


def _extract_year(text: str) -> str:
    m = re.search(r'(2024|2025|2026)', text)
    return m.group(1) if m else "2026"


def parse_debate(content: str) -> dict:
    """Extract optimist/skeptic labels for the debate tension map."""
    result = {"optimist": "Value creation path", "skeptic": "Caution / constraint path",
              "synthesis": "Both right, sequentially"}
    section_m = re.search(r'## The Debate\n(.*?)(?=\n## )', content, re.DOTALL)
    if not section_m:
        return result

    section = section_m.group(1)
    # Extract the citation labels from **Optimist case (...):** and **Skeptic case (...):** headers
    opt_m = re.search(r'\*\*Optimist\s+case\s*\(([^)]{5,50})\)', section)
    skep_m = re.search(r'\*\*Skeptic[^(]*\(([^)]{5,50})\)', section)
    synth_m = re.search(r'\*\*What the evidence supports[^:]*:\*\*\s*\n([A-Z].{15,80}?)[\.\n]', section, re.DOTALL)

    if opt_m:
        result["optimist"] = opt_m.group(1).strip()[:40]
    if skep_m:
        result["skeptic"] = skep_m.group(1).strip()[:40]
    if synth_m:
        result["synthesis"] = synth_m.group(1).strip()[:45]

    return result


def parse_connections(content: str) -> list[dict]:
    """Extract connected categories for the mindmap."""
    conns = []
    section_m = re.search(r'## Connections to Other Categories\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not section_m:
        return conns

    # Match "Category 01 (Name)" anywhere in a bullet — flexible enough for any bold formatting
    for m in re.finditer(
        r'Category\s+(\d+)\s+\(([^)]{3,40})\)',
        section_m.group(1)
    ):
        cat_num = m.group(1)
        cat_name = m.group(2).strip()
        conns.append({"num": cat_num, "name": cat_name[:20]})

    return conns[:7]


def _connection_keyword(desc: str) -> str:
    """Extract a 1-2 word concept from a connection description."""
    # Try to find the first meaningful noun phrase
    for phrase in ["constrains", "feeds into", "depends on", "shapes", "drives", "enables"]:
        if phrase in desc.lower():
            idx = desc.lower().index(phrase)
            tail = desc[idx + len(phrase):].strip()
            return tail[:25].split(".")[0].strip()
    return desc[:25].split(".")[0].strip()


# ──────────────────────────────────────────────
# Mermaid generators
# ──────────────────────────────────────────────

def generate_timeline(developments: list[dict], category_name: str) -> str:
    if not developments:
        return ""
    by_year: dict[str, list] = {}
    for d in developments:
        by_year.setdefault(d["year"], []).append(d)

    lines = [f"```mermaid", f"timeline", f"    title Key Developments — {category_name}"]
    for year in sorted(by_year.keys()):
        lines.append(f"    section {year}")
        for d in by_year[year]:
            period = d["date"] if d["date"] else year
            lines.append(f"        {period} : {d['label']}")
    lines.append("```")
    return "\n".join(lines)


def generate_debate_map(debate: dict, category_name: str) -> str:
    # debate values are strings after the updated parse_debate()
    opt = debate.get("optimist", "Value creation at scale")
    skep = debate.get("skeptic", "Organizational barriers persist")
    synth = debate.get("synthesis", "Both right, sequentially")

    return (
        "```mermaid\n"
        "graph LR\n"
        "    E[Evidence Base] --> T{Central Tension}\n"
        f"    T -->|Optimist| O[\"{opt}\"]\n"
        f"    T -->|Skeptic| S[\"{skep}\"]\n"
        f"    O --> C[\"{synth}\"]\n"
        "    S --> C\n"
        "```"
    )


def generate_signal_quadrant(signals: list[dict], category_name: str) -> str:
    if not signals:
        return ""
    lines = [
        "```mermaid",
        "quadrantChart",
        f"    title Signal Landscape — {category_name}",
        "    x-axis Theoretical --> Industry Standard",
        "    y-axis Immediate --> Far Future",
        "    quadrant-1 Strategic Bets",
        "    quadrant-2 Watch Closely",
        "    quadrant-3 Monitor",
        "    quadrant-4 Act Now",
    ]
    for s in signals:
        lines.append(f"    {s['name']}: [{s['x']}, {s['y']}]")
    lines.append("```")
    return "\n".join(lines)


def generate_connections_description(connections: list[dict], category_name: str, content: str) -> str:
    """Generate a prose description of category connections for PaperBanana input."""
    if not connections:
        return f"The {category_name} research category within the Possibilities with Probabilities AI knowledge system."

    # Extract connection descriptions from the Connections section
    section_m = re.search(r'## Connections to Other Categories\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if section_m:
        return (
            f"Category connection map for: {category_name}\n\n"
            f"This knowledge category connects to {len(connections)} other research areas:\n\n"
            + section_m.group(1).strip()
        )
    return f"The {category_name} category connects to: " + ", ".join(c['name'] for c in connections)


# ──────────────────────────────────────────────
# Injector
# ──────────────────────────────────────────────

def section_already_has_mermaid(section_content: str) -> bool:
    return "```mermaid" in section_content


def inject_after_header(content: str, header_pattern: str, diagram: str) -> str:
    """Insert diagram block after the first matching section header.
    Skips if a mermaid block already exists between this header and the next."""
    header_re = re.compile(r'(^' + re.escape(header_pattern) + r'.*?\n)', re.MULTILINE)
    m = header_re.search(content)
    if not m:
        return content

    insert_pos = m.end()
    # Find the end of this section (next ## header or end of file)
    next_header_m = re.search(r'\n## ', content[insert_pos:])
    section_end = insert_pos + next_header_m.start() if next_header_m else len(content)
    section_body = content[insert_pos:section_end]

    if section_already_has_mermaid(section_body):
        return content  # idempotent — don't double-inject

    # Skip any immediate blank lines after header, then insert
    insertion = "\n" + diagram + "\n"
    return content[:insert_pos] + insertion + content[insert_pos:]


def replace_mermaid_block(content: str, header_pattern: str, new_diagram: str) -> str:
    """Replace an existing mermaid block in the named section (for weekly scan updates)."""
    header_re = re.compile(r'(^' + re.escape(header_pattern) + r'.*?\n)', re.MULTILINE)
    m = header_re.search(content)
    if not m:
        return inject_after_header(content, header_pattern, new_diagram)

    insert_pos = m.end()
    next_header_m = re.search(r'\n## ', content[insert_pos:])
    section_end = insert_pos + next_header_m.start() if next_header_m else len(content)
    section_body = content[insert_pos:section_end]

    # Replace existing mermaid block
    mermaid_re = re.compile(r'```mermaid.*?```', re.DOTALL)
    if mermaid_re.search(section_body):
        new_body = mermaid_re.sub(new_diagram, section_body, count=1)
        return content[:insert_pos] + new_body + content[section_end:]

    # No existing block — fall back to inject
    return inject_after_header(content, header_pattern, new_diagram)


# ──────────────────────────────────────────────
# PaperBanana
# ──────────────────────────────────────────────

def run_paperbanana(content_text: str, caption: str, output_path: Path) -> str | None:
    """Invoke PaperBanana CLI and return the path of the selected candidate PNG."""
    if not PAPERBANANA_DIR.exists():
        print(f"  [PaperBanana] ERROR: not found at {PAPERBANANA_DIR}", file=sys.stderr)
        return None

    # Write content to a UNIQUE temp file (parallel calls must not clobber each other)
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", prefix="viz-pb-", delete=False) as tf:
        tf.write(content_text)
        content_file = Path(tf.name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Output stem — PaperBanana appends _0, _1, _2 for multiple candidates
    output_stem = output_path.with_suffix("")

    cmd = [
        str(PAPERBANANA_DIR / ".venv" / "bin" / "python"),
        str(PAPERBANANA_DIR / "skill" / "run.py"),
        "--content-file", str(content_file),
        "--caption", caption,
        "--task", "diagram",
        "--output", str(output_stem) + ".png",
        "--aspect-ratio", "16:9",
        "--num-candidates", "3",
        "--max-critic-rounds", "2",
        "--retrieval-setting", "none",
        "--exp-mode", "demo_full",
    ]

    print(f"  [PaperBanana] Running (this takes 10-30 min for 3 candidates)...")
    print(f"  [PaperBanana] Output: {output_stem}_0.png, _1.png, _2.png")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PAPERBANANA_DIR))
        if result.returncode != 0:
            print(f"  [PaperBanana] FAILED:\n{result.stderr}", file=sys.stderr)
            return None

        # Find the first candidate
        candidate = Path(str(output_stem) + "_0.png")
        if candidate.exists():
            # Copy candidate_0 to the canonical path for embedding
            import shutil
            shutil.copy(candidate, output_path)
            print(f"  [PaperBanana] Candidate _0 copied to {output_path}")
            print(f"  [PaperBanana] Review _1 and _2 manually; replace if preferred.")
            return str(output_path)
        else:
            print(f"  [PaperBanana] Candidate _0 not found at {candidate}", file=sys.stderr)
            return None
    except FileNotFoundError:
        print(f"  [PaperBanana] Python binary not found at {PAPERBANANA_DIR / '.venv' / 'bin' / 'python'}", file=sys.stderr)
        return None


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Inject visualizations into a research category file")
    parser.add_argument("file", help="Path to the category markdown file")
    parser.add_argument("--with-paperbanana", action="store_true",
                        help="Also generate PaperBanana concept diagram (Gemini API cost)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print generated diagrams without writing to file")
    parser.add_argument("--update-quadrant-only", action="store_true",
                        help="Only regenerate the Signal Landscape quadrant (used by weekly scan)")
    args = parser.parse_args()

    category_file = Path(args.file)
    if not category_file.exists():
        print(f"ERROR: file not found: {category_file}", file=sys.stderr)
        sys.exit(1)

    content = category_file.read_text()
    category_name = parse_category_name(content)
    slug = category_file.stem  # e.g. "02-enterprise-ai-org-transformation"
    # Remove the leading "NN-" number prefix for slug
    slug_clean = re.sub(r'^\d+-', '', slug)

    print(f"[viz-pass] Category: {category_name}")
    print(f"[viz-pass] File: {category_file}")
    print(f"[viz-pass] Slug: {slug_clean}")

    signals = parse_signals(content)
    print(f"[viz-pass] Signals found: {len(signals)}")

    # Full viz pass
    developments = parse_developments(content)
    debate = parse_debate(content)
    connections = parse_connections(content)

    print(f"[viz-pass] Developments: {len(developments)}, Connections: {len(connections)}")

    # Only generate Mermaid diagrams for SIMPLE flows:
    #   - Timeline (sequential dates)
    #   - Debate Tension Map (5-node LR flow)
    # Complex visuals (Concept, Connections, Signal Landscape) are handled by PaperBanana.
    timeline = generate_timeline(developments, category_name)
    debate_map = generate_debate_map(debate, category_name)

    if args.dry_run:
        print("\n=== Timeline (Mermaid) ===")
        print(timeline)
        print("\n=== Debate Map (Mermaid) ===")
        print(debate_map)
        print("\n=== Signal Landscape (PaperBanana — requires --with-paperbanana) ===")
        print(f"Signals: {len(signals)}")
        print("\n=== Connections Map (PaperBanana — requires --with-paperbanana) ===")
        print(f"Connections: {len(connections)}")
        return

    # Inject Mermaid diagrams (idempotent)
    modified = content
    if timeline:
        modified = inject_after_header(modified, "## Key Developments", timeline)
        print("[viz-pass] ✓ Timeline (Mermaid) injected")
    if debate_map:
        modified = inject_after_header(modified, "## The Debate", debate_map)
        print("[viz-pass] ✓ Debate Map (Mermaid) injected")

    # PaperBanana diagrams — build specs, run in parallel, then inject results.
    # Each PaperBanana call is an independent subprocess; running 3 concurrently
    # cuts wall time from ~12 min to ~4 min per category.
    if args.with_paperbanana:
        images_dir = REPO_ROOT / "knowledge-system" / "assets" / "images" / slug_clean
        specs = []  # each: dict(key, content, caption, output_path, section_header, caption_md)

        # --- Spec 1: Concept diagram (top of file)
        state_m = re.search(r'## State of the Field.*?\n(.*?)(?=\n## )', content, re.DOTALL)
        dev_m = re.search(r'## Key Developments.*?\n(.*?)(?=\n## )', content, re.DOTALL)
        first_section_m = re.search(r'## .+?\n(.*?)(?=\n## )', content, re.DOTALL)
        pb_content = ""
        if state_m:
            pb_content += state_m.group(1).strip() + "\n\n"
        elif first_section_m:
            pb_content += first_section_m.group(1).strip() + "\n\n"
        if dev_m:
            pb_content += dev_m.group(1).strip()
        specs.append({
            "key": "concept",
            "content": pb_content,
            "caption": f"Conceptual overview of {category_name} — key forces, dynamics, "
                       f"and transformation patterns in AI research intelligence",
            "output_path": images_dir / "concept-diagram-b.png",
        })

        # --- Spec 2: Signal Landscape
        if signals:
            sl_lines = [
                f"Signal Landscape for {category_name} — a scatter plot positioning "
                f"the ranked shortlist signals by Evidence Strength (x-axis, 1-5 scale) "
                f"and Time Horizon (y-axis: Now, Near, Medium, Far future).\n",
                "The plot has four quadrants: Strategic Bets (top-right, high evidence + "
                "long-term), Watch Closely (top-left, low evidence + long-term), Monitor "
                "(bottom-left, low evidence + near-term), Act Now (bottom-right, high "
                "evidence + near-term).\n",
                "Signals to plot:",
            ]
            for s in signals:
                sl_lines.append(f"- {s['name'].rstrip('…')}: Evidence={s['e']} of 5, Horizon={s['z']}")
            specs.append({
                "key": "signal_landscape",
                "content": "\n".join(sl_lines),
                "caption": f"Signal Landscape — {category_name}. Scatter plot of "
                           f"ranked shortlist signals by Evidence Strength and Time Horizon",
                "output_path": images_dir / "signal-landscape-b.png",
            })

        # --- Spec 3: Connections map
        if connections:
            specs.append({
                "key": "connections",
                "content": generate_connections_description(connections, category_name, content),
                "caption": f"Knowledge system connections for {category_name} — "
                           f"how this category relates to the other 9 research areas in "
                           f"the Possibilities with Probabilities intelligence framework",
                "output_path": images_dir / "connections-map-b.png",
            })

        # Run all PaperBanana calls in parallel — 3 concurrent subprocesses, 3 candidates each
        print(f"[viz-pass] Running {len(specs)} PaperBanana calls in parallel (3 candidates each)...")
        results = {}
        with ThreadPoolExecutor(max_workers=len(specs)) as executor:
            futures = {
                executor.submit(run_paperbanana, spec["content"], spec["caption"], spec["output_path"]): spec["key"]
                for spec in specs
            }
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                    print(f"[viz-pass] ✓ {key} diagram complete")
                except Exception as e:
                    print(f"[viz-pass] ✗ {key} diagram FAILED: {e}")
                    results[key] = None

        # Inject results into markdown (after all PaperBanana calls complete)
        if results.get("concept"):
            rel_path = os.path.relpath(results["concept"], category_file.parent)
            img_block = (f"\n![{category_name} — Concept Diagram]({rel_path})\n"
                         f"*Conceptual overview — generated via PaperBanana (color infographic)*\n")
            meta_end_m = re.search(r'\*\*Baseline status:\*\*.*?\n', modified)
            if meta_end_m:
                ins = meta_end_m.end()
                modified = modified[:ins] + "\n---\n" + img_block + "\n---\n" + modified[ins:]
            print(f"[viz-pass] ✓ Concept diagram injected")

        if results.get("signal_landscape"):
            rel_path = os.path.relpath(results["signal_landscape"], category_file.parent)
            img_block = (f"\n![Signal Landscape — {category_name}]({rel_path})\n"
                         f"*Signal landscape (Evidence vs. Time Horizon) — PaperBanana*\n")
            modified = inject_after_header(modified, "## Signal Assessment", img_block.strip())
            print(f"[viz-pass] ✓ Signal Landscape injected")

        if results.get("connections"):
            rel_path = os.path.relpath(results["connections"], category_file.parent)
            img_block = (f"\n![{category_name} — Connections Map]({rel_path})\n"
                         f"*Category connections map — generated via PaperBanana*\n")
            modified = inject_after_header(modified, "## Connections to Other Categories", img_block.strip())
            print(f"[viz-pass] ✓ Connections map injected")

    category_file.write_text(modified)
    print(f"[viz-pass] File written: {category_file}")
    print(f"[viz-pass] Done.")


if __name__ == "__main__":
    main()
