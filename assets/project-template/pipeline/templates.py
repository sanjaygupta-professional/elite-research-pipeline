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

    return f"""What if {scenario.lower().rstrip('.')}?

Probability: {probability} | Timeframe: {timeframe}

{advisory_text}

Source: {source_title}

#PossibilitiesWithProbabilities {hashtags}
"""


def x_post(card: dict, source_title: str) -> str:
    """Generate an X/Twitter post from an intel card. Zero tokens."""
    signals = card.get("signals", [])
    possibilities = card.get("possibilities", [])
    if not signals or not possibilities:
        return ""

    top_signal = signals[0]
    top_possibility = possibilities[0]
    probability = top_possibility.get("probability", "Medium")

    return f"""Signal: {top_signal}

Possibility: {top_possibility.get('scenario', '')}
Probability: {probability}

#PossibilitiesWithProbabilities"""


def weekly_digest_markdown(cards: list[dict], week_label: str) -> str:
    """Generate a weekly digest from multiple intel cards. Zero tokens."""
    lines = [f"# Futures Intelligence Digest — {week_label}\n"]

    # Group by theme
    theme_cards: dict[str, list[dict]] = {}
    for card in cards:
        for theme in card.get("themes", ["Uncategorized"]):
            theme_cards.setdefault(theme, []).append(card)

    for theme, themed in sorted(theme_cards.items()):
        lines.append(f"\n## {theme}\n")
        for card in themed:
            for p in card.get("possibilities", []):
                prob = p.get("probability", "?")
                tf = p.get("timeframe", "?")
                lines.append(f"- **{p.get('scenario', '')}** [{prob}, {tf}]")

    # Advisory summary
    lines.append("\n## Action Items\n")
    for card in cards:
        for a in card.get("advisory", []):
            lines.append(f"- {a}")

    return "\n".join(lines)
