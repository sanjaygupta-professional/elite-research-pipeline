# pipeline/cli.py
"""CLI commands for the Futures Intelligence System."""

from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .db import PipelineDB
from .templates import linkedin_post, x_post, weekly_digest_markdown


def cmd_intel(args):
    """Show recent intel cards."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        cards = db.get_intel_cards(limit=args.limit, theme=args.theme)
        for card in cards:
            print(f"\n{'='*60}")
            print(f"Title: {card['title']}")
            print(f"URL:   {card['url']}")
            print(f"Themes: {', '.join(card['themes'])}")
            print(f"\nSignals:")
            for s in card["signals"]:
                print(f"  - {s}")
            print(f"\nPossibilities:")
            for p in card["possibilities"]:
                if isinstance(p, dict):
                    print(f"  - {p.get('scenario', p)} [{p.get('probability', '?')}, {p.get('timeframe', '?')}]")
                else:
                    print(f"  - {p}")
            print(f"\nAdvisory:")
            for a in card["advisory"]:
                print(f"  - {a}")
    finally:
        db.close()


def cmd_draft(args):
    """Generate a draft post from an intel card."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        cards = db.get_intel_cards(limit=1)
        if not cards:
            print("No intel cards found.")
            return
        card = cards[0]
        if args.format == "linkedin":
            print(linkedin_post(card, card["title"], card["url"]))
        elif args.format == "x":
            print(x_post(card, card["title"]))
    finally:
        db.close()


def cmd_digest(args):
    """Generate a weekly digest."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        cards = db.get_intel_cards(limit=50)
        print(weekly_digest_markdown(cards, args.week or "This Week"))
    finally:
        db.close()


def cmd_themes(args):
    """Show trending themes."""
    config = load_config(args.config, args.env)
    db = PipelineDB(config.db_path)
    db.connect()
    try:
        themes = db.get_recent_themes(days=args.days)
        for theme, count in themes.items():
            print(f"  {count:3d}x  {theme}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Futures Intelligence System")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--env", default=".env")
    sub = parser.add_subparsers(dest="command")

    # intel
    p = sub.add_parser("intel", help="Show recent intel cards")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--theme", help="Filter by theme")

    # draft
    p = sub.add_parser("draft", help="Generate a draft post")
    p.add_argument("format", choices=["linkedin", "x"])

    # digest
    p = sub.add_parser("digest", help="Generate weekly digest")
    p.add_argument("--week", help="Week label")

    # themes
    p = sub.add_parser("themes", help="Show trending themes")
    p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"intel": cmd_intel, "draft": cmd_draft, "digest": cmd_digest, "themes": cmd_themes}[args.command](args)


if __name__ == "__main__":
    main()
