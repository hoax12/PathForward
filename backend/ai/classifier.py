from __future__ import annotations

import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field

from ai.client import get_client, get_model_name
from schemas import ClassifiedIntent, IntakeProfile

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "classifier_v1.txt"


class ExtractedFact(BaseModel):
    key: str
    value: str

class GeminiClassifiedIntent(BaseModel):
    primary_intent: str
    urgency_level: Literal["immediate", "this_week", "this_month"]
    extracted_facts: list[ExtractedFact] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def classify_intent(profile: IntakeProfile) -> ClassifiedIntent:
    client = get_client()
    prompt = _load_prompt()

    payload = {
        "location": profile.location.model_dump() if hasattr(profile.location, "model_dump") else profile.location.dict(),
        "income_band": profile.income_band,
        "employment_status": profile.employment_status,
        "business_type": profile.business_type,
        "urgent_needs": profile.urgent_needs,
        "free_text": profile.free_text,
        "monthly_revenue": profile.monthly_revenue,
        "has_paypal_account": profile.has_paypal_account,
        "extracted_attributes": profile.extracted_attributes,
    }

    response = client.models.generate_content(
        model=get_model_name(),
        contents="Classify this intake profile into the strict schema below:\n" + json.dumps(payload, indent=2),
        config={
            "system_instruction": prompt,
            "response_mime_type": "application/json",
            "response_schema": GeminiClassifiedIntent,
            "temperature": 0.0,
        },
    )

    parsed = response.parsed
    return ClassifiedIntent(
        primary_intent=parsed.primary_intent,
        urgency_level=parsed.urgency_level,
        extracted_facts={f.key: f.value for f in (parsed.extracted_facts or [])},
        confidence=parsed.confidence,
    )