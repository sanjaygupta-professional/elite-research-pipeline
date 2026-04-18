# pipeline/templates.py
"""Zero-token publishing templates.

Fill intel card data into pre-built templates for LinkedIn, X, newsletter.
Only use Claude (via skills) for deep analysis pieces.
"""

from __future__ import annotations


def linkedin_post(card: dict, source_title: str, source_url: str) -> str:
    """Generate a LinkedIn post from an intel card. Zero tokens."""
    possibilities = card.get("possibilities", [])
    if not possibilities:
        return ""

    top = possibilities[0]
    scenario = top.get("scenario", "")
    probability = top.get("probability", "Medium")
    timeframe = top.get("timeframe", "12-24 months")

    advisory = card.get("advisory", [])
    advisory_text = advisory[0] if advisory else "Monitor this space closely."

    themes = card.get("themes", [])
    hashtags = " ".join(f"#{t.replace(' ', '')}" for t in themes[:3])

    source_line = f"Source: {source_title} — {source_url}" if source_url else f"Source: {source_title}"

    return f"""What if {scenario.lower().rstrip('.')}?

Probability: {probability} | Timeframe: {timeframe}

{advisory_text}

{source_line}

#PossibilitiesWithProbabilities {hashtags}
"""


def x_post(card: dict, source_title: str, source_url: str = "") -> str:
    """Generate an X/Twitter post from an intel card. Zero tokens.

    Appends the source URL so readers can verify the claim (280-char budget
    means we favor the URL over the title when forced to choose).
    """
    signals = card.get("signals", [])
    possibilities = card.get("possibilities", [])
    if not signals or not possibilities:
        return ""

    top_signal = signals[0]
    top_possibility = possibilities[0]
    probability = top_possibility.get("probability", "Medium")

    source_line = source_url if source_url else source_title

    return f"""Signal: {top_signal}

Possibility: {top_possibility.get('scenario', '')}
Probability: {probability}

{source_line}

#PossibilitiesWithProbabilities"""


def weekly_digest_markdown(cards: list[dict], week_label: str) -> str:
    """Generate a weekly digest from multiple intel cards. Zero tokens.

    Includes a `## Sources` section at the bottom listing every item with a
    working URL — required by the knowledge system citation standard.
    """
    lines = [f"# Futures Intelligence Digest — {week_label}\n"]

    # Group by theme
    theme_cards: dict[str, list[dict]] = {}
    for card in cards:
        for theme in card.get("themes", ["Uncategorized"]):
            theme_cards.setdefault(theme, []).append(card)

    for theme, themed in sorted(theme_cards.items()):
        lines.append(f"\n## {theme}\n")
        for card in themed:
            title = card.get("title", "Untitled")
            url = card.get("url", "")
            for p in card.get("possibilities", []):
                prob = p.get("probability", "?")
                tf = p.get("timeframe", "?")
                scenario = p.get("scenario", "")
                if url:
                    lines.append(
                        f"- **{scenario}** [{prob}, {tf}] — [{title}]({url})"
                    )
                else:
                    lines.append(f"- **{scenario}** [{prob}, {tf}] — {title}")

    # Advisory summary
    lines.append("\n## Action Items\n")
    for card in cards:
        for a in card.get("advisory", []):
            lines.append(f"- {a}")

    # Sources — one line per distinct item URL
    lines.append("\n## Sources\n")
    seen_urls: set[str] = set()
    for card in cards:
        url = card.get("url", "")
        title = card.get("title", "Untitled")
        if url and url not in seen_urls:
            lines.append(f"- [{title}]({url})")
            seen_urls.add(url)
        elif not url:
            lines.append(f"- {title} *(source URL missing)*")

    return "\n".join(lines)
