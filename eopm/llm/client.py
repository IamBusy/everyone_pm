from __future__ import annotations

import os

import litellm

from eopm.config import get_anthropic_api_key
from eopm.llm.prompts import SYSTEM_PROMPT, PRD_PROMPT, TECH_SPEC_PROMPT


class EopmLLMError(RuntimeError):
    """Clean, user-facing LLM error with an actionable hint."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint


def generate_artifact(
    *,
    kind: str,
    messages: list[dict],
    stage_manager=None,
    max_tokens: int = 8000,
) -> str:
    """Generate a markdown artifact (e.g., PRD / Tech Spec) from the current session."""

    model = os.getenv("EOPM_MODEL", "anthropic/claude-3-5-sonnet-latest")
    _ensure_provider_env(model)

    # For reasoning models, increase max_tokens significantly
    if any(x in model.lower() for x in ["o1", "gpt-5", "reasoning"]):
        max_tokens = 40000

    if kind.lower() == "prd":
        instruction = PRD_PROMPT
        # Add workflow state context if available
        if stage_manager and stage_manager.state:
            state = stage_manager.state
            context = "\n\n---\n\n**Accumulated Workflow Context:**\n\n"

            if state.user_personas:
                context += "### Validated User Personas\n"
                for p in state.user_personas:
                    context += p.to_markdown() + "\n\n"

            if state.competitors:
                context += "### Competitor Analysis\n"
                for c in state.competitors:
                    context += c.to_markdown() + "\n\n"

            if state.product_vision_statement:
                context += f"### Product Vision\n{state.product_vision_statement}\n\n"

            if state.mvp_features:
                context += "### MVP Features\n"
                for f in state.mvp_features:
                    context += f.to_markdown()
                context += "\n"

            if state.user_journey_map:
                context += f"### User Journey Map\n{state.user_journey_map}\n\n"

            instruction = context + "\n\n" + instruction

    elif kind.lower() in {"techspec", "tech_spec", "tech-spec", "spec"}:
        instruction = TECH_SPEC_PROMPT
        # Add workflow state context if available
        if stage_manager and stage_manager.state:
            state = stage_manager.state
            context = "\n\n---\n\n**Accumulated Workflow Context:**\n\n"

            if state.product_vision_statement:
                context += f"### Product Vision\n{state.product_vision_statement}\n\n"

            if state.mvp_features:
                context += "### Confirmed MVP Features\n"
                p0_features = [f for f in state.mvp_features if f.priority == "P0"]
                p1_features = [f for f in state.mvp_features if f.priority == "P1"]
                for f in p0_features + p1_features:
                    context += f.to_markdown()
                context += "\n"

            if state.tech_recommendation:
                context += f"### Technical Approach\n{state.tech_recommendation}\n\n"

            if state.tech_options:
                context += "### Technical Options Considered\n"
                for i, opt in enumerate(state.tech_options, 1):
                    context += f"{i}. {opt}\n"
                context += "\n"

            instruction = context + "\n\n" + instruction
    else:
        raise ValueError(f"Unknown artifact kind: {kind}")

    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + "\n\n"
                + "When asked to generate artifacts, output ONLY the artifact in Markdown (no preamble).",
            },
            *messages,
            {"role": "user", "content": instruction},
        ],
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    if isinstance(content, str):
        return content.strip()
    if content is None:
        raise RuntimeError("LLM returned empty content")
    try:
        return "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        ).strip()
    except Exception:
        return str(content)


def summarize(text: str, *, max_chars: int = 8000) -> str:
    """Summarize arbitrary reference text into a compact note.

    MVP: implemented via the same chat/completion stack to keep dependencies minimal.
    """

    model = os.getenv("EOPM_MODEL", "anthropic/claude-3-5-sonnet-latest")
    _ensure_provider_env(model)

    clipped = text if len(text) <= max_chars else (text[:max_chars] + "\n\n[...truncated]")

    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes web/PDF content for downstream reasoning. \
Return a concise Markdown bullet summary (max ~200 lines), focusing on factual content and key points.",
            },
            {
                "role": "user",
                "content": "Summarize the following content for use as context in a product/tech spec conversation:\n\n"
                + clipped,
            },
        ],
        max_tokens=800,
    )

    content = response.choices[0].message.content
    if isinstance(content, str):
        return content.strip()
    if content is None:
        raise RuntimeError("LLM returned empty content")
    try:
        return "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        ).strip()
    except Exception:
        return str(content)


def _ensure_provider_env(model: str) -> None:
    # For Anthropic models, fail early with a clear message.
    if model.startswith("anthropic/"):
        api_key = get_anthropic_api_key()
        os.environ.setdefault("ANTHROPIC_API_KEY", api_key)
        return

    # OpenAI-compatible gateways / OpenAI models.
    if model.startswith("openai/"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing OPENAI_API_KEY for openai/* models. Add it to your environment or .env."
            )
        # LiteLLM uses OPENAI_API_KEY, keep it set in the process env.
        os.environ.setdefault("OPENAI_API_KEY", api_key)
        return

    # Azure models can be configured via env vars; we don't hard-fail here because
    # some environments use nonstandard gateways and may set custom variables.
    if model.startswith("azure/"):
        return


def chat(messages: list[dict], *, stage_manager=None, max_tokens: int = 4000) -> str:
    model = os.getenv("EOPM_MODEL", "anthropic/claude-3-5-sonnet-latest")
    _ensure_provider_env(model)

    kwargs: dict = {}

    # For reasoning models (o1 series, gpt-5, etc.), we need much higher max_tokens
    # because they use reasoning_tokens which count against the limit
    # These models reserve tokens for "reasoning" before generating actual output
    if any(x in model.lower() for x in ["o1", "gpt-5", "reasoning"]):
        max_tokens = 20000  # Reasoning models need much higher limits
        # Also set max_completion_tokens for newer OpenAI API
        kwargs["max_completion_tokens"] = 8000

    # Azure + custom gateways: some environments expose an OpenAI-compatible
    # endpoint but require AzureOpenAI-style parameters and headers.
    if model.startswith("azure/"):
        deployment = os.getenv("AZURE_DEPLOYMENT_NAME") or os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        )
        if deployment:
            kwargs["azure_deployment"] = deployment

        # If you're using a gateway endpoint that still expects AzureOpenAI client
        # semantics, allow passing these through explicitly.
        azure_endpoint = os.getenv("AZURE_ENDPOINT")
        if azure_endpoint:
            kwargs["azure_endpoint"] = azure_endpoint

        # For custom gateways, use api_base instead
        api_base = os.getenv("AZURE_API_BASE") or os.getenv("AZURE_OPENAI_API_BASE")
        if api_base:
            kwargs["api_base"] = api_base

        api_version = os.getenv("AZURE_API_VERSION")
        if api_version:
            kwargs["api_version"] = api_version

        default_headers_raw = os.getenv("EOPM_DEFAULT_HEADERS")
        if default_headers_raw:
            import json

            kwargs["default_headers"] = json.loads(default_headers_raw)

    if model.startswith("openai/"):
        api_base = os.getenv("OPENAI_API_BASE")
        if api_base:
            kwargs["api_base"] = api_base

        default_headers_raw = os.getenv("EOPM_DEFAULT_HEADERS")
        if default_headers_raw:
            import json

            kwargs["default_headers"] = json.loads(default_headers_raw)

    # Build system prompt based on current stage
    system_prompt = SYSTEM_PROMPT
    if stage_manager:
        from eopm.llm.prompts import get_system_prompt

        system_prompt = get_system_prompt(stage_manager.current_stage.value)

    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
            max_tokens=max_tokens,
            **kwargs,
        )
    except litellm.AuthenticationError:
        raise EopmLLMError(
            "API key rejected (401 Unauthorized)",
            hint=(
                f"Your API key for model '{model}' is invalid or missing.\n"
                f"  • Check ~/.eopm/.env or local .env\n"
                f"  • Make sure ANTHROPIC_API_KEY / OPENAI_API_KEY is set correctly"
            ),
        )
    except litellm.RateLimitError:
        raise EopmLLMError(
            "Rate limit hit (429 Too Many Requests)",
            hint="Wait a moment and try again, or switch to a model with a higher quota.",
        )
    except litellm.NotFoundError:
        raise EopmLLMError(
            f"Model not found: {model}",
            hint=(
                f"Check EOPM_MODEL in your config.\n"
                f"  • Anthropic example: anthropic/claude-3-5-sonnet-latest\n"
                f"  • OpenAI example:    openai/gpt-4o\n"
                f"  • Azure example:     azure/gpt-4o"
            ),
        )
    except litellm.ContextWindowExceededError:
        raise EopmLLMError(
            "Conversation too long for this model's context window",
            hint="Start a fresh session with /fresh, or use a model with a larger context window.",
        )
    except litellm.BadRequestError as e:
        raise EopmLLMError(
            "Bad request — the model rejected the input",
            hint=f"Details: {e}",
        )
    except Exception as e:
        # Network issues, unexpected errors — show a short message, not a traceback
        kind = type(e).__name__
        raise EopmLLMError(
            f"Unexpected error ({kind})",
            hint=(
                f"{e}\n\n"
                f"  • Model: {model}\n"
                f"  • API base: {kwargs.get('api_base', 'default')}\n"
                f"  • If this persists, run with LITELLM_LOG=DEBUG for details"
            ),
        )

    # Process the response
    try:
        message = response.choices[0].message
        content = message.content

        # For reasoning models, also check reasoning_content
        reasoning_content = getattr(message, "reasoning_content", None)

        # Combine content and reasoning_content if available
        if reasoning_content and not content:
            content = reasoning_content
        elif reasoning_content and content:
            content = f"{reasoning_content}\n\n{content}"

        # Handle empty content
        if not content:
            # Check finish_reason for more context
            finish_reason = response.choices[0].finish_reason if response.choices else "unknown"
            if finish_reason == "length":
                current_model = os.getenv("EOPM_MODEL", "unknown")
                is_reasoning = any(x in current_model.lower() for x in ["o1", "gpt-5", "reasoning"])
                if is_reasoning:
                    raise RuntimeError(
                        f"LLM response was truncated because the model '{current_model}' uses reasoning tokens "
                        f"that consumed the entire budget (current limit: {max_tokens} tokens). "
                        f"Reasoning models like o1/gpt-5 need much higher limits.\n\n"
                        f"Solution: Add this to your .env file:\n"
                        f"  EOPM_MAX_TOKENS=40000\n\n"
                        f"Or switch to a faster/cheaper non-reasoning model:\n"
                        f"  EOPM_MODEL=anthropic/claude-3-5-sonnet-latest\n"
                        f"  EOPM_MODEL=azure/gpt-4o"
                    )
                else:
                    raise RuntimeError(
                        f"LLM response was truncated due to max_tokens limit (current: {max_tokens}). "
                        f"Set EOPM_MAX_TOKENS=8000 in your .env file."
                    )
            raise RuntimeError("LLM returned empty content - check API configuration and model availability")

        if isinstance(content, str):
            stripped = content.strip()
            if not stripped:
                raise RuntimeError("LLM returned only whitespace content")
            return stripped

        if content is None:
            raise RuntimeError("LLM returned None content")

        # Some providers may return a list of content blocks; best-effort join.
        try:
            result = "\n".join(
                part.get("text", "") if isinstance(part, dict) else str(part) for part in content
            ).strip()
            if not result:
                raise RuntimeError("LLM content blocks resulted in empty string after joining")
            return result
        except Exception:
            return str(content)
    except (AttributeError, IndexError) as e:
        raise RuntimeError(f"Failed to extract content from LLM response: {e}") from e
