from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Global config path: ~/.eopm/.env
GLOBAL_ENV_PATH = Path.home() / ".eopm" / ".env"

# Load order (dotenv won't override already-set vars):
#   priority: real env vars > local .env > global ~/.eopm/.env
load_dotenv()                              # local .env (overrides global)
load_dotenv(GLOBAL_ENV_PATH)              # global fallback

EOPM_DIR = Path(".eopm")
SESSION_PATH = EOPM_DIR / "session.json"

VERSION = "0.2.6"

_API_KEY_VARS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "AZURE_API_KEY",
    "AZURE_OPENAI_API_KEY",
]


def check_env_file() -> tuple[bool, str]:
    """Check whether any env source provides required configuration.

    Checks (in order): real env vars, local .env, global ~/.eopm/.env.

    Returns:
        (has_env, message): Tuple of whether env is configured and a status message
    """
    local_env = Path(".env")
    has_local = local_env.exists()
    has_global = GLOBAL_ENV_PATH.exists()

    # API keys are already loaded into os.environ by load_dotenv above
    has_key = any(os.getenv(k) for k in _API_KEY_VARS)

    if has_key:
        if has_global and not has_local:
            return True, f"Environment configured (global config: {GLOBAL_ENV_PATH})"
        return True, "Environment configured"

    if not has_local and not has_global:
        return False, f"No .env file found (local or global at {GLOBAL_ENV_PATH})"

    return False, "Config file exists but no API key found"


def get_anthropic_api_key() -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY. Add it to your environment or a .env file in the repo root."
        )
    return api_key
