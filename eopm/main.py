from __future__ import annotations

import sys

try:
    import readline
except ImportError:
    # Windows may need pyreadline3
    import pyreadline3 as readline  # type: ignore

import typer

from eopm.config import SESSION_PATH, VERSION, check_env_file
from eopm.core.session import load_messages, load_workflow_state, save_session
from eopm.core.stage_manager import StageManager, Stage, WorkflowState
from eopm.core.pdf import fetch_pdf_text
from eopm.core.web import extract_urls, fetch_url
from pathlib import Path

from eopm.llm.client import chat, generate_artifact, summarize
from eopm.ui.console import print_markdown, status, print_stage_header, print_error, ProgressSpinner, console
from eopm.llm.client import EopmLLMError
from eopm.ui.interactive import ChoicePrompt, ChoiceType, parse_ai_choices, present_choices, format_choices_for_ai

app = typer.Typer(add_completion=False, context_settings={"help_option_names": ["-h", "--help"]})


def main() -> None:
    app()


def _is_exit(text: str) -> bool:
    return text.strip().lower() in {"exit", "quit", "/exit"}


def _parse_export_dir(text: str) -> Path | None:
    stripped = text.strip()
    if not stripped.startswith("/export"):
        return None
    parts = stripped.split(maxsplit=1)
    if len(parts) != 2:
        return None
    return Path(parts[1]).expanduser()


@app.command()
def new(
    initial_prompt: str | None = typer.Argument(
        None, help="Initial prompt to start the consultation (optional)."
    ),
    fresh: bool = typer.Option(False, "--fresh"),
    file: str | None = typer.Option(None, "--file", "-f", help="Load existing PRD or Tech Spec file to continue work on"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit."),
) -> None:
    """Start (or resume) an interactive product design consultation.

    Use --file to load an existing PRD.md or TECH_SPEC.md to continue development.
    """

    if version:
        from eopm.ui.console import print_version

        print_version(VERSION)
        raise typer.Exit()

    # Load or initialize session state
    if fresh:
        messages: list[dict] = []
        workflow_state = None
        stage_manager = StageManager()
    else:
        messages = load_messages(SESSION_PATH)
        workflow_state = load_workflow_state(SESSION_PATH)
        stage_manager = StageManager(workflow_state)

    # Load existing file if specified
    if file:
        file_path = Path(file)
        if not file_path.exists():
            print_error(f"File not found: {file_path}")
            print_markdown("\n**Usage:** `--file <path>` to load an existing PRD.md or TECH_SPEC.md")
            raise typer.Exit(1)

        content = file_path.read_text(encoding="utf-8")
        messages.append({
            "role": "user",
            "content": f"I'm loading an existing document to continue working on it.\n\nFile: {file_path}\n\n--- Document Content ---\n\n{content}"
        })

        # Determine stage from filename
        if "prd" in file_path.name.lower():
            stage_manager.state.current_stage = Stage.DEFINITION
        elif "tech" in file_path.name.lower() or "spec" in file_path.name.lower():
            stage_manager.state.current_stage = Stage.DELIVERY

        print_markdown(f"✅ Loaded **{file_path.name}** ({len(content)} characters)")
        print_stage_header(stage_manager)

    # If no initial prompt was provided, show a welcome screen and wait for input.
    if initial_prompt is None:
        from eopm.ui.console import print_welcome

        print_welcome(SESSION_PATH, messages, stage_manager, VERSION)

        # Check environment configuration
        has_env, env_msg = check_env_file()
        if not has_env:
            from eopm.config import GLOBAL_ENV_PATH
            print(f"\n⚠️  {env_msg}")
            print("\nTo fix this, choose one of:")
            print(f"  A) Global config (works in every directory):")
            print(f"     mkdir -p {GLOBAL_ENV_PATH.parent}")
            print(f"     cp .env.example {GLOBAL_ENV_PATH}")
            print(f"     # Then edit {GLOBAL_ENV_PATH} with your credentials")
            print(f"")
            print(f"  B) Local config (this directory only):")
            print("     cp .env.example .env")
            print("     # Then edit .env with your credentials")
            print("\nExample config:")
            print("  EOPM_MODEL=anthropic/claude-3-5-sonnet-latest")
            print("  ANTHROPIC_API_KEY=your_key_here")
            print("  ")
            print("  # Or for Azure:")
            print("  EOPM_MODEL=azure/gpt-4o")
            print("  AZURE_API_KEY=your_key_here")
            print("  AZURE_API_BASE=https://your-resource.openai.azure.com")
            print("  AZURE_API_VERSION=2024-02-15-preview")
            print("  AZURE_DEPLOYMENT_NAME=your-deployment")

        # Show current stage if we're resuming
        if workflow_state and stage_manager.current_stage != Stage.DISCOVERY:
            print_stage_header(stage_manager)

        while True:
            try:
                user_text = input("\n> ")
            except EOFError:
                return
            except KeyboardInterrupt:
                print_markdown("\nUse 'exit' or 'quit' to leave the session.")
                continue

            if _is_exit(user_text):
                return
            export_dir = _parse_export_dir(user_text)
            if export_dir is not None:
                export_dir.mkdir(parents=True, exist_ok=True)

                with ProgressSpinner([
                    "🔗 Connecting to API for PRD generation...",
                    "📤 Preparing request...",
                    "🧠 AI is writing PRD (this may take 20-40s)...",
                    "📝 Finalizing PRD document...",
                ]) as progress:
                    progress.next_stage()
                    prd_md = generate_artifact(kind="prd", messages=messages, stage_manager=stage_manager)
                    progress.next_stage()

                print_markdown("**✓ PRD generated!**\n")
                console.print("  Now generating Tech Spec...\n")

                with ProgressSpinner([
                    "🔗 Connecting to API for Tech Spec...",
                    "📤 Preparing request...",
                    "🧠 AI is writing technical specifications...",
                    "📝 Finalizing Tech Spec document...",
                ]) as progress:
                    progress.next_stage()
                    tech_md = generate_artifact(kind="techspec", messages=messages, stage_manager=stage_manager)
                    progress.next_stage()

                (export_dir / "PRD.md").write_text(prd_md + "\n", encoding="utf-8")
                (export_dir / "TECH_SPEC.md").write_text(tech_md + "\n", encoding="utf-8")

                print_markdown("**✓ Tech Spec generated!**\n")

                print_markdown(
                    "**Exported artifacts:**\n"
                    f"- `{export_dir / 'PRD.md'}`\n"
                    f"- `{export_dir / 'TECH_SPEC.md'}`"
                )
                continue

            if user_text.strip() == "/export":
                print_markdown("Usage: `/export <dir>`")
                continue

            # Check for stage status command
            if user_text.strip() == "/status":
                print_stage_header(stage_manager)
                print_markdown(stage_manager.get_stage_context())
                continue

            if user_text.strip():
                initial_prompt = user_text
                break

    # If the prompt contains URLs, fetch and summarize them as additional context.
    urls = extract_urls(initial_prompt)
    if urls:
        for url in urls[:3]:
            try:
                console.print(f"\n📥 Fetching {url}...")
                with status(f"Downloading and analyzing {url}..."):
                    page = fetch_url(url)

                    text = page.text
                    if page.content_type and "pdf" in page.content_type.lower():
                        text = fetch_pdf_text(url)

                    summary = summarize(text)

                console.print(f"  ✓ Fetched and summarized ({len(summary)} chars)\n")

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Reference material fetched from URL:\n"
                            f"- URL: {url}\n\n"
                            "Summary:\n"
                            f"{summary}"
                        ),
                    }
                )
            except Exception as e:
                console.print(f"  ✗ Failed: {e}\n")

    # First turn - add stage context to the user's message
    user_content = initial_prompt
    stage_context = stage_manager.get_stage_context()
    if stage_context:
        user_content = f"{stage_context}\n\nUser input: {initial_prompt}"

    messages.append({"role": "user", "content": user_content})

    try:
        # Show progress to user
        with ProgressSpinner([
            f"🔗 Connecting to API (Stage: {stage_manager.current_stage.value})...",
            "📤 Sending your request...",
            f"🧠 AI is analyzing... (this may take 10-30s for reasoning models)",
            "📝 Processing response...",
        ]) as progress:
            progress.next_stage()  # Move to "Sending request"
            # Inject stage-specific system prompt
            assistant_text = chat(messages, stage_manager=stage_manager)
            progress.next_stage()  # Move to "Processing response"
    except Exception as e:
        _handle_llm_error(e, messages, stage_manager)
        return

    print_markdown(assistant_text)
    messages.append({"role": "assistant", "content": assistant_text})

    # Process @CHOICE blocks in the response; collect (prompt, selection) pairs.
    # Stage advancement happens inside _process_assistant_response when applicable.
    current_text = assistant_text
    had_choices = False   # True once we've processed at least one @CHOICE this round
    nudge_sent = False    # Limit auto-nudge to one attempt per response chain
    while True:
        choice_interactions = _process_assistant_response(current_text, stage_manager)
        if not choice_interactions:
            # If we already processed choices but AI forgot to include @CHOICE:confirm,
            # nudge it once to present the stage completion confirmation.
            if had_choices and stage_manager.needs_confirmation() and not nudge_sent:
                nudge_sent = True
                messages.append({
                    "role": "user",
                    "content": "(Please present the stage completion @CHOICE:confirm as required by the workflow.)",
                })
                with ProgressSpinner([
                    "🔗 Connecting to API...",
                    "📤 Requesting stage confirmation...",
                    "🧠 AI is preparing confirmation...",
                    "📝 Formatting response...",
                ]) as progress:
                    progress.next_stage()
                    followup = chat(messages, stage_manager=stage_manager)
                    progress.next_stage()
                console.print()
                print_markdown(followup)
                console.print()
                messages.append({"role": "assistant", "content": followup})
                current_text = followup
                continue
            break

        had_choices = True
        nudge_sent = False  # Reset on each successful choice round

        # If stage just advanced to COMPLETE, auto-export and stop
        if stage_manager.current_stage == Stage.COMPLETE:
            save_session(SESSION_PATH, messages, stage_manager.state)
            _auto_export(messages, stage_manager)
            return

        # Send all selections from this round to the AI and get one followup
        for prompt, user_selection in choice_interactions:
            messages.append({"role": "user", "content": format_choices_for_ai(prompt, user_selection)})

        with ProgressSpinner([
            "🔗 Connecting to API...",
            "📤 Sending selection...",
            "🧠 AI is processing your choice...",
            "📝 Formatting response...",
        ]) as progress:
            progress.next_stage()
            followup = chat(messages, stage_manager=stage_manager)
            progress.next_stage()

        console.print()
        print_markdown(followup)
        console.print()
        messages.append({"role": "assistant", "content": followup})

        # If the followup itself contains @CHOICE blocks, loop to present them too
        current_text = followup

    save_session(SESSION_PATH, messages, stage_manager.state)

    # REPL turns
    while True:
        try:
            user_text = input("\n> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            print_markdown("\nUse 'exit' or 'quit' to leave the session.")
            continue

        # Handle exit
        if _is_exit(user_text):
            break

        # Skip empty input
        if not user_text.strip():
            continue

        export_dir = _parse_export_dir(user_text)
        if export_dir is not None:
            export_dir.mkdir(parents=True, exist_ok=True)

            with ProgressSpinner([
                "🔗 Connecting to API for PRD generation...",
                "📤 Preparing request...",
                "🧠 AI is writing PRD (this may take 20-40s)...",
                "📝 Finalizing PRD document...",
            ]) as progress:
                progress.next_stage()
                prd_md = generate_artifact(kind="prd", messages=messages, stage_manager=stage_manager)
                progress.next_stage()

            print_markdown("**✓ PRD generated!**\n")
            console.print("  Now generating Tech Spec...\n")

            with ProgressSpinner([
                "🔗 Connecting to API for Tech Spec...",
                "📤 Preparing request...",
                "🧠 AI is writing technical specifications...",
                "📝 Finalizing Tech Spec document...",
            ]) as progress:
                progress.next_stage()
                tech_md = generate_artifact(kind="techspec", messages=messages, stage_manager=stage_manager)
                progress.next_stage()

            (export_dir / "PRD.md").write_text(prd_md + "\n", encoding="utf-8")
            (export_dir / "TECH_SPEC.md").write_text(tech_md + "\n", encoding="utf-8")

            print_markdown("**✓ Tech Spec generated!**\n")

            print_markdown(
                "**Exported artifacts:**\n"
                f"- `{export_dir / 'PRD.md'}`\n"
                f"- `{export_dir / 'TECH_SPEC.md'}`"
            )
            continue

        if user_text.strip() == "/export":
            print_markdown("Usage: `/export <dir>`")
            continue

        # Fresh start: clear session and reset workflow
        if user_text.strip() == "/fresh":
            confirm = input("Reset session and start over? (y/N) ").strip().lower()
            if confirm == "y":
                messages.clear()
                stage_manager.state = WorkflowState()
                if SESSION_PATH.exists():
                    SESSION_PATH.unlink()
                print_markdown("✅ Session cleared. Start typing your new prompt.")
            else:
                print_markdown("Cancelled.")
            continue

        # Check for stage status command
        if user_text.strip() == "/status":
            print_stage_header(stage_manager)
            context = stage_manager.get_stage_context()
            if context:
                print_markdown(context)
            continue

        # Check for stage advancement commands
        if user_text.strip() in {"/next", "/advance"}:
            if stage_manager.can_advance():
                new_stage = stage_manager.advance()
                print_stage_header(stage_manager)
                print_markdown(f"\n✅ Advanced to **{new_stage.upper()}** stage!\n")
                save_session(SESSION_PATH, messages, stage_manager.state)
            else:
                print_markdown("**Cannot advance yet.** Please complete the current stage requirements first:")
                if stage_manager.current_stage == Stage.DISCOVERY:
                    print_markdown("- Confirm user personas (reply 'confirm personas')")
                    print_markdown("- Confirm competitor analysis (reply 'confirm competitors')")
                elif stage_manager.current_stage == Stage.DEFINITION:
                    print_markdown("- Confirm MVP scope (reply 'confirm mvp')")
                elif stage_manager.current_stage == Stage.IDEATION:
                    print_markdown("- Confirm technical approach (reply 'confirm tech')")
            continue

        # Manual stage jump (for debugging/override)
        if user_text.strip().startswith("/goto "):
            target = user_text.strip().split(maxsplit=1)[1].lower()
            stage_map = {
                "discovery": Stage.DISCOVERY,
                "definition": Stage.DEFINITION,
                "ideation": Stage.IDEATION,
                "delivery": Stage.DELIVERY,
                "complete": Stage.COMPLETE,
            }
            if target in stage_map:
                stage_manager.state.current_stage = stage_map[target]
                print_stage_header(stage_manager)
                print_markdown(f"\n⚠️  Manually jumped to **{target.upper()}** stage\n")
                save_session(SESSION_PATH, messages, stage_manager.state)
            else:
                print_markdown(f"**Unknown stage.** Valid stages: {', '.join(stage_map.keys())}")
            continue

        # Read file command: /read <path>
        if user_text.strip().startswith("/read "):
            file_path_str = user_text.strip().split(maxsplit=1)[1]
            file_path = Path(file_path_str)

            if not file_path.exists():
                print_error(f"File not found: {file_path}")
                continue

            content = file_path.read_text(encoding="utf-8")
            messages.append({
                "role": "user",
                "content": f"Please read and analyze this file:\n\nFile: {file_path}\n\n--- Content ---\n\n{content}"
            })

            print_markdown(f"✅ Loaded **{file_path.name}** ({len(content)} characters) - Sending to AI for analysis...\n")

            # Get AI response
            with ProgressSpinner([
                "🔗 Connecting to API...",
                "📤 Sending file content...",
                "🧠 AI is analyzing the file...",
                "📝 Formatting response...",
            ]) as progress:
                progress.next_stage()
                assistant_text = chat(messages, stage_manager=stage_manager)
                progress.next_stage()

            console.print()
            print_markdown(assistant_text)
            messages.append({"role": "assistant", "content": assistant_text})

            save_session(SESSION_PATH, messages, stage_manager.state)
            continue

        # Write file command: /write <kind> <path>
        if user_text.strip().startswith("/write "):
            parts = user_text.strip().split(maxsplit=2)
            if len(parts) < 3:
                print_markdown("**Usage:** `/write <prd|techspec> <path>`")
                print_markdown("\nExamples:")
                print_markdown("  `/write prd ./my_project/PRD.md`")
                print_markdown("  `/write techspec ./my_project/TECH_SPEC.md`")
                continue

            kind = parts[1].lower()
            file_path = Path(parts[2])

            # Create parent directory
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate artifact
            with ProgressSpinner([
                f"🔗 Connecting to API for {kind} generation...",
                "📤 Preparing request...",
                f"🧠 AI is writing {kind.upper()}...",
                "📝 Finalizing document...",
            ]) as progress:
                progress.next_stage()
                content = generate_artifact(kind=kind, messages=messages, stage_manager=stage_manager)
                progress.next_stage()

            # Write to file
            file_path.write_text(content + "\n", encoding="utf-8")

            print_markdown(f"\n**✓ Written to:** `{file_path}` ({len(content)} characters)\n")
            continue

        # Check for confirm command
        if user_text.strip().lower() in {"confirm", "confirmed", "yes"}:
            _handle_confirmation(stage_manager)
            if stage_manager.can_advance():
                new_stage = stage_manager.advance()
                print_stage_header(stage_manager)
                print_markdown(f"\n✅ Advancing to **{new_stage.upper()}** stage!\n")
            save_session(SESSION_PATH, messages, stage_manager.state)
            continue

        # If the prompt contains URLs, fetch and summarize them as additional context.
        urls = extract_urls(user_text)
        if urls:
            for url in urls[:3]:
                try:
                    console.print(f"\n📥 Fetching {url}...")
                    with status(f"Downloading and analyzing {url}..."):
                        page = fetch_url(url)

                        text = page.text
                        if page.content_type and "pdf" in page.content_type.lower():
                            text = fetch_pdf_text(url)

                        summary = summarize(text)

                    console.print(f"  ✓ Fetched and summarized ({len(summary)} chars)\n")

                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Reference material fetched from URL:\n"
                                f"- URL: {url}\n\n"
                                "Summary:\n"
                                f"{summary}"
                            ),
                        }
                    )
                except Exception as e:
                    console.print(f"  ✗ Failed: {e}\n")

        # Add stage context to user message
        user_content = user_text
        stage_context = stage_manager.get_stage_context()
        if stage_context:
            user_content = f"{stage_context}\n\nUser input: {user_text}"

        messages.append({"role": "user", "content": user_content})

        try:
            # Show progress to user
            with ProgressSpinner([
                f"🔗 Connecting to API (Stage: {stage_manager.current_stage.value})...",
                "📤 Sending your request...",
                f"🧠 AI is analyzing... (this may take 10-30s for reasoning models)",
                "📝 Processing response...",
            ]) as progress:
                progress.next_stage()  # Move to "Sending request"
                assistant_text = chat(messages, stage_manager=stage_manager)
                progress.next_stage()  # Move to "Processing response"
        except Exception as e:
            _handle_llm_error(e, messages, stage_manager)
            continue

        print_markdown(assistant_text)
        messages.append({"role": "assistant", "content": assistant_text})

        # Process @CHOICE blocks; stage advancement is handled inside the function.
        # Loop so that any @CHOICE in a followup is also presented automatically.
        current_text = assistant_text
        had_choices = False   # True once we've processed at least one @CHOICE this round
        nudge_sent = False    # Limit auto-nudge to one attempt per response chain
        while True:
            choice_interactions = _process_assistant_response(current_text, stage_manager)
            if not choice_interactions:
                # If we already processed choices but AI forgot to include @CHOICE:confirm,
                # nudge it once to present the stage completion confirmation.
                if had_choices and stage_manager.needs_confirmation() and not nudge_sent:
                    nudge_sent = True
                    messages.append({
                        "role": "user",
                        "content": "(Please present the stage completion @CHOICE:confirm as required by the workflow.)",
                    })
                    with ProgressSpinner([
                        "🔗 Connecting to API...",
                        "📤 Requesting stage confirmation...",
                        "🧠 AI is preparing confirmation...",
                        "📝 Formatting response...",
                    ]) as progress:
                        progress.next_stage()
                        followup = chat(messages, stage_manager=stage_manager)
                        progress.next_stage()
                    console.print()
                    print_markdown(followup)
                    console.print()
                    messages.append({"role": "assistant", "content": followup})
                    current_text = followup
                    continue
                break

            had_choices = True
            nudge_sent = False  # Reset on each successful choice round

            # If stage just advanced to COMPLETE, auto-export and stop the REPL
            if stage_manager.current_stage == Stage.COMPLETE:
                save_session(SESSION_PATH, messages, stage_manager.state)
                _auto_export(messages, stage_manager)
                return

            for prompt, user_selection in choice_interactions:
                messages.append({"role": "user", "content": format_choices_for_ai(prompt, user_selection)})

            with ProgressSpinner([
                "🔗 Connecting to API...",
                "📤 Sending selection...",
                "🧠 AI is processing your choice...",
                "📝 Formatting response...",
            ]) as progress:
                progress.next_stage()
                followup = chat(messages, stage_manager=stage_manager)
                progress.next_stage()

            console.print()
            print_markdown(followup)
            console.print()
            messages.append({"role": "assistant", "content": followup})

            # Present choices from the followup too, if any
            current_text = followup

        save_session(SESSION_PATH, messages, stage_manager.state)


def _handle_llm_error(e: Exception, messages: list[dict], stage_manager: StageManager) -> None:
    """Print a friendly, targeted error message based on the exception type."""
    from eopm.config import GLOBAL_ENV_PATH

    if isinstance(e, EopmLLMError):
        console.print(f"\n[bold red]✗ {e}[/bold red]")
        if e.hint:
            console.print(f"\n[yellow]→ {e.hint}[/yellow]")
    else:
        console.print(f"\n[bold red]✗ Unexpected error: {e}[/bold red]")
        console.print(f"[dim]  {type(e).__name__}[/dim]")

    console.print(
        f"\n[dim]Config locations checked:"
        f"\n  local:  .env"
        f"\n  global: {GLOBAL_ENV_PATH}[/dim]"
    )
    save_session(SESSION_PATH, messages, stage_manager.state)


def _auto_export(messages: list[dict], stage_manager: StageManager) -> None:
    """Prompt user for export directory and write PRD.md + TECH_SPEC.md."""
    print_markdown("\n✅ **All stages complete!** Ready to export artifacts.\n")

    try:
        export_dir_str = input("Export directory (default: ./artifacts): ").strip()
    except (EOFError, KeyboardInterrupt):
        export_dir_str = ""

    export_dir = Path(export_dir_str) if export_dir_str else Path("artifacts")
    export_dir.mkdir(parents=True, exist_ok=True)

    with ProgressSpinner([
        "🔗 Connecting to API for PRD generation...",
        "📤 Preparing request...",
        "🧠 AI is writing PRD (this may take 20-40s)...",
        "📝 Finalizing PRD document...",
    ]) as progress:
        progress.next_stage()
        prd_md = generate_artifact(kind="prd", messages=messages, stage_manager=stage_manager)
        progress.next_stage()

    print_markdown("**✓ PRD generated!**\n")
    console.print("  Now generating Tech Spec...\n")

    with ProgressSpinner([
        "🔗 Connecting to API for Tech Spec...",
        "📤 Preparing request...",
        "🧠 AI is writing technical specifications...",
        "📝 Finalizing Tech Spec document...",
    ]) as progress:
        progress.next_stage()
        tech_md = generate_artifact(kind="techspec", messages=messages, stage_manager=stage_manager)
        progress.next_stage()

    (export_dir / "PRD.md").write_text(prd_md + "\n", encoding="utf-8")
    (export_dir / "TECH_SPEC.md").write_text(tech_md + "\n", encoding="utf-8")

    print_markdown(
        "**✓ Exported artifacts:**\n"
        f"- `{export_dir / 'PRD.md'}`\n"
        f"- `{export_dir / 'TECH_SPEC.md'}`\n"
    )


def _handle_confirmation(stage_manager: StageManager) -> None:
    """Handle user confirmation for current stage (triggered by explicit text input)."""
    stage = stage_manager.current_stage

    if stage == Stage.DISCOVERY:
        if not stage_manager.state.personas_confirmed:
            stage_manager.state.personas_confirmed = True
            print_markdown("✅ User personas confirmed!")
        elif not stage_manager.state.competitors_confirmed:
            stage_manager.state.competitors_confirmed = True
            print_markdown("✅ Competitor analysis confirmed!")

    elif stage == Stage.DEFINITION:
        if not stage_manager.state.mvp_confirmed:
            stage_manager.state.mvp_confirmed = True
            print_markdown("✅ MVP scope confirmed!")

    elif stage == Stage.IDEATION:
        if not stage_manager.state.tech_confirmed:
            stage_manager.state.tech_confirmed = True
            print_markdown("✅ Technical approach confirmed!")


def _confirm_current_stage(stage_manager: StageManager) -> None:
    """Set all confirmation flags for the current stage (called when user selects 'proceed').

    This marks the stage as fully confirmed so can_advance() returns True.
    """
    stage = stage_manager.current_stage

    if stage == Stage.DISCOVERY:
        stage_manager.state.personas_confirmed = True
        stage_manager.state.competitors_confirmed = True
    elif stage == Stage.DEFINITION:
        stage_manager.state.mvp_confirmed = True
    elif stage == Stage.IDEATION:
        stage_manager.state.tech_confirmed = True


def _process_assistant_response(text: str, stage_manager: StageManager) -> list[tuple[ChoicePrompt, str]]:
    """Present any structured @CHOICE blocks in the AI response, collect user selections.

    When a CONFIRM-type choice has its first option selected (the "proceed" option),
    this automatically confirms the current stage and advances to the next one.

    Returns:
        List of (prompt, user_selection) tuples to be sent back to the AI.
    """
    choice_interactions = []

    for prompt in parse_ai_choices(text):
        user_selection = present_choices(prompt)

        if not user_selection:
            continue

        choice_interactions.append((prompt, user_selection))

        # When the user selects the first option of a CONFIRM choice, treat it as
        # "yes, proceed": confirm the current stage and advance the workflow.
        if prompt.prompt_type == ChoiceType.CONFIRM and user_selection.startswith("1."):
            _confirm_current_stage(stage_manager)
            if stage_manager.can_advance():
                stage_manager.advance()
                print_stage_header(stage_manager)

    return choice_interactions


if __name__ == "__main__":
    main()
