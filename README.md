# EveryonePM

**Turn a raw product idea into a full PRD + Tech Spec in minutes — right in your terminal.**

EveryonePM is an AI-powered CLI that guides you through a structured **Double Diamond** product design workflow, producing professional-grade artifacts ready for engineering handoff.

```
eopm "I want to build a habit tracking app for remote teams"
```

---

## Why EveryonePM?

Most AI writing tools give you a wall of text and call it a spec. EveryonePM is different:

- **Structured workflow, not a chat box** — Four guided stages (Discovery → Definition → Ideation → Delivery) ensure nothing gets skipped
- **Interactive, not passive** — Keyboard-driven choice menus at each decision point keep you in control
- **Provider-agnostic** — Works with Anthropic, OpenAI-compatible gateways, and Azure OpenAI out of the box
- **Persistent sessions** — Resume where you left off across terminal sessions
- **Export-ready artifacts** — Outputs polished `PRD.md` and `TECH_SPEC.md` files

---

## Workflow: Double Diamond

```
📋 Discovery  →  🎯 Definition  →  💡 Ideation  →  🚀 Delivery
```

| Stage | What happens |
|---|---|
| **Discovery** | Competitor analysis, user personas, pain point mapping |
| **Definition** | Product vision, user journey, MVP feature prioritization |
| **Ideation** | Technical options, architecture recommendation, risk assessment |
| **Delivery** | Data models, API contracts, implementation plan |

At each stage, EveryonePM presents structured choices you navigate with arrow keys. Confirming a stage automatically advances the workflow — no manual `/next` required.

---

## Quick Start

### 1. Install

```bash
# Recommended: uv tool (works from any directory)
uv tool install -e .

# Or: pipx
pipx install -e .

# Or: pip editable
pip install -e .
```

### 2. Configure

Create a global config (works in every directory — no per-project setup needed):

```bash
mkdir -p ~/.eopm
cp .env.example ~/.eopm/.env
# Edit ~/.eopm/.env with your API credentials
```

Or use a local `.env` in your project directory. **Priority:** real env vars → local `.env` → `~/.eopm/.env`

### 3. Run

```bash
# Start with a prompt
eopm "Build a SaaS analytics dashboard for e-commerce"

# Or launch the interactive welcome screen
eopm

# Start fresh (discard previous session)
eopm --fresh
```

---

## Configuration

EveryonePM uses [LiteLLM](https://github.com/BerriAI/litellm) for provider abstraction. Set one of these in your `.env` or `~/.eopm/.env`:

### Anthropic (Claude)

```env
ANTHROPIC_API_KEY=your_key_here
EOPM_MODEL=anthropic/claude-3-5-sonnet-latest
```

### OpenAI / OpenAI-compatible gateway

```env
OPENAI_API_KEY=your_key_here
OPENAI_API_BASE=https://your-gateway-host/path  # omit for official OpenAI
EOPM_MODEL=openai/gpt-4o
```

### Azure OpenAI

```env
AZURE_API_KEY=your_key_here
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=your-deployment
EOPM_MODEL=azure/gpt-4o
```

### Optional settings

```env
# Increase for reasoning models (o1, gpt-5, etc.)
EOPM_MAX_TOKENS=40000

# Custom headers for gateway auth/tracing
EOPM_DEFAULT_HEADERS={"X-Custom-Header":"value"}
```

---

## REPL Commands

Once inside a session, these commands are available at the `>` prompt:

| Command | Description |
|---|---|
| `/fresh` | Reset session and start over |
| `/status` | Show current stage and workflow progress |
| `/next` | Manually advance to next stage |
| `/goto <stage>` | Jump to a specific stage (debug) |
| `/export <dir>` | Export `PRD.md` + `TECH_SPEC.md` to a directory |
| `/write <kind> <path>` | Write a single artifact (`prd` or `techspec`) to a file |
| `/read <path>` | Load a file and ask AI to analyze it |
| `confirm` | Confirm the current stage's artifacts |
| `exit` / `quit` / `/exit` | Leave the session |

---

## Features

- **Keyboard-driven choices** — Interactive menus using arrow keys (powered by [questionary](https://github.com/tmbo/questionary))
- **Auto stage advancement** — Selecting "Yes, proceed" in a confirmation choice automatically advances the workflow and updates stage state
- **URL & PDF context** — Paste URLs in your prompt; EveryonePM fetches and summarizes the content as context
- **Session persistence** — Conversations saved to `.eopm/session.json`; resume any time
- **Global config** — `~/.eopm/.env` applies to all projects, no per-directory setup
- **Reasoning model support** — Works with o1, gpt-5, and other reasoning models (auto-adjusts token limits)
- **Rich terminal UI** — Stage progress indicators, spinners, and formatted Markdown output

---

## Requirements

- Python **≥ 3.13**
- One of: Anthropic API key, OpenAI-compatible endpoint, or Azure OpenAI credentials

---

## Project Structure

```
eopm/
├── config.py          # Version, env loading, global config (~/.eopm/.env)
├── main.py            # CLI entry point, REPL loop, command handling
├── core/
│   ├── stage_manager.py  # Double Diamond state machine
│   ├── session.py        # Session persistence (load/save)
│   ├── web.py            # URL fetching and content extraction
│   └── pdf.py            # PDF text extraction
├── llm/
│   ├── client.py      # LiteLLM wrapper (chat, generate_artifact, summarize)
│   └── prompts.py     # Stage-specific system prompts
└── ui/
    ├── console.py     # Rich terminal UI (welcome screen, progress, stage headers)
    └── interactive.py # @CHOICE block parser and questionary presenter
```

---

## Development

```bash
# Install dependencies
uv sync

# Install in editable mode
uv pip install -e .

# Run directly
uv run eopm "Draft a PRD for a habit tracker"
```

---

## License

MIT
