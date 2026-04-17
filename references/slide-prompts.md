# Slide Prompt Templates — Reference

## Sources

### Primary: awesome-notebookLM-prompts
- **Repo:** https://github.com/serenakeyitan/awesome-notebookLM-prompts
- 21+ presentation design templates across 6 categories
- Complex YAML specs (200-400 lines) and concise text prompts (50-100 words)
- Field-tested by researchers, founders, and designers

### Google's Official Best Practices
- Be detailed and specific in prompts
- Specify presentation title, slide contents, design scheme, visual style
- Use "View custom prompt" (3-dot menu) to see what worked
- Choose Detailed Deck (standalone) vs Presenter Slides (visual, talking points)

### Sabrina Ramonov — Viral PowerPoints
- Source: https://www.sabrina.dev/p/viral-powerpoints-slides-free-notebooklm
- Convert statistics into clean data visualizations
- Use proven viral layouts: hero, contrast, icon grids, process flows
- Key insight: "Viral decks are not visually loud — they are intellectually loud"

---

## Built-in Styles (pipeline/prompts.py)

| Style | Best For |
|-------|----------|
| `executive` | Board presentations, stakeholder updates — professional, data-viz focused |
| `minimal` | Conference talks, TED-style — one idea per slide, bold typography |
| `technical` | Engineering reviews, research — architecture diagrams, code, tables |
| `storytelling` | Pitches, narratives — situation→complication→resolution arc |
| `visual` | Marketing, social — magazine-quality, infographic-style slides |
| `educational` | Training, workshops — progressive disclosure, learning objectives |
| `default` | General purpose — clean structure, balanced text and visuals |

## Audio Styles

| Style | Best For |
|-------|----------|
| `deep_dive` | Thorough exploration with analogies and practical implications |
| `brief` | Quick 3-5 key takeaways, action-oriented |
| `critical` | Analytical — strengths, weaknesses, assumptions, alternatives |
| `default` | Balanced, engaging overview |

---

## How to Customize

### Option 1: Change style in config.yaml
```yaml
styles:
  slides: "storytelling"   # Pick from built-in styles
  audio: "critical"
```

### Option 2: Add your own style in prompts.py
```python
SLIDE_PROMPTS["my_style"] = (
    "Create slides with [your specific instructions]..."
)
```

Then set `slides: "my_style"` in config.yaml.

### Option 3: Use prompts from awesome-notebookLM-prompts
Copy any prompt from the repo and add it as a new style in `prompts.py`.

---

## Tips for Great Slides

1. **Be specific** — "3 bullet points per slide" beats "keep it concise"
2. **Specify visual style** — color scheme, layout preferences, typography
3. **State the output format** — "headlines should state insights, not topics"
4. **Request data viz** — "convert statistics into circle percentages or icon grids"
5. **Define the audience** — "for technical leaders" vs "for non-technical stakeholders"
