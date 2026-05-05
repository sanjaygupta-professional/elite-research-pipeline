#!/bin/bash
# Generate ElevenLabs cloned-voice audio briefs.
# Subcommands:
#   gen-audio.sh dispatch [<YYYY-MM-DD>]
#       TTS the dispatch audio script to digest/public/audio/<date>.mp3.
#       Default date = today (UTC). Script must already exist at
#       digest/audio-scripts/<date>.md (the cron writes it; or hand-edit).
#
#   gen-audio.sh category <NN|all>
#       Generate (or regenerate) category audio brief for category 01-11.
#       Pass "all" to process every category in scope (excludes 06).
#       Auto-generates the script via Claude headless if missing.
#       Output: knowledge-system/audio/categories/<NN>.mp3
#
# Loads ELEVENLABS_* keys from .env at repo root. F-2 graceful: on
# ElevenLabs failure, exits non-zero with a clear message — caller
# (cron or human) decides whether to retry. Per-script char limit
# enforced at 3000 to catch runaway prompt outputs.

set -euo pipefail

# ── Setup ────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env (gitignored). Tolerate missing for failure messages.
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${ELEVENLABS_API_KEY:?ELEVENLABS_API_KEY not set in .env}"
: "${ELEVENLABS_VOICE_ID:?ELEVENLABS_VOICE_ID not set in .env}"
ELEVENLABS_MODEL_ID="${ELEVENLABS_MODEL_ID:-eleven_v3}"
ELEVENLABS_STABILITY="${ELEVENLABS_STABILITY:-0.6}"
ELEVENLABS_SIMILARITY="${ELEVENLABS_SIMILARITY:-0.85}"

MAX_SCRIPT_CHARS=3000

# Categories in scope for "category all" (excludes 06 weak-signal-watch
# which auto-updates weekly — audio would go stale).
CATEGORIES_IN_SCOPE=(01 02 03 04 05 07 08 09 10 11)

# Map category number → source file path (for script generation).
category_source_path() {
  local nn="$1"
  case "$nn" in
    01) echo "knowledge-system/baseline/zone1-present-intelligence/01-genai-capabilities.md" ;;
    02) echo "knowledge-system/baseline/zone1-present-intelligence/02-enterprise-ai-org-transformation.md" ;;
    03) echo "knowledge-system/baseline/zone1-present-intelligence/03-workforce-human-ai-collaboration.md" ;;
    04) echo "knowledge-system/baseline/zone1-present-intelligence/04-ai-governance-ethics.md" ;;
    05) echo "knowledge-system/baseline/zone2-futures-intelligence/05-ai-infrastructure-trajectory.md" ;;
    07) echo "knowledge-system/baseline/zone2-futures-intelligence/07-long-arc-futures-pov.md" ;;
    08) echo "knowledge-system/baseline/zone3-practitioner-toolkit/08-ai-productivity-tools.md" ;;
    09) echo "knowledge-system/baseline/zone3-practitioner-toolkit/09-transformation-methods-ai-era.md" ;;
    10) echo "knowledge-system/baseline/zone4-experimenters-lab/10-local-ai-engineering.md" ;;
    11) echo "knowledge-system/baseline/zone4-experimenters-lab/11-agent-frameworks-dev-tools.md" ;;
    *) return 1 ;;
  esac
}

# ── Core: TTS via ElevenLabs ─────────────────────────────────────────
# Args: <script-file> <output-mp3>
# Returns 0 on success. Exits non-zero with message on any failure.
tts_call() {
  local script_file="$1"
  local output_mp3="$2"

  if [[ ! -f "$script_file" ]]; then
    echo "ERROR: script file not found: $script_file" >&2
    return 1
  fi

  local script_chars
  script_chars=$(wc -c < "$script_file" | tr -d ' ')
  if (( script_chars > MAX_SCRIPT_CHARS )); then
    echo "ERROR: script $script_file is $script_chars chars (limit $MAX_SCRIPT_CHARS). Aborting TTS." >&2
    return 1
  fi
  if (( script_chars < 80 )); then
    echo "ERROR: script $script_file is suspiciously short ($script_chars chars). Aborting." >&2
    return 1
  fi

  # Build JSON payload safely. python3 escapes the script content,
  # avoiding shell-quoting hazards with quotes/newlines/etc in the prose.
  local payload
  payload=$(SCRIPT_FILE="$script_file" \
    MODEL="$ELEVENLABS_MODEL_ID" \
    STAB="$ELEVENLABS_STABILITY" \
    SIM="$ELEVENLABS_SIMILARITY" \
    python3 -c '
import json, os, sys
with open(os.environ["SCRIPT_FILE"], "r", encoding="utf-8") as f:
    text = f.read()
sys.stdout.write(json.dumps({
    "text": text,
    "model_id": os.environ["MODEL"],
    "voice_settings": {
        "stability": float(os.environ["STAB"]),
        "similarity_boost": float(os.environ["SIM"]),
    },
}))
')

  mkdir -p "$(dirname "$output_mp3")"

  local http_code
  http_code=$(curl -s -X POST \
    "https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}" \
    -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    -o "$output_mp3" \
    -w "%{http_code}")

  if [[ "$http_code" != "200" ]]; then
    # On error, output_mp3 contains JSON error body — preserve to stderr, remove file.
    echo "ERROR: ElevenLabs returned HTTP $http_code. Body:" >&2
    cat "$output_mp3" >&2 || true
    echo "" >&2
    rm -f "$output_mp3"
    return 1
  fi

  # Sanity check: did we get an actual MP3?
  if ! file "$output_mp3" | grep -qi "mpeg\|audio"; then
    echo "ERROR: response is not a valid MP3 file. See $output_mp3 for body." >&2
    return 1
  fi

  echo "✓ wrote $output_mp3 ($(wc -c < "$output_mp3" | tr -d ' ') bytes, from $script_chars script chars)"
}

# ── Dispatch subcommand ──────────────────────────────────────────────
cmd_dispatch() {
  local date="${1:-$(date -u +%F)}"
  local script_file="digest/audio-scripts/${date}.md"
  local output_mp3="digest/public/audio/${date}.mp3"

  echo "─── dispatch audio: $date ───"
  echo "script: $script_file"
  echo "output: $output_mp3"

  tts_call "$script_file" "$output_mp3"
}

# ── Category script generation (Claude headless) ─────────────────────
# Args: <category-number>
# Writes: knowledge-system/audio/categories/<NN>.script.md
generate_category_script() {
  local nn="$1"
  local source_path
  source_path=$(category_source_path "$nn") || {
    echo "ERROR: unknown category $nn" >&2
    return 1
  }

  if [[ ! -f "$source_path" ]]; then
    echo "ERROR: source file missing: $source_path" >&2
    return 1
  fi

  local script_file="knowledge-system/audio/categories/${nn}.script.md"
  mkdir -p "$(dirname "$script_file")"

  echo "→ generating script for category $nn from $source_path"

  # Headless Claude with subscription auth. Tightly scoped prompt;
  # output goes to stdout, captured to file.
  claude \
    --print \
    --permission-mode bypassPermissions \
    --allowedTools "Read" \
    --model opus \
    --max-budget-usd 1.00 \
    --output-format text \
    > "$script_file" <<EOF
Read the file at $source_path. Then write a 90-second audio brief script
suitable for text-to-speech with a cloned voice (mine). Hard constraints:

- 220 to 280 words total. Aim for 250.
- Open with: "Sanjay here." then a one-line hook from the category's
  central finding. Personal tone, like a voice memo to a peer.
- Middle: one sentence framing the category's domain, then 3-4 of the
  strongest signals/findings named with one sentence each.
- Close with: a one-line reader-action ("If your work is X: Y."), then
  "Full detail in the dispatch. Until next time."
- NO em-dashes (—) anywhere. Use commas, semicolons, parens.
- Spell out numbers in narrative prose ("eighty-five percent", "forty
  thousand to three hundred and twenty thousand dollars"). Preserve
  digits only inside benchmark or dollar figures cited verbatim from
  the source.
- Sentence average length: 15 words. Avoid long clauses.
- No URLs spoken aloud.
- No parentheticals (TTS pacing on parens is poor).

Output ONLY the script text. No frontmatter, no markdown, no commentary.
Plain prose paragraphs separated by blank lines.
EOF

  local chars
  chars=$(wc -c < "$script_file" | tr -d ' ')
  echo "✓ script: $script_file ($chars chars)"
}

# ── Category subcommand ──────────────────────────────────────────────
cmd_category() {
  local target="${1:?usage: gen-audio.sh category <NN|all>}"

  local categories=()
  if [[ "$target" == "all" ]]; then
    categories=("${CATEGORIES_IN_SCOPE[@]}")
  else
    # Normalize: 4 → 04
    target=$(printf "%02d" "${target##0}" 2>/dev/null || echo "$target")
    categories=("$target")
  fi

  local nn
  for nn in "${categories[@]}"; do
    echo "─── category audio: $nn ───"
    local script_file="knowledge-system/audio/categories/${nn}.script.md"
    local output_mp3="knowledge-system/audio/categories/${nn}.mp3"

    if [[ ! -f "$script_file" ]]; then
      generate_category_script "$nn" || {
        echo "✗ script generation failed for $nn — skipping" >&2
        continue
      }
    else
      echo "  using existing script: $script_file"
    fi

    tts_call "$script_file" "$output_mp3" || {
      echo "✗ TTS failed for category $nn — continuing" >&2
      continue
    }
  done
}

# ── Dispatch on subcommand ───────────────────────────────────────────
usage() {
  cat <<EOF >&2
usage:
  gen-audio.sh dispatch [<YYYY-MM-DD>]
  gen-audio.sh category <NN|all>

NN must be one of: ${CATEGORIES_IN_SCOPE[*]} (06 excluded — auto-updates weekly).
EOF
  exit 1
}

main() {
  local sub="${1:-}"
  shift || true

  case "$sub" in
    dispatch) cmd_dispatch "$@" ;;
    category) cmd_category "$@" ;;
    -h|--help|"") usage ;;
    *) echo "ERROR: unknown subcommand: $sub" >&2; usage ;;
  esac
}

main "$@"
