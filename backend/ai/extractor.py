from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field

from ai.client import get_client, get_model_name

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "extractor_v1.txt"


class ExtractionResult(BaseModel):
    extracted_attributes: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def extract_attributes(free_text: str) -> Dict[str, Any]:
    client = get_client()
    prompt = _load_prompt()

    response = client.models.generate_content(
        model=get_model_name(),
        contents="Extract structured facts from this text:\n" + json.dumps({"free_text": free_text}, indent=2, ensure_ascii=False),
        config={
            "system_instruction": prompt,
            "response_mime_type": "application/json",
            "response_schema": ExtractionResult,
            "max_output_tokens": 1000,
            "temperature": 0.0,
        },
    )

    return response.parsed.extracted_attributes