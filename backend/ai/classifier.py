from __future__ import annotations

import json
from pathlib import Path

from ai.client import get_client, get_model_name
from schemas import ClassifiedIntent, IntakeProfile

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "classifier_v1.txt"


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
            "response_schema": ClassifiedIntent,
            "temperature": 0.0,
        },
    )

    return response.parsed