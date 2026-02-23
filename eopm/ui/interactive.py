"""Interactive choice system for EveryonePM.

This module provides functionality for AI to present structured choices
to the user, similar to Claude Code's tool use confirmation system.
Uses questionary for keyboard-driven navigation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import questionary
from rich.console import Console
from rich.text import Text

console = Console()


class ChoiceType(str, Enum):
    """Types of choices that can be presented."""

    SINGLE = "single"  # Choose one option
    MULTIPLE = "multiple"  # Choose multiple options
    CONFIRM = "confirm"  # Yes/No confirmation
    INPUT = "input"  # Free text input


@dataclass
class Choice:
    """A single choice option."""

    key: str  # Short key like "1", "2", "a", "b"
    label: str  # Display text
    description: str = ""  # Optional longer description
    is_default: bool = False  # Whether this is the default choice


@dataclass
class ChoicePrompt:
    """A structured choice prompt from AI."""

    title: str  # Title like "Select your target users"
    prompt_type: ChoiceType
    choices: list[Choice]
    other_option: bool = False  # Whether to show "Other (type input)" option
    context: str = ""  # Additional context or question


def parse_ai_choices(text: str) -> list[ChoicePrompt]:
    """Parse AI response for structured choice prompts.

    Looks for patterns like:
    ```
    @CHOICE:select_one
    TITLE: Select your target users
    1. Professional traders
    2. Retail investors
    3. Quantitative analysts
    @END_CHOICE
    ```

    Returns:
        List of ChoicePrompt objects found in the text
    """
    prompts = []

    # Simple parsing - look for choice blocks
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Detect choice start
        if line.startswith("@CHOICE:"):
            choice_type_str = line.split(":", 1)[1].strip().lower()

            # Map string to ChoiceType
            if choice_type_str in ["single", "select_one", "one"]:
                prompt_type = ChoiceType.SINGLE
            elif choice_type_str in ["multiple", "select_multiple", "many"]:
                prompt_type = ChoiceType.MULTIPLE
            elif choice_type_str in ["confirm", "yes_no", "yesno"]:
                prompt_type = ChoiceType.CONFIRM
            else:
                prompt_type = ChoiceType.SINGLE

            i += 1
            title = ""
            choices = []
            other_option = False

            # Parse until @END_CHOICE
            while i < len(lines) and not lines[i].strip().startswith("@END_CHOICE"):
                line = lines[i].strip()

                if line.startswith("TITLE:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("OTHER:"):
                    other_option = line.split(":", 1)[1].strip().lower() == "true"
                elif line and line[0].isdigit() and ". " in line:
                    # Parse choice like "1. Option text"
                    parts = line.split(". ", 1)
                    key = parts[0]
                    label = parts[1] if len(parts) > 1 else ""
                    choices.append(Choice(key=key, label=label))
                elif line and line[0] in ["a", "b", "c", "d", "e"] and ". " in line:
                    # Parse lettered choices like "a. Option text"
                    parts = line.split(". ", 1)
                    key = parts[0]
                    label = parts[1] if len(parts) > 1 else ""
                    choices.append(Choice(key=key, label=label))

                i += 1

            if title and choices:
                prompts.append(
                    ChoicePrompt(
                        title=title,
                        prompt_type=prompt_type,
                        choices=choices,
                        other_option=other_option,
                    )
                )

        i += 1

    return prompts


def present_choices(prompt: ChoicePrompt) -> str:
    """Present choices to the user using questionary for keyboard navigation.

    Returns:
        The user's selection as a string
    """
    # Format choices for questionary
    choices_dict = {choice.key: choice for choice in prompt.choices}

    if prompt.prompt_type == ChoiceType.SINGLE:
        # Build choices list with descriptions
        qa_choices = []
        for choice in prompt.choices:
            display_text = choice.label
            if choice.description:
                display_text = f"{choice.label} - {choice.description}"
            qa_choices.append(questionary.Choice(display_text, value=choice.key))

        # Always add a free-text input option so users can supplement or override
        qa_choices.append(questionary.Choice("✏️  Type a message...", value="__other__"))

        # Use questionary select for keyboard navigation
        result = questionary.select(
            prompt.title,
            choices=qa_choices,
            qmark="➤",
            pointer="➤",
            instruction="Use arrow keys to navigate, Enter to select",
        ).ask()

        if result == "__other__":
            custom = questionary.text("Type your message:").ask()
            return f"User message: {custom.strip()}" if custom and custom.strip() else ""

        if result:
            choice = choices_dict.get(result)
            return f"{result}. {choice.label if choice else ''}" if choice else result

        return ""

    elif prompt.prompt_type == ChoiceType.MULTIPLE:
        # Build choices list
        qa_choices = []
        for choice in prompt.choices:
            display_text = choice.label
            if choice.description:
                display_text = f"{choice.label} - {choice.description}"
            qa_choices.append(questionary.Choice(display_text, value=choice.key, checked=False))

        # Use checkbox for multiple selection
        results = questionary.checkbox(
            prompt.title,
            choices=qa_choices,
            qmark="➤",
            pointer="➤",
            instruction="Use arrow keys, Space to select/deselect, Enter to confirm",
        ).ask()

        if results is None:
            return ""  # User cancelled with Ctrl+C

        if not results:
            # User pressed Enter without selecting any option — explicitly "none"
            selection_str = "(none selected)"
        else:
            selected_labels = []
            for key in results:
                choice = choices_dict.get(key)
                if choice:
                    selected_labels.append(f"{key}. {choice.label}")
            selection_str = ", ".join(selected_labels)

        # Always offer a free-text follow-up so users can add context
        extra = questionary.text(
            "Add a message (press Enter to skip):",
            default="",
        ).ask()
        if extra and extra.strip():
            return f"{selection_str}\nUser message: {extra.strip()}"
        return selection_str

    elif prompt.prompt_type == ChoiceType.CONFIRM:
        # Show ALL choices the model provided (not just first 2)
        qa_choices = []
        for choice in prompt.choices:
            qa_choices.append(questionary.Choice(choice.label, value=choice.key))

        result = questionary.select(
            prompt.title,
            choices=qa_choices,
            qmark="➤",
            pointer="➤",
        ).ask()

        return f"{result}. {choices_dict[result].label}" if result else ""

    return ""


def format_choices_for_ai(prompt: ChoicePrompt, user_selection: str) -> str:
    """Format a choice prompt and user selection as text for AI.

    This is used when user makes a selection.
    """
    lines = [
        f"**{prompt.title}**",
        "",
    ]

    if user_selection:
        lines.append(f"User selected: {user_selection}")

    return "\n".join(lines)


def enhance_ai_prompt_with_choices() -> str:
    """Return instructions for AI on how to format choices.

    This is added to the system prompt.
    """
    return """

When you need user input or confirmation, use structured choice format for better UX:

```markdown
@CHOICE:single
TITLE: What type of product is this?
1. Mobile app
2. Web application
3. Desktop software
4. API/Backend service
OTHER:true
@END_CHOICE
```

For multiple selections:
```markdown
@CHOICE:multiple
TITLE: Select all features that apply:
1. User authentication
2. Real-time updates
3. File uploads
4. Payment processing
@END_CHOICE
```

For yes/no confirmation:
```markdown
@CHOICE:confirm
TITLE: Proceed to the next stage?
1. Yes
2. No
@END_CHOICE
```

Guidelines:
- Use choices whenever asking users to select from options
- Keep choice labels concise (1-10 words)
- Use OTHER:true when user might want to provide custom input
- Order choices logically (most common first)
- Limit to 3-7 choices per prompt
- The user will navigate with arrow keys and select with Enter
"""
