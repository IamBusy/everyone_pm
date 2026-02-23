# Technology Stack

## Core
- **Language**: Python 3.10+
- **Package Manager**: Poetry

## Libraries
- **CLI Framework**: `typer[all]` (Standard for modern Python CLIs)
- **UI & Formatting**: `rich` (For markdown rendering, panels, spinners)
- **AI SDK**: `anthropic` (Direct access to Claude 3.5 Sonnet)
- **Environment**: `python-dotenv` (To load ANTHROPIC_API_KEY)
- **Data Serialization**: `pydantic` (For structured data validation if needed)

## File Storage
- **Session Storage**: JSON format, stored in `.specforge/session.json`
- **Output**: Standard Markdown files.
