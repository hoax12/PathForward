from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from ai.client import get_client, get_model_name
from schemas import ActionStep, ClassifiedIntent, ProgramMatch

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "explainer_v1.txt"


class ActionPlanOutput(BaseModel):
    steps: List[ActionStep] = Field(default_factory=list)


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_action_plan(intent: ClassifiedIntent, top_matches: List[ProgramMatch]) -> List[ActionStep]:
    client = get_client()
    prompt = _load_prompt()

    allowed_programs = [
        {
            "program_id": m.program_id,
            "name": m.name,
            "org_name": m.org_name,
            "program_type": m.program_type,
            "speed_to_fund": m.speed_to_fund,
            "documents_needed": m.documents_needed,
            "application_url": m.application_url,
            "max_amount": m.max_amount,
            "eligibility_score": m.eligibility_score,
            "eligibility_criteria_met": m.eligibility_criteria_met,
            "eligibility_criteria_missing": m.eligibility_criteria_missing,
        }
        for m in top_matches
    ]

    response = client.models.generate_content(
        model=get_model_name(),
        contents=json.dumps(
            {
                "classified_intent": intent.model_dump(),
                "top_matches": allowed_programs,
            },
            indent=2,
            ensure_ascii=False,
        ),
        config={
            "system_instruction": prompt,
            "response_mime_type": "application/json",
            "response_schema": ActionPlanOutput,
            "max_output_tokens": 1000,
            "temperature": 0.0,
        },
    )

    return response.parsed.steps