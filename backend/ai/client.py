# backend/ai/client.py
from __future__ import annotations

import os
from functools import lru_cache
from google import genai

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    # The SDK will also auto-read GEMINI_API_KEY / GOOGLE_API_KEY if set.
    return genai.Client()


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)