# SpecForge - Master Implementation Plan

## Phase 1: Foundation (MVP)
1. **Project Setup**: Initialize Python project with Poetry.
2. **CLI Skeleton**: Implement basic `typer` command structure.
3. **LLM Client**: Integrate `anthropic` SDK with environment variable handling.
4. **Interactive Loop**: Create the main REPL (Read-Eval-Print Loop) for chatting.

## Phase 2: Core Logic
1. **System Prompting**: Implement the "Architect" persona prompt.
2. **State Management**: Implement saving/loading chat history to `.specforge/session.json`.
3. **Rich UI**: Apply `rich` library for Markdown rendering and loading spinners.

## Phase 3: Export
1. **File Generation**: Implement the logic to parse LLM output and create the physical `design_docs` folder for the user's project.
