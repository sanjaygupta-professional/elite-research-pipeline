"""Curated prompt templates for NotebookLM artifact generation.

Slide prompts inspired by:
  - https://github.com/serenakeyitan/awesome-notebookLM-prompts
  - Google's official slide deck best practices
  - Sabrina Ramonov's viral PowerPoint techniques

Audio prompts based on notebooklm-py community best practices.
"""

from __future__ import annotations


# ─── Slide Deck Prompts ───────────────────────────────────────────────

SLIDE_PROMPTS: dict[str, str] = {
    "executive": (
        "Create a polished executive-level presentation. "
        "Use a clean, professional design with a dark navy and white color scheme. "
        "Start with a compelling title slide, then an executive summary. "
        "Each slide should have a clear headline that states the key insight, "
        "not just a topic label. Use 3-4 bullet points maximum per slide. "
        "Convert any statistics into simple data visualizations — circle percentages, "
        "icon-based comparisons, or progress bars. End with clear takeaways and next steps. "
        "The deck should be standalone — anyone reading it without a presenter should "
        "understand the full narrative."
    ),
    "minimal": (
        "Design a minimalist presentation with maximum clarity. "
        "Use generous white space, large typography, and a single accent color. "
        "One idea per slide. Headlines should be complete sentences that deliver "
        "the key message. Use full-bleed visuals where appropriate. "
        "No bullet points — use short paragraphs or single statements. "
        "Think TED talk slides: simple, bold, memorable."
    ),
    "technical": (
        "Create a detailed technical presentation. "
        "Use a clean, structured layout suitable for engineering or research audiences. "
        "Include architecture diagrams described in text, code snippets where relevant, "
        "and detailed comparison tables. Use a logical flow: problem → approach → "
        "implementation → results → conclusions. Each slide should have a descriptive "
        "headline and supporting details. Use monospace font references for technical terms."
    ),
    "storytelling": (
        "Create a narrative-driven presentation that tells a compelling story. "
        "Open with a hook — a surprising fact, question, or bold claim. "
        "Structure the deck as: situation → complication → resolution. "
        "Use contrast slides (before/after, old way/new way) to create tension. "
        "Include quote slides for key insights. Build to a powerful conclusion. "
        "Each slide should advance the narrative — no filler slides. "
        "Use warm, engaging colors and conversational language."
    ),
    "visual": (
        "Design a highly visual, magazine-quality presentation. "
        "Prioritize visual storytelling over text. Each slide should feature "
        "a dominant visual element — infographic, chart, diagram, or icon composition. "
        "Use a bold, modern color palette with high contrast. "
        "Text should be minimal — headlines and short captions only. "
        "Think editorial design: every slide should look like a magazine spread. "
        "Use data visualization for all statistics — never just list numbers."
    ),
    "educational": (
        "Create an educational presentation optimized for learning. "
        "Start with learning objectives. Use progressive disclosure — "
        "introduce concepts step by step, building on each other. "
        "Include 'key concept' highlight slides for important ideas. "
        "Use diagrams and flowcharts to explain processes. "
        "Add summary/recap slides at section transitions. "
        "End with key takeaways and suggested further reading. "
        "Use a clear, readable design with good information hierarchy."
    ),
    "japanese_minimal": (
        "Create a presentation inspired by Japanese minimalist design (wabi-sabi). "
        "Use extreme negative space (ma), a muted earthy palette — charcoal, warm white, "
        "a single accent in deep indigo or terracotta. Typography should be clean and large, "
        "with generous breathing room. One core idea per slide, no clutter. "
        "Structure as an actionable playbook for AI Architects and CTOs: "
        "start with the strategic context (why this matters now), then deliver 3-5 concrete "
        "decision frameworks or action items per section. Each slide headline should be "
        "a decisive statement — not a topic, but a recommendation. "
        "Include 'Decision Point' slides that frame build-vs-buy, adopt-vs-wait, "
        "or risk-vs-reward trade-offs. End with a prioritized action checklist: "
        "what to do this week, this quarter, this year. "
        "The deck should feel like a senior advisor's brief — calm authority, "
        "zero fluff, every slide earns its place."
    ),
    "default": (
        "Create a well-structured, professional slide deck. "
        "Use clear headlines that state key insights. "
        "Include an overview slide, logically organized content sections, "
        "and a summary with key takeaways. Keep text concise — "
        "prefer visuals and bullet points over paragraphs."
    ),
}


# ─── Audio Overview Prompts ───────────────────────────────────────────

AUDIO_PROMPTS: dict[str, str] = {
    "deep_dive": (
        "Create an in-depth discussion that thoroughly explores the key ideas. "
        "Explain concepts clearly with real-world analogies. "
        "Highlight what makes this content unique or surprising. "
        "Discuss practical implications and applications."
    ),
    "brief": (
        "Create a concise summary hitting only the most important points. "
        "Focus on key takeaways and actionable insights. "
        "Keep it tight — prioritize the 3-5 most valuable ideas."
    ),
    "critical": (
        "Take a critical analysis approach. Examine the strengths and weaknesses "
        "of the arguments presented. Identify assumptions, potential biases, "
        "and areas that need more evidence. Compare with alternative viewpoints."
    ),
    "default": (
        "Create an engaging overview of the key ideas and insights. "
        "Make it accessible and interesting, highlighting what matters most."
    ),
}


# ─── Style Auto-Selection ────────────────────────────────────────────

# Keywords that signal a particular slide style.
# Matched against video title + description (case-insensitive).
# Order matters: first match wins, so put more specific patterns first.
STYLE_KEYWORDS: dict[str, list[str]] = {
    "technical": [
        "architecture", "system design", "infrastructure", "api",
        "engineering", "code", "coding", "programming", "developer",
        "devops", "kubernetes", "docker", "database", "backend",
        "frontend", "framework", "library", "open source", "github",
        "benchmark", "performance", "latency", "scalab", "microservice",
        "deploy", "pipeline", "MLOps", "LLMOps", "fine-tun", "training",
        "inference", "model architecture", "transformer", "embedding",
    ],
    "educational": [
        "tutorial", "how to", "learn", "guide", "explained",
        "introduction", "beginner", "course", "lesson", "teach",
        "understand", "basics", "fundamentals", "step by step",
        "walkthrough", "crash course", "deep dive", "masterclass",
    ],
    "executive": [
        "business", "strategy", "revenue", "growth", "market",
        "investment", "funding", "startup", "enterprise", "roi",
        "board", "stakeholder", "quarterly", "forecast", "valuation",
        "acquisition", "partnership", "go-to-market", "competitive",
    ],
    "storytelling": [
        "story", "journey", "how i", "why i", "my experience",
        "lessons learned", "behind the scenes", "interview",
        "conversation", "podcast", "talk", "keynote", "fireside",
        "panel", "debate", "opinion", "prediction", "future of",
        "what happened", "rise and fall", "history of",
    ],
    "visual": [
        "design", "ui", "ux", "creative", "brand", "marketing",
        "infographic", "visualization", "dashboard", "demo",
        "showcase", "product launch", "announcement",
    ],
    "minimal": [
        "philosophy", "thinking", "mental model", "principle",
        "mindset", "wisdom", "reflection", "minimalis",
        "essential", "simplicity",
    ],
}

# Styles to exclude from auto-selection (they're special-purpose)
_EXCLUDED_FROM_AUTO = {"japanese_minimal", "default"}


def select_contextual_style(title: str, description: str = "") -> str:
    """Pick the most appropriate slide style based on content signals.

    Scans title and description for keyword matches.
    Returns a style name different from japanese_minimal (the default playbook).
    Falls back to 'storytelling' — the most universally engaging format.
    """
    text = f"{title} {description}".lower()

    for style, keywords in STYLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return style

    return "storytelling"


def get_slide_prompt(style: str) -> str:
    """Get the slide generation prompt for a given style.

    Falls back to 'default' if the style is not found.
    """
    return SLIDE_PROMPTS.get(style, SLIDE_PROMPTS["default"])


def get_audio_prompt(style: str) -> str:
    """Get the audio generation prompt for a given style.

    Falls back to 'default' if the style is not found.
    """
    return AUDIO_PROMPTS.get(style, AUDIO_PROMPTS["default"])


def list_slide_styles() -> list[str]:
    """Return all available slide style names."""
    return list(SLIDE_PROMPTS.keys())


def list_audio_styles() -> list[str]:
    """Return all available audio style names."""
    return list(AUDIO_PROMPTS.keys())
